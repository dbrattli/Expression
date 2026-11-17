from collections.abc import Awaitable, Callable, Coroutine
from typing import Any

from expression import Result


def bind[TSource, TResult, TError](
    mapper: Callable[[TSource], Awaitable[Result[TResult, TError]]],
) -> Callable[[Result[TSource, TError]], Coroutine[Any, Any, Result[TResult, TError]]]:
    """Apply an asynchronous mapper to Ok, preserving Error without calling it."""

    async def wrapped(result: Result[TSource, TError]) -> Result[TResult, TError]:
        return await result.abind(mapper)

    return wrapped


__all__ = ["bind"]
