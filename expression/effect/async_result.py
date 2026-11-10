"""Typed result computations using ordinary coroutine return values."""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Coroutine
from functools import wraps
from typing import Any, Concatenate, TypeVar

from typing_extensions import ParamSpec

from expression.core.result import Ok, Result

from ._scope import Abort, ResultInvocation, hide_scope_parameter
from .result import ResultScope


_T = TypeVar("_T")
_E = TypeVar("_E")
_P = ParamSpec("_P")


async def async_run_result(body: Callable[[ResultScope[_E]], Awaitable[_T]]) -> Result[_T, _E]:
    """Await a result computation and close its scope on every exit path."""
    invocation = ResultInvocation[_E]()
    scope = ResultScope(invocation)
    try:
        value = await body(scope)
        return invocation.failure if invocation.failure is not None else Ok(value)
    except Abort as signal:
        if signal.owner is not invocation.owner or invocation.failure is None:
            raise
        return invocation.failure
    finally:
        invocation.close()


def async_result(
    body: Callable[Concatenate[ResultScope[_E], _P], Awaitable[_T]],
) -> Callable[_P, Coroutine[Any, Any, Result[_T, _E]]]:
    """Decorate a coroutine, inferring its result and error types from the body."""

    @wraps(body)
    async def run(*args: _P.args, **kwargs: _P.kwargs) -> Result[_T, _E]:
        def invoke(scope: ResultScope[_E]) -> Awaitable[_T]:
            return body(scope, *args, **kwargs)

        return await async_run_result(invoke)

    return hide_scope_parameter(run, body)


def async_try(
    body: Callable[Concatenate[ResultScope[Exception], _P], Awaitable[_T]],
) -> Callable[_P, Coroutine[Any, Any, Result[_T, Exception]]]:
    """Decorate a coroutine with explicit exception errors; raised exceptions propagate."""
    return async_result(body)


__all__ = ["async_result", "async_run_result", "async_try"]
