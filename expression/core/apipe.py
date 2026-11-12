"""Asynchronous pipe composition.

The pipe handles both synchronous and asynchronous functions; if a function
returns a Coroutine, it is awaited before its result is passed to the next function.
"""

import inspect
from collections.abc import Callable, Coroutine
from typing import Any, TypeVar, overload


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
SyncOrAsyncCallable = SyncCallable[_X, _Y] | AsyncCallable[_X, _Y]


@overload
async def apipe(value: Coroutine[Any, Any, _A] | _A, /) -> _A: ...


@overload
async def apipe(
    value: Coroutine[Any, Any, _A] | _A,
    fn1: SyncOrAsyncCallable[_A, _B],
    /,
) -> _B: ...


@overload
async def apipe(
    value: Coroutine[Any, Any, _A] | _A,
    fn1: SyncOrAsyncCallable[_A, _B],
    fn2: SyncOrAsyncCallable[_B, _C],
    /,
) -> _C: ...


@overload
async def apipe(
    value: Coroutine[Any, Any, _A] | _A,
    fn1: SyncOrAsyncCallable[_A, _B],
    fn2: SyncOrAsyncCallable[_B, _C],
    fn3: SyncOrAsyncCallable[_C, _D],
    /,
) -> _D: ...


@overload
async def apipe(
    value: Coroutine[Any, Any, _A] | _A,
    fn1: SyncOrAsyncCallable[_A, _B],
    fn2: SyncOrAsyncCallable[_B, _C],
    fn3: SyncOrAsyncCallable[_C, _D],
    fn4: SyncOrAsyncCallable[_D, _E],
    /,
) -> _E: ...


@overload
async def apipe(
    value: Coroutine[Any, Any, _A] | _A,
    fn1: SyncOrAsyncCallable[_A, _B],
    fn2: SyncOrAsyncCallable[_B, _C],
    fn3: SyncOrAsyncCallable[_C, _D],
    fn4: SyncOrAsyncCallable[_D, _E],
    fn5: SyncOrAsyncCallable[_E, _F],
    /,
) -> _F: ...


@overload
async def apipe(
    value: Coroutine[Any, Any, _A] | _A,
    fn1: SyncOrAsyncCallable[_A, _B],
    fn2: SyncOrAsyncCallable[_B, _C],
    fn3: SyncOrAsyncCallable[_C, _D],
    fn4: SyncOrAsyncCallable[_D, _E],
    fn5: SyncOrAsyncCallable[_E, _F],
    fn6: SyncOrAsyncCallable[_F, _G],
    /,
) -> _G: ...


@overload
async def apipe(
    value: Coroutine[Any, Any, _A] | _A,
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
async def apipe(
    value: Coroutine[Any, Any, _A] | _A,
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
async def apipe(
    value: Coroutine[Any, Any, _A] | _A,
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


async def apipe(value: Any, *functions: SyncOrAsyncCallable[Any, Any]) -> Any:
    """Apply mixed synchronous and asynchronous stages sequentially.

    Await native coroutines in the initial value and each stage's output once.
    Other values, including Option, Result, tasks, and futures, pass through
    unchanged. Wrap other awaitables in an async function to resolve them.
    Execution starts when the returned coroutine is awaited. Exceptions and
    cancellation propagate without running subsequent stages.
    """
    if inspect.iscoroutine(value):
        value = await value
    for function in functions:
        value = function(value)
        if inspect.iscoroutine(value):
            value = await value
    return value


__all__ = ["apipe"]
