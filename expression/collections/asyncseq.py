import builtins
import itertools
from collections.abc import AsyncIterable, AsyncIterator, Callable
from typing import Any, TypeVar, overload

from expression.core import Option, pipe


TSource = TypeVar("TSource")
TResult = TypeVar("TResult")
TState = TypeVar("TState")


class AsyncSeq(AsyncIterable[TSource]):
    def __init__(self, ai: AsyncIterable[TSource]):
        self._ai = ai

    async def map(self, mapper: Callable[[TSource], TResult]) -> "AsyncSeq[TResult]":
        # Use the module-level `map` function defined later to transform the
        # underlying async iterable and wrap the result back into an AsyncSeq.
        return AsyncSeq(pipe(self._ai, map(mapper)))  # type: ignore[arg-type]

    @classmethod
    async def empty(cls) -> "AsyncSeq[Any]":
        return AsyncSeq(empty())

    @overload
    @classmethod
    def range(cls, stop: int) -> "AsyncSeq[int]": ...

    @overload
    @classmethod
    def range(cls, start: int, stop: int) -> "AsyncSeq[int]": ...

    @overload
    @classmethod
    def range(cls, start: int, stop: int, step: int) -> "AsyncSeq[int]": ...

    @classmethod
    def range(cls, *args: int, **kw: int) -> "AsyncSeq[int]":
        return AsyncSeq(range(*args, **kw))

    def __aiter__(self) -> AsyncIterator[TSource]:
        return self._ai.__aiter__()

    async def choose(self, chooser: Callable[[TSource], Option[TResult]]) -> AsyncIterable[TResult]:
        """Choose items from the sequence.

        Applies the given function to each element of the list. Returns
        the list comprised of the results x for each element where the
        function returns `Some(x)`.

        Args:
            chooser: The function to generate options from the elements.

        Returns:
            The list comprising the values selected from the chooser
            function.
        """

        async def _choose(source: AsyncIterable[TSource]) -> AsyncIterable[TResult]:
            async for value in source:
                result = chooser(value)
                if not result.is_none():
                    yield result.value

        return pipe(self, _choose)

    async def collect(self, mapping: Callable[[TSource], AsyncIterable[TResult]]) -> AsyncIterable[TResult]:
        """Collect items from the sequence.

        Applies the given function to each element of the list and
        concatenates all the resulting sequences. This function is known
        as `bind` or `flat_map` in other languages.

        Args:
            mapping: The function that generates an async iterable for each element.

        Returns:
            An async iterable yielding all items from the inner iterables.
        """

        async def _collect(source: AsyncIterable[TSource]) -> AsyncIterable[TResult]:
            async for value in source:
                async for item in mapping(value):
                    yield item

        return pipe(self, _collect)

    async def concat(self: "AsyncSeq[AsyncIterable[TResult]]") -> AsyncIterable[TResult]:
        """Concatenate sequences.

        Combines the given variable number of enumerations and/or
        enumeration-of-enumerations as a single concatenated enumeration.
        """

        async def _concat(source: AsyncIterable[AsyncIterable[TSource]]) -> AsyncIterable[TSource]:
            async for value in source:
                async for item in value:
                    yield item

        return pipe(self, _concat)

    async def filter(self, predicate: Callable[[TSource], bool]) -> AsyncIterable[TSource]:
        """Filter sequence.

        Filters the sequence to a new sequence containing only the
        elements of the sequence for which the given predicate returns
        `True`.

        Args:
            predicate: A function that tests each item.

        Returns:
            The filtered async iterable.
        """

        async def _filter(source: AsyncIterable[TSource]) -> AsyncIterable[TSource]:
            async for value in source:
                if predicate(value):
                    yield value

        return pipe(self, _filter)

    async def fold(self, folder: Callable[[TState, TSource], TState], state: TState) -> TState:
        """Fold elements in sequence.

        Applies a function to each element of the collection,
        threading an accumulator argument through the computation.
        """
        result = state
        async for value in self:
            result = folder(result, value)
        return result

    async def fold_back(self, folder: Callable[[TSource, TState], TState], state: TState) -> TState:
        """Fold elements in sequence backwards.

        Applies the function to each element of the collection,
        starting from the end.
        """
        items = []
        async for value in self:
            items.append(value)

        result = state
        for value in reversed(items):
            result = folder(value, result)
        return result

    async def scan(self, scanner: Callable[[TState, TSource], TState], state: TState) -> AsyncIterable[TState]:
        """Scan elements in sequence.

        Like fold, but yields intermediate results.
        """
        result = state
        yield result

        async for value in self:
            result = scanner(result, value)
            yield result

    async def take(self, count: int) -> AsyncIterable[TSource]:
        """Returns the first N elements of the sequence."""

        async def _take(source: AsyncIterable[TSource]) -> AsyncIterable[TSource]:
            i = 0
            async for value in source:
                if i >= count:
                    break
                yield value
                i += 1

        return pipe(self, _take)

    async def skip(self, count: int) -> AsyncIterable[TSource]:
        """Skip elements from sequence."""

        async def _skip(source: AsyncIterable[TSource]) -> AsyncIterable[TSource]:
            i = 0
            async for value in source:
                if i >= count:
                    yield value
                i += 1

        return pipe(self, _skip)

    async def head(self) -> TSource:
        """Returns the first element of the sequence."""
        async for value in self:
            return value
        raise ValueError("Sequence contains no elements")

    async def tail(self) -> AsyncIterable[TSource]:
        """Return the tail of the sequence."""

        async def _tail(source: AsyncIterable[TSource]) -> AsyncIterable[TSource]:
            first = True
            async for value in source:
                if first:
                    first = False
                    continue
                yield value

        return pipe(self, _tail)

    async def length(self) -> int:
        """Returns the length of the sequence."""
        count = 0
        async for _ in self:
            count += 1
        return count

    async def sum(self) -> TSource:
        """Returns the sum of the elements in the sequence."""
        result: TSource = 0  # type: ignore
        async for value in self:
            result += value  # type: ignore
        return result

    async def max(self) -> TSource:
        """Return maximum of all elements."""
        items = []
        async for value in self:
            items.append(value)
        if not items:
            raise ValueError("Sequence contains no elements")
        return builtins.max(items)

    async def min(self) -> TSource:
        """Return minimum of all elements."""
        items = []
        async for value in self:
            items.append(value)
        if not items:
            raise ValueError("Sequence contains no elements")
        return builtins.min(items)


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


async def repeat(value: TSource, times: int | None = None) -> AsyncIterable[TSource]:
    for v in itertools.repeat(value, times or 0):
        yield v


@overload
def range(stop: int) -> AsyncIterable[int]: ...
@overload
def range(start: int, stop: int) -> AsyncIterable[int]: ...
@overload
def range(start: int, start_stop: int, step: int) -> AsyncIterable[int]: ...


async def range(*args: int, **kw: int) -> AsyncIterable[int]:
    for value in builtins.range(*args, **kw):
        yield value


def filter(predicate: Callable[[TSource], bool]) -> Callable[[AsyncIterable[TSource]], AsyncIterable[TSource]]:
    async def _filter(source: AsyncIterable[TSource]) -> AsyncIterable[TSource]:
        async for value in source:
            if predicate(value):
                yield value

    return _filter


def map(mapper: Callable[[TSource], TResult]) -> Callable[[AsyncIterable[TSource]], AsyncIterable[TResult]]:
    async def _map(source: AsyncIterable[TSource]) -> AsyncIterable[TResult]:
        async for value in source:
            yield mapper(value)

    return _map


def choose(chooser: Callable[[TSource], Option[TResult]]) -> Callable[[AsyncIterable[TSource]], AsyncIterable[TResult]]:
    """Choose items from the sequence."""
    async def _choose(source: AsyncIterable[TSource]) -> AsyncIterable[TResult]:
        async for value in source:
            result = chooser(value)
            if not result.is_none():
                yield result.value

    return _choose


def collect(
    mapping: Callable[[TSource], AsyncIterable[TResult]],
) -> Callable[[AsyncIterable[TSource]], AsyncIterable[TResult]]:
    """Collect items from the sequence."""
    async def _collect(source: AsyncIterable[TSource]) -> AsyncIterable[TResult]:
        async for value in source:
            async for item in mapping(value):
                yield item

    return _collect
