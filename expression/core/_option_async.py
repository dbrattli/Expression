"""Private asynchronous functional helpers for Option."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import overload

from .option import Nothing, Option, Some


class _AsyncMap[TSource, TResult]:
    def __init__(self, mapper: Callable[[TSource], Awaitable[TResult]]) -> None:
        self._mapper = mapper

    @overload
    async def __call__(self, source: Some[TSource]) -> Some[TResult]: ...

    @overload
    async def __call__(self, source: Nothing) -> Nothing: ...

    @overload
    async def __call__(self, source: Option[TSource]) -> Option[TResult]: ...

    async def __call__(self, source: Option[TSource]) -> Option[TResult]:
        return await source.amap(self._mapper)


def amap[TSource, TResult](mapper: Callable[[TSource], Awaitable[TResult]]) -> _AsyncMap[TSource, TResult]:
    """Create an async mapping stage for pipe or apipe.

    Await the returned stage's coroutine to map Some, preserving Nothing without
    invoking the callback. Exceptions and cancellation propagate.
    """
    return _AsyncMap(mapper)


class _AsyncBind[TSource, TOption: Some[object] | Nothing]:
    def __init__(self, mapper: Callable[[TSource], Awaitable[TOption]]) -> None:
        self._mapper = mapper

    @overload
    async def __call__(self, source: Some[TSource]) -> TOption: ...

    @overload
    async def __call__(self, source: Nothing) -> Nothing: ...

    @overload
    async def __call__(self, source: Option[TSource]) -> TOption | Nothing: ...

    async def __call__(self, source: Option[TSource]) -> TOption | Nothing:
        return await source.abind(self._mapper)


def abind[TSource, TOption: Some[object] | Nothing](
    mapper: Callable[[TSource], Awaitable[TOption]],
) -> _AsyncBind[TSource, TOption]:
    """Create an async binding stage, preserving Nothing without invoking the callback.

    Await the stage's coroutine to obtain the callback's option directly.
    Exceptions and cancellation propagate.
    """
    return _AsyncBind(mapper)
