"""Async Pipe module

The pipe handles both synchronous and asynchronous functions; if a function
returns a Coroutine, it is awaited before its result is passed to the next function.
"""

from collections.abc import Callable
from typing import Any, TypeVar, overload, Union, Coroutine
import inspect

_A = TypeVar("_A")
_B = TypeVar("_B")
_C = TypeVar("_C")
_D = TypeVar("_D")
_E = TypeVar("_E")
_F = TypeVar("_F")
_G = TypeVar("_G")
_H = TypeVar("_H")
_T = TypeVar("_T")
_J = TypeVar("_J")

_X = TypeVar("_X")
_Y = TypeVar("_Y")

SyncCallable = Callable[[_X], _Y]
AsyncCallable = Callable[[_X], Coroutine[Any, Any, _Y]]
SyncOrAsyncCallable = Union[SyncCallable[_X, _Y], AsyncCallable[_X, _Y]]


@overload
async def async_pipe(value: _A, /) -> _A: ...


@overload
async def async_pipe(
    value: _A,
    fn1: SyncOrAsyncCallable[_A, _B],
    /,
) -> _B: ...


@overload
async def async_pipe(
    value: _A,
    fn1: SyncOrAsyncCallable[_A, _B],
    fn2: SyncOrAsyncCallable[_B, _C],
    /,
) -> _C: ...


@overload
async def async_pipe(
    value: _A,
    fn1: SyncOrAsyncCallable[_A, _B],
    fn2: SyncOrAsyncCallable[_B, _C],
    fn3: SyncOrAsyncCallable[_C, _D],
    /,
) -> _D: ...


@overload
async def async_pipe(
    value: _A,
    fn1: SyncOrAsyncCallable[_A, _B],
    fn2: SyncOrAsyncCallable[_B, _C],
    fn3: SyncOrAsyncCallable[_C, _D],
    fn4: SyncOrAsyncCallable[_D, _E],
    /,
) -> _E: ...


@overload
async def async_pipe(
    value: _A,
    fn1: SyncOrAsyncCallable[_A, _B],
    fn2: SyncOrAsyncCallable[_B, _C],
    fn3: SyncOrAsyncCallable[_C, _D],
    fn4: SyncOrAsyncCallable[_D, _E],
    fn5: SyncOrAsyncCallable[_E, _F],
    /,
) -> _F: ...


@overload
async def async_pipe(
    value: _A,
    fn1: SyncOrAsyncCallable[_A, _B],
    fn2: SyncOrAsyncCallable[_B, _C],
    fn3: SyncOrAsyncCallable[_C, _D],
    fn4: SyncOrAsyncCallable[_D, _E],
    fn5: SyncOrAsyncCallable[_E, _F],
    fn6: SyncOrAsyncCallable[_F, _G],
    /,
) -> _G: ...


@overload
async def async_pipe(
    value: _A,
    fn1: SyncOrAsyncCallable[_A, _B],
    fn2: SyncOrAsyncCallable[_B, _C],
    fn3: SyncOrAsyncCallable[_C, _D],
    fn4: SyncOrAsyncCallable[_D, _E],
    fn5: SyncOrAsyncCallable[_E, _F],
    fn6: SyncOrAsyncCallable[_F, _G],
    fn7: SyncOrAsyncCallable[_G, _H],
    /,
) -> _H: ...


@overload
async def async_pipe(
    value: _A,
    fn1: SyncOrAsyncCallable[_A, _B],
    fn2: SyncOrAsyncCallable[_B, _C],
    fn3: SyncOrAsyncCallable[_C, _D],
    fn4: SyncOrAsyncCallable[_D, _E],
    fn5: SyncOrAsyncCallable[_E, _F],
    fn6: SyncOrAsyncCallable[_F, _G],
    fn7: SyncOrAsyncCallable[_G, _H],
    fn8: SyncOrAsyncCallable[_H, _T],
    /,
) -> _T: ...


@overload
async def async_pipe(
    value: _A,
    fn1: SyncOrAsyncCallable[_A, _B],
    fn2: SyncOrAsyncCallable[_B, _C],
    fn3: SyncOrAsyncCallable[_C, _D],
    fn4: SyncOrAsyncCallable[_D, _E],
    fn5: SyncOrAsyncCallable[_E, _F],
    fn6: SyncOrAsyncCallable[_F, _G],
    fn7: SyncOrAsyncCallable[_G, _H],
    fn8: SyncOrAsyncCallable[_H, _T],
    fn9: SyncOrAsyncCallable[_T, _J],
    /,
) -> _J: ...


async def async_pipe(value: Any, *functions: SyncOrAsyncCallable[Any, Any]) -> Any:
    """Functional async pipe (`|>`).

    Passes the `value` to the first function in `functions`, then the result of that
    to the second function, and so on, recursively. If any function in the sequence
    returns a coroutine, it is `await`ed before its result is passed to the next function.

    Args:
        value: The initial value for the pipeline.
        *functions: A sequence of functions to apply. Each function should
                    accept the output of the previous function (or the initial
                    `value` for the first function) as its input. Functions can be
                    synchronous or asynchronous.

    Returns:
        The result of passing the value through all functions in the sequence.
    """
    if inspect.iscoroutine(value):
        value = await value
    if not functions:
        return value
    next_func, *remaining_functions = functions
    result_or_awaitable = next_func(value)
    return await async_pipe(result_or_awaitable, *remaining_functions)


__all__ = ["async_pipe"]
