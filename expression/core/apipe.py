"""Asynchronous pipe composition.

The pipe handles both synchronous and asynchronous functions; if a function
returns a Coroutine, it is awaited before its result is passed to the next function.
"""

import inspect
from collections.abc import Callable, Coroutine
from typing import Any, overload


type SyncCallable[X, Y] = Callable[[X], Y]
type AsyncCallable[X, Y] = Callable[[X], Coroutine[Any, Any, Y]]
type SyncOrAsyncCallable[X, Y] = SyncCallable[X, Y] | AsyncCallable[X, Y]


@overload
async def apipe[A](value: Coroutine[Any, Any, A] | A, /) -> A: ...


@overload
async def apipe[A, B](
    value: Coroutine[Any, Any, A] | A,
    fn1: SyncOrAsyncCallable[A, B],
    /,
) -> B: ...


@overload
async def apipe[A, B, C](
    value: Coroutine[Any, Any, A] | A,
    fn1: SyncOrAsyncCallable[A, B],
    fn2: SyncOrAsyncCallable[B, C],
    /,
) -> C: ...


@overload
async def apipe[A, B, C, D](
    value: Coroutine[Any, Any, A] | A,
    fn1: SyncOrAsyncCallable[A, B],
    fn2: SyncOrAsyncCallable[B, C],
    fn3: SyncOrAsyncCallable[C, D],
    /,
) -> D: ...


@overload
async def apipe[A, B, C, D, E](
    value: Coroutine[Any, Any, A] | A,
    fn1: SyncOrAsyncCallable[A, B],
    fn2: SyncOrAsyncCallable[B, C],
    fn3: SyncOrAsyncCallable[C, D],
    fn4: SyncOrAsyncCallable[D, E],
    /,
) -> E: ...


@overload
async def apipe[A, B, C, D, E, F](
    value: Coroutine[Any, Any, A] | A,
    fn1: SyncOrAsyncCallable[A, B],
    fn2: SyncOrAsyncCallable[B, C],
    fn3: SyncOrAsyncCallable[C, D],
    fn4: SyncOrAsyncCallable[D, E],
    fn5: SyncOrAsyncCallable[E, F],
    /,
) -> F: ...


@overload
async def apipe[A, B, C, D, E, F, G](
    value: Coroutine[Any, Any, A] | A,
    fn1: SyncOrAsyncCallable[A, B],
    fn2: SyncOrAsyncCallable[B, C],
    fn3: SyncOrAsyncCallable[C, D],
    fn4: SyncOrAsyncCallable[D, E],
    fn5: SyncOrAsyncCallable[E, F],
    fn6: SyncOrAsyncCallable[F, G],
    /,
) -> G: ...


@overload
async def apipe[A, B, C, D, E, F, G, H](
    value: Coroutine[Any, Any, A] | A,
    fn1: SyncOrAsyncCallable[A, B],
    fn2: SyncOrAsyncCallable[B, C],
    fn3: SyncOrAsyncCallable[C, D],
    fn4: SyncOrAsyncCallable[D, E],
    fn5: SyncOrAsyncCallable[E, F],
    fn6: SyncOrAsyncCallable[F, G],
    fn7: SyncOrAsyncCallable[G, H],
    /,
) -> H: ...


@overload
async def apipe[A, B, C, D, E, F, G, H, T](
    value: Coroutine[Any, Any, A] | A,
    fn1: SyncOrAsyncCallable[A, B],
    fn2: SyncOrAsyncCallable[B, C],
    fn3: SyncOrAsyncCallable[C, D],
    fn4: SyncOrAsyncCallable[D, E],
    fn5: SyncOrAsyncCallable[E, F],
    fn6: SyncOrAsyncCallable[F, G],
    fn7: SyncOrAsyncCallable[G, H],
    fn8: SyncOrAsyncCallable[H, T],
    /,
) -> T: ...


@overload
async def apipe[A, B, C, D, E, F, G, H, T, J](
    value: Coroutine[Any, Any, A] | A,
    fn1: SyncOrAsyncCallable[A, B],
    fn2: SyncOrAsyncCallable[B, C],
    fn3: SyncOrAsyncCallable[C, D],
    fn4: SyncOrAsyncCallable[D, E],
    fn5: SyncOrAsyncCallable[E, F],
    fn6: SyncOrAsyncCallable[F, G],
    fn7: SyncOrAsyncCallable[G, H],
    fn8: SyncOrAsyncCallable[H, T],
    fn9: SyncOrAsyncCallable[T, J],
    /,
) -> J: ...


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
