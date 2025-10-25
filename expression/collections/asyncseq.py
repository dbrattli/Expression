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
        return pipe(self, map(mapper))

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
            mapping: The function to generate sequences from the elements.

        Returns:
            A sequence comprising the concatenated values from the mapping
            function.
        """

        async def _collect(source: AsyncIterable[TSource]) -> AsyncIterable[TResult]:
            async for value in source:
                async for item in mapping(value):
                    yield item

        return pipe(self, _collect)

    async def concat(self: AsyncSeq[AsyncIterable[TResult]]) -> AsyncIterable[TResult]:
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
            predicate: A function to test whether each item in the
                input sequence should be included in the output.

        Returns:
            The filtered sequence.
        """

        async def _filter(source: AsyncIterable[TSource]) -> AsyncIterable[TSource]:
            async for value in source:
                if predicate(value):
                    yield value

        return pipe(self, _filter)

    async def fold(self, folder: Callable[[TState, TSource], TState], state: TState) -> TState:
        """Fold elements in sequence.

        Applies a function to each element of the collection,
        threading an accumulator argument through the computation. If
        the input function is f and the elements are i0...iN then
        computes f (... (f s i0)...) iN.

        Args:
            folder: A function that updates the state with each element
                from the sequence.
            state: The initial state.

        Returns:
            The state object after the folding function is applied to
            each element of the sequence.
        """
        result = state
        async for value in self:
            result = folder(result, value)
        return result

    async def fold_back(self, folder: Callable[[TSource, TState], TState], state: TState) -> TState:
        """Fold elements in sequence backwards.

        Applies a function to each element of the collection,
        starting from the end, threading an accumulator argument through
        the computation. If the input function is f and the elements are
        i0...iN then computes f i0 (... (f iN s)...).

        Args:
            folder: A function that updates the state with each element
                from the sequence.
            state: The initial state.

        Returns:
            The state object after the folding function is applied to
            each element of the sequence.
        """
        # Convert to list first since we need to iterate backwards
        items = []
        async for value in self:
            items.append(value)

        result = state
        for value in reversed(items):
            result = folder(value, result)
        return result

    async def scan(self, scanner: Callable[[TState, TSource], TState], state: TState) -> AsyncIterable[TState]:
        """Scan elements in sequence.

        Like fold, but computes on-demand and returns the sequence of
        intermediary and final results.

        Args:
            scanner: A function that updates the state with each element
                from the sequence.
            state: The initial state.

        Returns:
            The resulting sequence of computed states.
        """
        result = state
        yield result

        async for value in self:
            result = scanner(result, value)
            yield result

    async def take(self, count: int) -> AsyncIterable[TSource]:
        """Returns the first N elements of the sequence.

        Args:
            count: The number of items to take.
        """

        async def _take(source: AsyncIterable[TSource]) -> AsyncIterable[TSource]:
            i = 0
            async for value in source:
                if i >= count:
                    break
                yield value
                i += 1

        return pipe(self, _take)

    async def skip(self, count: int) -> AsyncIterable[TSource]:
        """Skip elements from sequence.

        Returns a sequence that skips N elements of the underlying
        sequence and then yields the remaining elements of the sequence.

        Args:
            count: The number of items to skip.
        """

        async def _skip(source: AsyncIterable[TSource]) -> AsyncIterable[TSource]:
            i = 0
            async for value in source:
                if i >= count:
                    yield value
                i += 1

        return pipe(self, _skip)

    async def head(self) -> TSource:
        """Returns the first element of the sequence.

        Returns:
            The first element of the sequence.

        Raises:
            Raises `ValueError` if the source sequence is empty.
        """
        async for value in self:
            return value

        raise ValueError("Sequence contains no elements")

    async def tail(self) -> AsyncIterable[TSource]:
        """Return the tail of the sequence.

        Returns a sequence that skips 1 element of the underlying
        sequence and then yields the remaining elements of the
        sequence.
        """

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
        """Return maximum of all elements.

        Returns the greatest of all elements of the sequence, compared via
        `max()`.
        """
        items = []
        async for value in self:
            items.append(value)
        if not items:
            raise ValueError("Sequence contains no elements")
        return builtins.max(items)

    async def min(self) -> TSource:
        """Return the minimum of all elements.

        Returns the smallest of all elements of the sequence, compared via
        `min()`.
        """
        items = []
        async for value in self:
            items.append(value)
        if not items:
            raise ValueError("Sequence contains no elements")
        return builtins.min(items)

    async def max(self) -> TSource:
        """Return maximum of all elements.

        Returns the greatest of all elements of the sequence, compared via
        `max()`.
        """
        items = []
        async for value in self:
            items.append(value)
        if not items:
            raise ValueError("Sequence contains no elements")
        return builtins.max(items)

    async def min(self) -> TSource:
        """Return the minimum of all elements.

        Returns the smallest of all elements of the sequence, compared via
        `min()`.
        """
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
    for value in itertools.repeat(value, times or 0):
        yield value


@overload
def range(stop: int) -> AsyncIterable[int]: ...


@overload
def range(start: int, stop: int) -> AsyncIterable[int]: ...


@overload
def range(start: int, stop: int, step: int) -> AsyncIterable[int]: ...


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

    return _choose


def collect(
    mapping: Callable[[TSource], AsyncIterable[TResult]],
) -> Callable[[AsyncIterable[TSource]], AsyncIterable[TResult]]:
    """Collect items from the sequence.

    Applies the given function to each element of the list and
    concatenates all the resulting sequences. This function is known
    as `bind` or `flat_map` in other languages.

    Args:
        mapping: The function to generate sequences from the elements.

    Returns:
        A sequence comprising the concatenated values from the mapping
        function.
    """

    async def _collect(source: AsyncIterable[TSource]) -> AsyncIterable[TResult]:
        async for value in source:
            async for item in mapping(value):
                yield item

    return _collect


async def concat(source: AsyncIterable[AsyncIterable[TSource]]) -> AsyncIterable[TSource]:
    """Concatenate sequences.

    Combines the given variable number of enumerations and/or
    enumeration-of-enumerations as a single concatenated enumeration.
    """
    async for value in source:
        async for item in value:
            yield item


def fold(folder: Callable[[TState, TSource], TState], state: TState) -> Callable[[AsyncIterable[TSource]], TState]:
    """Fold elements in sequence.

    Applies a function to each element of the collection,
    threading an accumulator argument through the computation. If
    the input function is f and the elements are i0...iN then
    computes f (... (f s i0)...) iN.

    Args:
        folder: A function that updates the state with each element
            from the sequence.
        state: The initial state.

    Returns:
        The state object after the folding function is applied to
        each element of the sequence.
    """

    async def _fold(source: AsyncIterable[TSource]) -> TState:
        result = state
        async for value in source:
            result = folder(result, value)
        return result

    return _fold


def fold_back(folder: Callable[[TSource, TState], TState], state: TState) -> Callable[[AsyncIterable[TSource]], TState]:
    """Fold elements in sequence backwards.

    Applies a function to each element of the collection,
    starting from the end, threading an accumulator argument through
    the computation. If the input function is f and the elements are
    i0...iN then computes f i0 (... (f iN s)...).

    Args:
        folder: A function that updates the state with each element
            from the sequence.
        state: The initial state.

    Returns:
        The state object after the folding function is applied to
        each element of the sequence.
    """

    async def _fold_back(source: AsyncIterable[TSource]) -> TState:
        # Convert to list first since we need to iterate backwards
        items = []
        async for value in source:
            items.append(value)

        result = state
        for value in reversed(items):
            result = folder(value, result)
        return result

    return _fold_back


def scan(
    scanner: Callable[[TState, TSource], TState], state: TState
) -> Callable[[AsyncIterable[TSource]], AsyncIterable[TState]]:
    """Scan elements in sequence.

    Like fold, but computes on-demand and returns the sequence of
    intermediary and final results.

    Args:
        scanner: A function that updates the state with each element
            from the sequence.
        state: The initial state.

    Returns:
        The resulting sequence of computed states.
    """

    async def _scan(source: AsyncIterable[TSource]) -> AsyncIterable[TState]:
        result = state
        yield result

        async for value in source:
            result = scanner(result, value)
            yield result

    return _scan


def take(count: int) -> Callable[[AsyncIterable[TSource]], AsyncIterable[TSource]]:
    """Returns the first N elements of the sequence.

    Args:
        count: The number of items to take.
    """

    async def _take(source: AsyncIterable[TSource]) -> AsyncIterable[TSource]:
        i = 0
        async for value in source:
            if i >= count:
                break
            yield value
            i += 1

    return _take


def skip(count: int) -> Callable[[AsyncIterable[TSource]], AsyncIterable[TSource]]:
    """Skip elements from sequence.

    Returns a sequence that skips N elements of the underlying
    sequence and then yields the remaining elements of the sequence.

    Args:
        count: The number of items to skip.
    """

    async def _skip(source: AsyncIterable[TSource]) -> AsyncIterable[TSource]:
        i = 0
        async for value in source:
            if i >= count:
                yield value
            i += 1

    return _skip


async def head(source: AsyncIterable[TSource]) -> TSource:
    """Returns the first element of the sequence.

    Returns:
        The first element of the sequence.

    Raises:
        Raises `ValueError` if the source sequence is empty.
    """
    async for value in source:
        return value

    raise ValueError("Sequence contains no elements")


async def tail(source: AsyncIterable[TSource]) -> AsyncIterable[TSource]:
    """Return the tail of the sequence.

    Returns a sequence that skips 1 element of the underlying
    sequence and then yields the remaining elements of the
    sequence.
    """

    async def _tail(source: AsyncIterable[TSource]) -> AsyncIterable[TSource]:
        first = True
        async for value in source:
            if first:
                first = False
                continue
            yield value

    return _tail


async def length(source: AsyncIterable[TSource]) -> int:
    """Returns the length of the sequence."""
    count = 0
    async for _ in source:
        count += 1
    return count


async def sum(source: AsyncIterable[TSource]) -> TSource:
    """Returns the sum of the elements in the sequence."""
    result: TSource = 0  # type: ignore
    async for value in source:
        result += value  # type: ignore
    return result


async def max(source: AsyncIterable[TSource]) -> TSource:
    """Return maximum of all elements.

    Returns the greatest of all elements of the sequence, compared via
    `max()`.
    """
    items = []
    async for value in source:
        items.append(value)
    if not items:
        raise ValueError("Sequence contains no elements")
    return builtins.max(items)


async def min(source: AsyncIterable[TSource]) -> TSource:
    """Return the minimum of all elements.

    Returns the smallest of all elements of the sequence, compared via
    `min()`.
    """
    items = []
    async for value in source:
        items.append(value)
    if not items:
        raise ValueError("Sequence contains no elements")
    return builtins.min(items)


__all__ = [
    "AsyncSeq",
    "choose",
    "collect",
    "concat",
    "filter",
    "fold",
    "fold_back",
    "head",
    "length",
    "map",
    "max",
    "min",
    "range",
    "repeat",
    "scan",
    "skip",
    "sum",
    "tail",
    "take",
]
