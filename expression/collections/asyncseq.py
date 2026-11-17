import builtins
import itertools
from collections.abc import AsyncIterable, AsyncIterator, Awaitable, Callable, Coroutine, Iterable
from typing import Any, cast, overload

from expression.core import Option
from expression.core.typing import SupportsLessThan, SupportsSum


class AsyncSeq[TSource](AsyncIterable[TSource]):
    """A lazy async sequence with directly chainable transformations.

    Stream transformations return AsyncSeq without awaiting. Terminal operations
    are awaited to consume the source and compute a result. Operations prefixed
    with ``a`` await their callbacks during consumption.
    """

    def __init__(self, ai: AsyncIterable[TSource]):
        self._ai = ai

    def map[TResult](self, mapper: Callable[[TSource], TResult]) -> "AsyncSeq[TResult]":
        """Lazily transform each item with a synchronous callback."""
        return AsyncSeq(map(mapper)(self))

    def amap[TResult](self, mapper: Callable[[TSource], Awaitable[TResult]]) -> "AsyncSeq[TResult]":
        """Lazily await the mapper for each item, sequentially and in source order.

        Constructing the sequence requires no await. Exceptions and cancellation
        propagate during iteration; returned collections remain individual items.
        """
        return AsyncSeq(amap(mapper)(self))

    def afilter(self, predicate: Callable[[TSource], Awaitable[bool]]) -> "AsyncSeq[TSource]":
        """Lazily keep items whose awaited predicate is true."""
        return AsyncSeq(afilter(predicate)(self))

    def achoose[TResult](self, chooser: Callable[[TSource], Awaitable[Option[TResult]]]) -> "AsyncSeq[TResult]":
        """Lazily await the chooser and yield the values of present options."""
        return AsyncSeq(achoose(chooser)(self))

    def acollect[TResult](
        self, mapping: Callable[[TSource], Awaitable[Iterable[TResult] | AsyncIterable[TResult]]]
    ) -> "AsyncSeq[TResult]":
        """Lazily await each mapping and flatten its ordinary or async iterable."""
        return AsyncSeq(acollect(mapping)(self))

    async def afold[TState](self, folder: Callable[[TState, TSource], Awaitable[TState]], state: TState) -> TState:
        """Consume the sequence, awaiting each accumulator update in order."""
        return await afold(folder, state)(self)

    async def afold_back[TState](self, folder: Callable[[TSource, TState], Awaitable[TState]], state: TState) -> TState:
        """Buffer the sequence, then await accumulator updates in reverse order."""
        return await afold_back(folder, state)(self)

    def ascan[TState](
        self, scanner: Callable[[TState, TSource], Awaitable[TState]], state: TState
    ) -> "AsyncSeq[TState]":
        """Lazily yield the initial state and each awaited accumulator update."""
        return AsyncSeq(ascan(scanner, state)(self))

    @classmethod
    def empty(cls) -> "AsyncSeq[Any]":
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

    def choose[TResult](self, chooser: Callable[[TSource], Option[TResult]]) -> "AsyncSeq[TResult]":
        """Choose items from the sequence.

        Applies the given function to each element of the sequence. Returns
        the sequence comprised of the results x for each element where the
        function returns `Some(x)`.

        Args:
            chooser: The function to generate options from the elements.

        Returns:
            The async sequence comprising the values selected from the chooser
            function.
        """
        return AsyncSeq(choose(chooser)(self))

    def collect[TResult](self, mapping: Callable[[TSource], AsyncIterable[TResult]]) -> "AsyncSeq[TResult]":
        """Collect items from the sequence.

        Applies the given function to each element of the sequence and
        concatenates all the resulting sequences. This function is known
        as `bind` or `flat_map` in other languages.

        Args:
            mapping: The function that generates an async iterable for each element.

        Returns:
            An async sequence yielding all items from the inner iterables.
        """
        return AsyncSeq(collect(mapping)(self))

    def concat[TResult](self: "AsyncSeq[AsyncIterable[TResult]]") -> "AsyncSeq[TResult]":
        """Concatenate sequences.

        Combines the given variable number of enumerations and/or
        enumeration-of-enumerations as a single concatenated enumeration.
        """

        async def _concat(source: AsyncIterable[AsyncIterable[TResult]]) -> AsyncIterable[TResult]:
            async for value in source:
                async for item in value:
                    yield item

        return AsyncSeq(_concat(self))

    def filter(self, predicate: Callable[[TSource], bool]) -> "AsyncSeq[TSource]":
        """Filter sequence.

        Filters the sequence to a new sequence containing only the
        elements of the sequence for which the given predicate returns
        `True`.

        Args:
            predicate: A function that tests each item.

        Returns:
            The filtered async sequence.
        """
        return AsyncSeq(filter(predicate)(self))

    async def fold[TState](self, folder: Callable[[TState, TSource], TState], state: TState) -> TState:
        """Fold elements in sequence.

        Applies a function to each element of the collection,
        threading an accumulator argument through the computation.
        """
        result = state
        async for value in self:
            result = folder(result, value)
        return result

    async def fold_back[TState](self, folder: Callable[[TSource, TState], TState], state: TState) -> TState:
        """Fold elements in sequence backwards.

        Applies the function to each element of the collection,
        starting from the end.
        """
        items: list[TSource] = []
        async for value in self:
            items.append(value)

        result = state
        for value in reversed(items):
            result = folder(value, result)
        return result

    def scan[TState](self, scanner: Callable[[TState, TSource], TState], state: TState) -> "AsyncSeq[TState]":
        """Lazily yield the initial state and each synchronous accumulator update."""

        async def _scan() -> AsyncIterator[TState]:
            result = state
            yield result
            async for value in self:
                result = scanner(result, value)
                yield result

        return AsyncSeq(_scan())

    def take(self, count: int) -> "AsyncSeq[TSource]":
        """Returns the first N elements of the sequence."""

        async def _take(source: AsyncIterable[TSource]) -> AsyncIterable[TSource]:
            if count <= 0:
                return
            i = 0
            async for value in source:
                yield value
                i += 1
                if i >= count:
                    break

        return AsyncSeq(_take(self))

    def skip(self, count: int) -> "AsyncSeq[TSource]":
        """Skip elements from sequence."""

        async def _skip(source: AsyncIterable[TSource]) -> AsyncIterable[TSource]:
            i = 0
            async for value in source:
                if i >= count:
                    yield value
                i += 1

        return AsyncSeq(_skip(self))

    async def head(self) -> TSource:
        """Returns the first element of the sequence."""
        async for value in self:
            return value
        raise ValueError("Sequence contains no elements")

    def tail(self) -> "AsyncSeq[TSource]":
        """Return the tail of the sequence."""

        async def _tail(source: AsyncIterable[TSource]) -> AsyncIterable[TSource]:
            first = True
            async for value in source:
                if first:
                    first = False
                    continue
                yield value

        return AsyncSeq(_tail(self))

    async def length(self) -> int:
        """Returns the length of the sequence."""
        count = 0
        async for _ in self:
            count += 1
        return count

    async def sum[TSourceSum: SupportsSum](self: "AsyncSeq[TSourceSum]") -> TSourceSum:
        """Returns the sum of the elements in the sequence."""
        result = cast(TSourceSum, 0)
        async for value in self:
            result = cast(TSourceSum, result + value)
        return result

    async def max[TSourceSortable: SupportsLessThan](self: "AsyncSeq[TSourceSortable]") -> TSourceSortable:
        """Return maximum of all elements."""
        items: list[TSourceSortable] = []
        async for value in self:
            items.append(value)
        if not items:
            raise ValueError("Sequence contains no elements")
        return builtins.max(items)

    async def min[TSourceSortable: SupportsLessThan](self: "AsyncSeq[TSourceSortable]") -> TSourceSortable:
        """Return minimum of all elements."""
        items: list[TSourceSortable] = []
        async for value in self:
            items.append(value)
        if not items:
            raise ValueError("Sequence contains no elements")
        return builtins.min(items)


def append[TSource](
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


async def repeat[TSource](value: TSource, times: int | None = None) -> AsyncIterable[TSource]:
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


def filter[TSource](predicate: Callable[[TSource], bool]) -> Callable[[AsyncIterable[TSource]], AsyncIterable[TSource]]:
    async def _filter(source: AsyncIterable[TSource]) -> AsyncIterable[TSource]:
        async for value in source:
            if predicate(value):
                yield value

    return _filter


def map[TSource, TResult](
    mapper: Callable[[TSource], TResult],
) -> Callable[[AsyncIterable[TSource]], AsyncIterable[TResult]]:
    async def _map(source: AsyncIterable[TSource]) -> AsyncIterable[TResult]:
        async for value in source:
            yield mapper(value)

    return _map


def amap[TSource, TResult](
    mapper: Callable[[TSource], Awaitable[TResult]],
) -> Callable[[Iterable[TSource] | AsyncIterable[TSource]], AsyncIterable[TResult]]:
    """Map an ordinary or async iterable with an awaitable-returning callback.

    The returned async iterable is lazy: each requested item awaits one mapper
    call before advancing the source. Results preserve source order and are not
    flattened. No tasks are scheduled, and exceptions and cancellation propagate.
    Use ordinary ``pipe`` to compose this transformation; consume it with
    ``async for``. Sources implementing both protocols use async iteration.
    """

    async def _amap(source: Iterable[TSource] | AsyncIterable[TSource]) -> AsyncIterator[TResult]:
        async for value in _iterate(source):
            yield await mapper(value)

    return _amap


def choose[TSource, TResult](
    chooser: Callable[[TSource], Option[TResult]],
) -> Callable[[AsyncIterable[TSource]], AsyncIterable[TResult]]:
    """Choose items from the sequence."""

    async def _choose(source: AsyncIterable[TSource]) -> AsyncIterable[TResult]:
        async for value in source:
            result = chooser(value)
            if not result.is_none():
                yield result.value

    return _choose


def collect[TSource, TResult](
    mapping: Callable[[TSource], AsyncIterable[TResult]],
) -> Callable[[AsyncIterable[TSource]], AsyncIterable[TResult]]:
    """Collect items from the sequence."""

    async def _collect(source: AsyncIterable[TSource]) -> AsyncIterable[TResult]:
        async for value in source:
            async for item in mapping(value):
                yield item

    return _collect


async def _iterate[TSource](source: Iterable[TSource] | AsyncIterable[TSource]) -> AsyncIterator[TSource]:
    if isinstance(source, AsyncIterable):
        async for value in source:
            yield value
    else:
        for value in source:
            yield value


def afilter[TSource](
    predicate: Callable[[TSource], Awaitable[bool]],
) -> Callable[[Iterable[TSource] | AsyncIterable[TSource]], AsyncIterable[TSource]]:
    """Lazily await a predicate for each item, yielding only matching items.

    Accept ordinary or async iterables. Callbacks run sequentially in source
    order; exceptions and cancellation propagate during iteration.
    """

    async def _afilter(source: Iterable[TSource] | AsyncIterable[TSource]) -> AsyncIterator[TSource]:
        async for value in _iterate(source):
            if await predicate(value):
                yield value

    return _afilter


def achoose[TSource, TResult](
    chooser: Callable[[TSource], Awaitable[Option[TResult]]],
) -> Callable[[Iterable[TSource] | AsyncIterable[TSource]], AsyncIterable[TResult]]:
    """Lazily await a chooser and yield present values, skipping Nothing.

    Accept ordinary or async iterables. Callbacks run sequentially in source
    order; exceptions and cancellation propagate during iteration.
    """

    async def _achoose(source: Iterable[TSource] | AsyncIterable[TSource]) -> AsyncIterator[TResult]:
        async for value in _iterate(source):
            result = await chooser(value)
            if not result.is_none():
                yield result.value

    return _achoose


def acollect[TSource, TResult](
    mapping: Callable[[TSource], Awaitable[Iterable[TResult] | AsyncIterable[TResult]]],
) -> Callable[[Iterable[TSource] | AsyncIterable[TSource]], AsyncIterable[TResult]]:
    """Lazily await each mapping and flatten its ordinary or async iterable.

    Accept ordinary or async sources. Consume each inner iterable before advancing
    the source. Exceptions and cancellation propagate. For callbacks returning
    async iterables directly, without an awaitable wrapper, use ``collect``.
    """

    async def _acollect(source: Iterable[TSource] | AsyncIterable[TSource]) -> AsyncIterator[TResult]:
        async for value in _iterate(source):
            async for item in _iterate(await mapping(value)):
                yield item

    return _acollect


def afold[TSource, TState](
    folder: Callable[[TState, TSource], Awaitable[TState]], state: TState
) -> Callable[[Iterable[TSource] | AsyncIterable[TSource]], Coroutine[Any, Any, TState]]:
    """Consume an ordinary or async iterable, awaiting each accumulator update.

    Return the initial state for empty input. Run callbacks sequentially in source
    order, propagating exceptions and cancellation. Await the resulting coroutine.
    """

    async def _afold(source: Iterable[TSource] | AsyncIterable[TSource]) -> TState:
        result = state
        async for value in _iterate(source):
            result = await folder(result, value)
        return result

    return _afold


def afold_back[TSource, TState](
    folder: Callable[[TSource, TState], Awaitable[TState]], state: TState
) -> Callable[[Iterable[TSource] | AsyncIterable[TSource]], Coroutine[Any, Any, TState]]:
    """Buffer a finite ordinary or async iterable, then fold in reverse order.

    Await callbacks sequentially with item before state. Empty input returns the
    initial state. Exceptions and cancellation propagate. Memory use is linear in
    source length; await the resulting coroutine.
    """

    async def _afold_back(source: Iterable[TSource] | AsyncIterable[TSource]) -> TState:
        items = [value async for value in _iterate(source)]
        result = state
        for value in reversed(items):
            result = await folder(value, result)
        return result

    return _afold_back


def ascan[TSource, TState](
    scanner: Callable[[TState, TSource], Awaitable[TState]], state: TState
) -> Callable[[Iterable[TSource] | AsyncIterable[TSource]], AsyncIterable[TState]]:
    """Lazily yield the initial state and each awaited accumulator update.

    Accept ordinary or async iterables. Yield the initial state without touching
    the source. Callbacks run sequentially; exceptions and cancellation propagate.
    """

    async def _ascan(source: Iterable[TSource] | AsyncIterable[TSource]) -> AsyncIterator[TState]:
        result = state
        yield result
        async for value in _iterate(source):
            result = await scanner(result, value)
            yield result

    return _ascan
