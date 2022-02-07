import builtins
import itertools
from typing import (
    Any,
    AsyncIterable,
    AsyncIterator,
    Callable,
    Optional,
    TypeVar,
    overload,
)

from expression.core import pipe

TSource = TypeVar("TSource")
TResult = TypeVar("TResult")


class AsyncSeq(AsyncIterable[TSource]):
    def __init__(self, ai: AsyncIterable[TSource]):
        self._ai = ai

    async def map(self, mapper: Callable[[TSource], TResult]) -> AsyncIterable[TResult]:
        return pipe(self, map(mapper))

    @classmethod
    def empty(cls) -> AsyncIterable[Any]:
        return AsyncSeq(empty())

    @overload
    @classmethod
    def range(cls, stop: int) -> AsyncIterable[int]:
        ...

    @overload
    @classmethod
    def range(cls, start: int, stop: int) -> AsyncIterable[int]:
        ...

    @overload
    @classmethod
    def range(cls, start: int, stop: int, step: int) -> AsyncIterable[int]:
        ...

    @classmethod
    def range(cls, *args: Any, **kw: Any) -> AsyncIterable[int]:
        return AsyncSeq(range(*args, **kw))

    def __aiter__(self) -> AsyncIterator[TSource]:
        return self._ai.__aiter__()


def append(
    other: AsyncIterable[TSource],
) -> Callable[[AsyncIterable[TSource]], AsyncIterable[TSource]]:
    async def _append(source: AsyncIterable[TSource]) -> AsyncIterable[TSource]:
        async for value in source:
            yield value
        async for value in other:
            yield value

    return _append


async def empty() -> AsyncIterable[Any]:
    while False:
        yield


async def repeat(value: TSource, times: Optional[int] = None) -> AsyncIterable[TSource]:
    for value in itertools.repeat(value, times):  # type: ignore
        yield value


@overload
def range(stop: int) -> AsyncIterable[int]:
    ...


@overload
def range(start: int, stop: int) -> AsyncIterable[int]:
    ...


@overload
def range(start: int, stop: int, step: int) -> AsyncIterable[int]:
    ...


async def range(*args: int, **kw: int) -> AsyncIterable[int]:
    for value in builtins.range(*args, **kw):
        yield value


def filter(
    predicate: Callable[[TSource], bool]
) -> Callable[[AsyncIterable[TSource]], AsyncIterable[TSource]]:
    async def _filter(source: AsyncIterable[TSource]) -> AsyncIterable[TSource]:
        async for value in source:
            if predicate(value):
                yield value

    return _filter


def map(
    mapper: Callable[[TSource], TResult]
) -> Callable[[AsyncIterable[TSource]], AsyncIterable[TResult]]:
    async def _map(source: AsyncIterable[TSource]) -> AsyncIterable[TResult]:
        async for value in source:
            yield mapper(value)

    return _map


__all__ = [
    "AsyncSeq",
    "range",
    "filter",
    "map",
    "repeat",
]
