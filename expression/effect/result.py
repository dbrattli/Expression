"""Typed scopes for synchronous computations that can fail."""

from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import Concatenate, Generic, Never, TypeVar, final, overload

from typing_extensions import ParamSpec

from expression.core.result import Error, Ok, Result

from ._scope import Abort, ResultInvocation, hide_scope_parameter


_A = TypeVar("_A")
_T = TypeVar("_T")
_E = TypeVar("_E")
_P = ParamSpec("_P")


@final
class ResultScope(Generic[_E]):
    """Bind results sharing one error type inside a computation.

    Scopes are supplied by :func:`result` and :func:`run_result`. Each bind has
    its own payload type. Errors end the computation, while ordinary exceptions
    propagate. A scope cannot escape its invocation or be used in another task.
    """

    def __init__(self, invocation: ResultInvocation[_E]) -> None:
        self._invocation = invocation

    @overload
    def bind(self, value: Error[_E]) -> Never: ...

    @overload
    def bind(self, value: Result[_A, _E]) -> _A: ...

    def bind(self, value: Result[_A, _E]) -> _A:
        self._invocation.check()
        if self._invocation.failure is not None:
            raise Abort(self._invocation.owner)
        match value:
            case Ok(ok):
                return ok
            case Error() as failure:
                self._invocation.failure = failure
                raise Abort(self._invocation.owner)
            case _:
                raise TypeError("ResultScope.bind expects Ok or Error")


def run_result(body: Callable[[ResultScope[_E]], _T]) -> Result[_T, _E]:
    """Run a result computation, including a bound method or callback."""
    invocation = ResultInvocation[_E]()
    scope = ResultScope(invocation)
    try:
        value = body(scope)
        return invocation.failure if invocation.failure is not None else Ok(value)
    except Abort as signal:
        if signal.owner is not invocation.owner or invocation.failure is None:
            raise
        return invocation.failure
    finally:
        invocation.close()


def result(body: Callable[Concatenate[ResultScope[_E], _P], _T]) -> Callable[_P, Result[_T, _E]]:
    """Decorate a scoped function, inferring its final result and error types."""

    @wraps(body)
    def run(*args: _P.args, **kwargs: _P.kwargs) -> Result[_T, _E]:
        def invoke(scope: ResultScope[_E]) -> _T:
            return body(scope, *args, **kwargs)

        return run_result(invoke)

    return hide_scope_parameter(run, body)


def try_(body: Callable[Concatenate[ResultScope[Exception], _P], _T]) -> Callable[_P, Result[_T, Exception]]:
    """Decorate a result computation whose explicit errors are exceptions.

    Unexpected exceptions raised by the body still propagate.
    """
    return result(body)


__all__ = ["ResultScope", "result", "run_result", "try_"]
