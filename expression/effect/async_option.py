"""Typed optional computations using ordinary coroutine return values."""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Coroutine
from functools import wraps
from typing import Any, Concatenate, TypeVar

from typing_extensions import ParamSpec

from expression.core.option import NOTHING, Option, Some

from ._scope import Abort, OptionInvocation, hide_scope_parameter
from .option import OptionScope


_T = TypeVar("_T")
_P = ParamSpec("_P")


async def async_run_option(body: Callable[[OptionScope], Awaitable[_T]]) -> Option[_T]:
    """Await an optional computation and close its scope on every exit path."""
    invocation = OptionInvocation()
    scope = OptionScope(invocation)
    try:
        value = await body(scope)
        return NOTHING if invocation.failed else Some(value)
    except Abort as signal:
        if signal.owner is not invocation.owner:
            raise
        return NOTHING
    finally:
        invocation.close()


def async_option(
    body: Callable[Concatenate[OptionScope, _P], Awaitable[_T]],
) -> Callable[_P, Coroutine[Any, Any, Option[_T]]]:
    """Decorate a coroutine that binds optional values through its scope."""

    @wraps(body)
    async def run(*args: _P.args, **kwargs: _P.kwargs) -> Option[_T]:
        return await async_run_option(lambda scope: body(scope, *args, **kwargs))

    return hide_scope_parameter(run, body)


__all__ = ["async_option", "async_run_option"]
