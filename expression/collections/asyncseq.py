import builtins
import itertools
from typing import Any, AsyncIterable, Callable, Optional, TypeVar, overload

TSource = TypeVar("TSource")
TResult = TypeVar("TResult")


class AsyncSeq(AsyncIterable[TSource]):
    def __init__(self, ai: AsyncIterable[TSource]):
        self._ai = ai


async def repeat(value: TSource, times: Optional[int] = None) -> AsyncIterable[TSource]:
    for value in itertools.repeat(value, times):  # type: ignore
        yield value


@overload
async def range(stop: int) -> AsyncIterable[int]:
    ...


@overload
async def range(start: int, stop: int, step: Optional[int]) -> AsyncIterable[int]:
    ...


async def range(*args: Any) -> AsyncIterable[int]:
    for value in builtins.range(*args):
        yield value


async def filter(predicate: Callable[[TSource], bool], source: AsyncIterable[TSource]) -> AsyncIterable[TSource]:
    async for value in source:
        if predicate(value):
            yield value


async def map(mapper: Callable[[TSource], TResult], source: AsyncIterable[TSource]) -> AsyncIterable[TResult]:
    async for value in source:
        yield mapper(value)


__all__ = [
    "AsyncSeq",
    "range",
    "filter",
    "map",
    "repeat",
]
