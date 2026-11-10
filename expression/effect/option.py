"""Typed scopes for synchronous optional computations."""

from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import Concatenate, Never, TypeVar, final, overload

from typing_extensions import ParamSpec

from expression.core.option import Nothing, Option, Some

from ._scope import Abort, OptionInvocation, hide_scope_parameter


_A = TypeVar("_A")
_T = TypeVar("_T")
_P = ParamSpec("_P")


@final
class OptionScope:
    """Bind optional values inside one computation.

    Scopes are supplied by :func:`option` and :func:`run_option`. Each call to
    ``bind`` preserves its payload type; ``Nothing()`` ends the computation.
    A scope cannot be used after its computation ends or from another task.
    """

    def __init__(self, invocation: OptionInvocation) -> None:
        self._invocation = invocation

    @overload
    def bind(self, value: Nothing) -> Never: ...

    @overload
    def bind(self, value: Option[_A]) -> _A: ...

    def bind(self, value: Option[_A]) -> _A:
        self._invocation.check()
        if self._invocation.failed:
            raise Abort(self._invocation.owner)
        match value:
            case Some(some):
                return some
            case Nothing():
                self._invocation.failed = True
                raise Abort(self._invocation.owner)
            case _:
                raise TypeError("OptionScope.bind expects Some or Nothing")


def run_option(body: Callable[[OptionScope], _T]) -> Option[_T]:
    """Run an optional computation, including a bound method or callback."""
    invocation = OptionInvocation()
    scope = OptionScope(invocation)
    try:
        value = body(scope)
        return Nothing() if invocation.failed else Some(value)
    except Abort as signal:
        if signal.owner is not invocation.owner:
            raise
        return Nothing()
    finally:
        invocation.close()


def option(body: Callable[Concatenate[OptionScope, _P], _T]) -> Callable[_P, Option[_T]]:
    """Decorate a scoped function, inferring its final optional result type."""

    @wraps(body)
    def run(*args: _P.args, **kwargs: _P.kwargs) -> Option[_T]:
        return run_option(lambda scope: body(scope, *args, **kwargs))

    return hide_scope_parameter(run, body)


__all__ = ["OptionScope", "option", "run_option"]
