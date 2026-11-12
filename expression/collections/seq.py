"""Sequence module.

Contains a collection of static methods (functions) for operating on
sequences. A sequence is a thin wrapper around `Iterable` so all
functions take (and return) Python iterables.

All functions takes the source as the last curried
argument, i.e all functions returns a function that takes the source
sequence as the only argument.

Example (functional style):
    >>> from expression.collections import seq
    >>> xs = seq.of_iterable([1, 2, 3])
    >>> ys = xs.pipe(
        seq.map(lambda x: x + 1),
        seq.filter(lambda x: x < 3)
    )

Example (fluent style):
    >>> from expression.collections import Seq
    >>> xs = Seq([1, 2, 3])
    >>> ys = xs.map(lambda x: x + 1).filter(lambda x: x < 3)
"""

from __future__ import annotations

import builtins
import functools
import itertools
from collections.abc import Callable, Iterable, Iterator
from typing import TYPE_CHECKING, Any, Literal, cast, overload

from expression.core import (
    NOTHING,
    Option,
    PipeMixin,
    Some,
    SupportsGreaterThan,
    SupportsLessThan,
    SupportsSum,
    curry_flip,
    identity,
    pipe,
)


if TYPE_CHECKING:
    from .block import Block


class Seq[TSource](Iterable[TSource], PipeMixin):
    """Sequence type.

    Contains instance methods for dot-chaining operators methods on
    sequences.

    Example:
        >>> xs = Seq([1, 2, 3])
        >>> ys = xs.map(lambda x: x + 1).filter(lambda x: x < 3)
    """

    __match_args__ = ("iterable",)

    def __init__(self, iterable: Iterable[TSource] = ()) -> None:
        self._value = iterable

    @staticmethod
    def of[TResult](*args: TResult) -> Seq[TResult]:
        return Seq(args)

    @classmethod
    def of_iterable[TResult](cls: type[Seq[Any]], source: Iterable[TResult]) -> Seq[TResult]:
        return cls(source)

    def append(self, *others: Iterable[TSource]) -> Seq[TSource]:
        """Append sequence to other sequences.

        Wraps the given enumerations as a single concatenated
        enumeration.
        """
        return Seq(concat(self._value, *others))

    def filter(self, predicate: Callable[[TSource], bool]) -> Seq[TSource]:
        return Seq(filter(predicate)(self))

    def choose[TResult](self, chooser: Callable[[TSource], Option[TResult]]) -> Seq[TResult]:
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
        xs = pipe(self, choose(chooser))
        return Seq(xs)

    def concat[TResult](self: Seq[Seq[TResult]]) -> Seq[TResult]:
        """Concatenate sequences.

        Combines the given variable number of enumerations and/or
        enumeration-of-enumerations as a single concatenated enumeration.
        """
        return Seq(concat(*self))

    def collect[TResult](self, mapping: Callable[[TSource], Seq[TResult]]) -> Seq[TResult]:
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
        return self.map(mapping).concat()

    @staticmethod
    def delay[TResult](generator: Callable[[], Iterable[TResult]]) -> Iterable[TResult]:
        """Delay sequence.

        Returns a sequence that is built from the given delayed specification of a
        sequence.

        The input function is evaluated each time an IEnumerator for the sequence
        is requested.

        Args:
            generator: The generating function for the sequence.
        """
        return delay(generator)

    @staticmethod
    def empty() -> Seq[TSource]:
        """Returns empty sequence."""
        return Seq()

    def fold[TState](self, folder: Callable[[TState, TSource], TState], state: TState) -> TState:
        """Fold sequence.

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
        return functools.reduce(folder, self, state)

    def head(self) -> TSource:
        """Returns the first element of the sequence."""
        return head(self)

    def length(self) -> int:
        """Returns the length of the sequence."""
        return length(self)

    def map[TResult](self, mapper: Callable[[TSource], TResult]) -> Seq[TResult]:
        """Map sequence.

        Builds a new collection whose elements are the results of
        applying the given function to each of the elements of the
        collection.

        Args:
            mapper: A function to transform items from the input sequence.

        Returns:
            The result sequence.
        """
        return Seq(pipe(self, map(mapper)))

    @overload
    def starmap[T1, T2, TResult](self: Seq[tuple[T1, T2]], mapping: Callable[[T1, T2], TResult]) -> Seq[TResult]: ...

    @overload
    def starmap[T1, T2, T3, TResult](
        self: Seq[tuple[T1, T2, T3]],
        mapping: Callable[[T1, T2, T3], TResult],
    ) -> Seq[TResult]: ...

    @overload
    def starmap[T1, T2, T3, T4, TResult](
        self: Seq[tuple[T1, T2, T3, T4]],
        mapping: Callable[[T1, T2, T3, T4], TResult],
    ) -> Seq[TResult]: ...

    def starmap(self: Seq[Any], mapping: Callable[..., Any]) -> Seq[Any]:
        """Starmap source sequence.

        Unpack arguments grouped as tuple elements. Builds a new
        collection whose elements are the results of applying the given
        function to the unpacked arguments to each of the elements of
        the collection.

        Args:
            mapping: A function to transform items from the input sequence.

        Returns:
            Partially applied map function.
        """
        return Seq(starmap(mapping)(self))

    def mapi[TResult](self, mapping: Callable[[int, TSource], TResult]) -> Seq[TResult]:
        """Map list with index.

        Builds a new collection whose elements are the results of
        applying the given function to each of the elements of the
        collection. The integer index passed to the function indicates
        the index (from 0) of element being transformed.

        Args:
            mapping: The function to transform elements and their
                indices.

        Returns:
            The list of transformed elements.
        """
        return Seq(mapi(mapping)(self))

    def pairwise(self) -> Seq[tuple[TSource, TSource]]:
        """Return adjacent elements paired with their predecessor."""
        return Seq(pairwise(self))

    @overload
    @staticmethod
    def range(stop: int) -> Iterable[int]: ...

    @overload
    @staticmethod
    def range(start: int, stop: int) -> Iterable[int]: ...

    @overload
    @staticmethod
    def range(start: int, stop: int, step: int) -> Iterable[int]: ...

    @staticmethod
    def range(*args: int, **kw: int) -> Iterable[int]:
        return range(*args, **kw)

    def scan[TState](self, scanner: Callable[[TState, TSource], TState], state: TState) -> Iterable[TState]:
        """Scan sequence.

        Like fold, but computes on-demand and returns the sequence of
        intermediary and final results.

        Args:
            scanner: A function that updates the state with each element
                from the sequence.
            state: The initial state.

        Returns:
            The resulting sequence of computed states.
        """
        return Seq(itertools.accumulate(self._value, scanner, initial=state))

    def skip(self, count: int) -> Seq[TSource]:
        """Skip elements from sequence.

        Returns a sequence that skips N elements of the underlying
        sequence and then yields the remaining elements of the sequence.

        Args:
            count: The number of items to skip.
        """
        return Seq(pipe(self, skip(count)))

    def sum[TSupportsSum: SupportsSum](self: Seq[TSupportsSum]) -> TSupportsSum | Literal[0]:
        """Returns the sum of the elements in the sequence."""
        return sum(self)

    def sum_by[TSupportsSum: SupportsSum](
        self, projection: Callable[[TSource], TSupportsSum]
    ) -> TSupportsSum | Literal[0]:
        """Sum the sequence by projection.

        Returns the sum of the results generated by applying the
        function to each element of the sequence.
        """
        return pipe(self, sum_by(projection))

    def tail(self) -> Seq[TSource]:
        """Return the tail of the sequence.

        Returns a sequence that skips 1 element of the underlying
        sequence and then yields the remaining elements of the
        sequence.
        """
        return self.skip(1)

    def take(self, count: int) -> Seq[TSource]:
        """Returns the first N elements of the sequence.

        Args:
            count: The number of items to take.
        """
        return Seq(pipe(self, take(count)))

    def take_while(self, predicate: Callable[[TSource], bool]) -> Seq[TSource]:
        """Returns elements while a predicate holds.

        Returns a sequence that yields elements from the underlying
        sequence while the given predicate returns `True`, and then
        skips the remaining elements.

        Args:
            predicate: A function that evaluates to `False` when no more
                items should be returned.
        """
        return Seq(pipe(self, take_while(predicate)))

    def to_list(self) -> Block[TSource]:
        return to_list(self)

    def try_find_index(self, predicate: Callable[[TSource], bool]) -> Option[int]:
        """Return the index of the first element matching the predicate, if any."""
        return pipe(self, try_find_index(predicate))

    def try_pick[TResult](self, chooser: Callable[[TSource], Option[TResult]]) -> Option[TResult]:
        """Return the first value produced by the chooser, if any."""
        return pipe(self, try_pick(chooser))

    def dict(self) -> Iterable[TSource]:
        """Returns a json serializable representation of the list."""

        def to_obj(value: Any) -> Any:
            attr = getattr(value, "dict", None) or getattr(value, "dict", None)
            if attr and callable(attr):
                value = attr()
            return value

        return (to_obj(value) for value in self)

    @classmethod
    def unfold[TState, TResult](
        cls,
        generator: Callable[[TState], Option[tuple[TResult, TState]]],
        state: TState,
    ) -> Iterable[TResult]:
        """Unfold sequence.

        Returns a list that contains the elements generated by the
        given computation. The given initial state argument is passed to
        the element generator.

        Args:
            generator: A function that takes in the current state and
                returns an option tuple of the next element of the list
                and the next state value.
            state: The initial state.

        Returns:
            The result list.
        """
        return pipe(state, unfold(generator))

    def zip[TResult](self, other: Iterable[TResult]) -> Iterable[tuple[TSource, TResult]]:
        """Zip sequence.

        Combines the two sequences into a list of pairs. The two
        sequences need not have equal lengths: when one sequence is
        exhausted any remaining elements in the other sequence are
        ignored.

        Args:
            other: The second input sequence.

        Returns:
            The result sequence.
        """
        return builtins.zip(self, other)

    def __iter__(self) -> Iterator[TSource]:
        """Return iterator for sequence."""
        # Make sure we return a proper generator that can handle send, throw, and close
        return (x for x in self._value)

    def __repr__(self) -> str:
        result = "["

        for count, x in enumerate(self):
            if count == 0:
                result += str(x)

            elif count == 100:
                result += "; ..."
                break

            else:
                result += "; " + str(x)

        return result + "]"

    def __str__(self) -> str:
        return repr(self)


class SeqGen[TSource](Iterable[TSource]):
    """Sequence from a generator function.

    We use this to allow multiple iterations over the same sequence
    generated by a generator function.
    """

    def __init__(self, gen: Callable[[], Iterable[TSource]]) -> None:
        self.gen = gen

    def __iter__(self) -> Iterator[TSource]:
        xs = self.gen()
        # Make sure we return a proper generator that can handle send, throw, and close
        return (x for x in xs)


def append[TSource](
    *others: Iterable[TSource],
) -> Callable[[Iterable[TSource]], Iterable[TSource]]:
    """Append sequence to other sequences.

    Wraps the given enumerations as a single concatenated enumeration.
    """

    def _(source: Iterable[TSource]) -> Iterable[TSource]:
        return concat(source, *others)

    return _


@curry_flip(1)
def choose[TSource, TResult](
    source: Iterable[TSource], chooser: Callable[[TSource], Option[TResult]]
) -> Iterable[TResult]:
    """Choose items from the sequence.

    Applies the given function to each element of the list. Returns
    the list comprised of the results x for each element where the
    function returns `Some(x)`.

    Args:
        source: The input sequence to to choose from.
        chooser: The function to generate options from the elements.

    Returns:
        The list comprising the values selected from the chooser
        function.
    """

    def mapper(x: TSource) -> Iterable[TResult]:
        return chooser(x).to_seq()

    return pipe(source, collect(mapper))


@curry_flip(1)
def collect[TSource, TResult](
    source: Iterable[TSource],
    mapping: Callable[[TSource], Iterable[TResult]],
) -> Iterable[TResult]:
    """Collect items from the sequence.

    Applies the given function to each element of the list and
    concatenates all the resulting sequences. This function is known as
    `bind` or `flat_map` in other languages.

    Args:
        source: The input sequence to to collect from.
        mapping: The function to generate sequences from the elements.

    Returns:
        A sequence comprising the concatenated values from the mapping
        function.
    """

    def gen() -> Iterator[TResult]:
        for xs in source:
            yield from mapping(xs)

    return SeqGen(gen)


def concat[TSource](*iterables: Iterable[TSource]) -> Iterable[TSource]:
    """Concatenate sequences.

    Combines the given variable number of enumerations and/or
    enumeration-of-enumerations as a single concatenated enumeration.

    Args:
        iterables: The input enumeration-of-enumerations.

    Returns:
        The result sequence.
    """

    def gen() -> Iterator[TSource]:
        for it in iterables:
            yield from it

    return SeqGen(gen)


def delay[TSource](generator: Callable[[], Iterable[TSource]]) -> Iterable[TSource]:
    """Delay sequence.

    Returns a sequence that is built from the given delayed
    specification of a sequence.

    The input function is evaluated each time an Iterator for the
    sequence is requested.

    Args:
        generator: The generating function for the sequence.
    """
    return SeqGen(generator)


empty: Seq[Any] = Seq()
"""The empty sequence."""


@curry_flip(1)
def filter[TSource](source: Iterable[TSource], predicate: Callable[[TSource], bool]) -> Iterable[TSource]:
    """Filter sequence.

    Filters the sequence to a new sequence containing only the
    elements of the sequence for which the given predicate returns
    `True`.

    Args:
        source: (curried) The input sequence to to filter.
        predicate: A function to test whether each item in the
            input sequence should be included in the output.

    Returns:
        A partially applied filter function.
    """
    return builtins.filter(predicate, source)


@curry_flip(1)
def fold[TSource, TState](
    source: Iterable[TSource],
    folder: Callable[[TState, TSource], TState],
    state: TState,
) -> TState:
    """Fold elements in sequence.

    Applies a function to each element of the collection,
    threading an accumulator argument through the computation. If
    the input function is f and the elements are i0...iN then
    computes f (... (f s i0)...) iN.

    Args:
        source: The input sequence to fold.
        folder: A function that updates the state with each element
            from the sequence.
        state: The initial state.

    Returns:
        Partially applied fold function that takes a source sequence and
        returns the state object after the folding function is applied
        to each element of the sequence.
    """
    return functools.reduce(folder, source, state)


def fold_back[TState, TSource](
    folder: Callable[[TSource, TState], TState], source: Iterable[TSource]
) -> Callable[[TState], TState]:
    """Fold elements in sequence backwards.

    Applies a function to each element of the collection,
    starting from the end, threading an accumulator argument through
    the computation. If the input function is f and the elements are
    i0...iN then computes f i0 (... (f iN s)...).

    Args:
        folder: A function that updates the state with each element
            from the sequence.
        source: The input sequence to fold backwards.

    Returns:
        Partially applied fold_back function.
    """

    def _fold_back(state: TState) -> TState:
        """Partially applied fold_back function.

        Returns:
            The state object after the folding function is applied
            to each element of the sequence.
        """
        return functools.reduce(lambda x, y: folder(y, x), reversed(list(source)), state)

    return _fold_back


def head[TSource](source: Iterable[TSource]) -> TSource:
    """Return the first element of the sequence.

    Args:
        source: The input sequence.

    Returns:
        The first element of the sequence.

    Raises:
        Raises `ValueError` if the source sequence is empty.
    """
    for value in source:
        return value

    raise ValueError("Sequence contains no elements")


def init_infinite[TSource](initializer: Callable[[int], TSource]) -> Iterable[TSource]:
    """Generate infinite sequence.

    Generates a new sequence which, when iterated, will return
    successive elements by calling the given function. The results of
    calling the function will not be saved, that is the function will be
    reapplied as necessary to regenerate the elements. The function is
    passed the index of the item being generated.

    Iteration can continue up to `sys.maxsize`.
    """

    class Infinite[TResult](Iterable[TResult]):
        """An infinite iterable.

        Where each iterator starts counting at 0.
        """

        def __init__(self, initializer: Callable[[int], TResult]) -> None:
            self.initializer = initializer

        def __iter__(self) -> Iterator[TResult]:
            return builtins.map(self.initializer, itertools.count(0, 1))

    return Infinite(initializer)


infinite: Iterable[int] = init_infinite(identity)
"""An infinite iterable."""


@curry_flip(1)
def iter[TSource](source: Iterable[TSource], action: Callable[[TSource], None]) -> None:
    """Applies the given function to each element of the collection.

    Args:
        source: The input sequence to iterate.
        action: A function to apply to each element of the sequence.

    Returns:
        A partially applied iter function.
    """
    for x in source:
        action(x)


def length(source: Seq[Any]) -> int:
    """Return the length of the sequence."""
    return builtins.sum(1 for _ in source)


@curry_flip(1)
def map[TSource, TResult](source: Iterable[TSource], mapper: Callable[[TSource], TResult]) -> Iterable[TResult]:
    """Map source sequence.

    Builds a new collection whose elements are the results of
    applying the given function to each of the elements of the
    collection.

    Args:
        source: The input sequence to map.
        mapper: A function to transform items from the input sequence.

    Returns:
        Partially applied map function.
    """

    def gen():
        for x in source:
            yield mapper(x)

    return SeqGen(gen)


@overload
def starmap[T1, T2, TResult](
    mapper: Callable[[T1, T2], TResult],
) -> Callable[[Iterable[tuple[T1, T2]]], Iterable[TResult]]: ...


@overload
def starmap[T1, T2, T3, TResult](
    mapper: Callable[[T1, T2, T3], TResult],
) -> Callable[[Iterable[tuple[T1, T2, T3]]], Iterable[TResult]]: ...


@overload
def starmap[T1, T2, T3, T4, TResult](
    mapper: Callable[[T1, T2, T3, T4], TResult],
) -> Callable[[Iterable[tuple[T1, T2, T3, T4]]], Iterable[TResult]]: ...


def starmap(mapper: Callable[..., Any]) -> Callable[[Iterable[Any]], Iterable[Any]]:
    """Starmap source sequence.

    Unpack arguments grouped as tuple elements. Builds a new collection
    whose elements are the results of applying the given function to the
    unpacked arguments to each of the elements of the collection.

    Args:
        mapper: A function to transform items from the input sequence.

    Returns:
        Partially applied map function.
    """

    def mapper_(args: tuple[Any, ...]) -> Any:
        return mapper(*args)

    return map(mapper_)


def map2[T1, T2, TResult](
    mapper: Callable[[T1, T2], TResult],
) -> Callable[[Iterable[tuple[T1, T2]]], Iterable[TResult]]:
    return starmap(mapper)


def map3[T1, T2, T3, TResult](
    mapper: Callable[[T1, T2, T3], TResult],
) -> Callable[[Iterable[tuple[T1, T2, T3]]], Iterable[TResult]]:
    return starmap(mapper)


@curry_flip(1)
def mapi[TSource, TResult](source: Iterable[TSource], mapping: Callable[[int, TSource], TResult]) -> Iterable[TResult]:
    """Map list with index.

    Builds a new collection whose elements are the results of
    applying the given function to each of the elements of the
    collection. The integer index passed to the function indicates
    the index (from 0) of element being transformed.

    Args:
        source: The input sequence to to map.
        mapping: The function to transform elements and their
            indices.

    Returns:
        The list of transformed elements.
    """
    return (*itertools.starmap(mapping, builtins.enumerate(source)),)


def max[TSupportsGreaterThan: SupportsGreaterThan](source: Iterable[TSupportsGreaterThan]) -> TSupportsGreaterThan:
    """Return maximum of all elements.

    Returns the greatest of all elements of the sequence, compared via
    `max()`.
    """
    value: TSupportsGreaterThan = builtins.max(source)
    return value


@curry_flip(1)
def max_by[TSource, TSupportsGreaterThan: SupportsGreaterThan](
    source: Iterable[TSource], projection: Callable[[TSource], TSupportsGreaterThan]
) -> TSupportsGreaterThan:
    return builtins.max(projection(x) for x in source)


def min[TSupportsLessThan: SupportsLessThan](source: Iterable[TSupportsLessThan]) -> TSupportsLessThan:
    """Return the minimum of all elements.

    Returns the smallest of all elements of the sequence, compared via
    `max()`.
    """
    return builtins.min(source)


@curry_flip(1)
def min_by[TSource, TSupportsLessThan: SupportsLessThan](
    source: Iterable[TSource], projection: Callable[[TSource], TSupportsLessThan]
) -> TSupportsLessThan:
    return builtins.min(projection(x) for x in source)


def of[TSource](*args: TSource) -> Seq[TSource]:
    """Create sequence from iterable.

    Enables fluent dot chaining on the created sequence object.
    """
    return Seq(args)


def of_iterable[TSource](source: Iterable[TSource]) -> Seq[TSource]:
    """Alias to `Seq.of`."""
    return Seq(source)


of_list = of_iterable
"""Alias to `seq.of_iterable`."""


def pairwise[TSource](source: Iterable[TSource]) -> Iterable[tuple[TSource, TSource]]:
    """Return adjacent elements paired with their predecessor.

    The result is evaluated lazily and contains no elements when the source has
    fewer than two elements.

    Args:
        source: The input sequence.

    Returns:
        A sequence of overlapping adjacent pairs.

    Example:
        >>> list(pairwise([1, 2, 3, 4]))
        [(1, 2), (2, 3), (3, 4)]
    """
    return SeqGen(lambda: itertools.pairwise(source))


@overload
def range(stop: int) -> Iterable[int]: ...


@overload
def range(
    start: int,
    stop: int,
) -> Iterable[int]: ...


@overload
def range(start: int, stop: int, step: int) -> Iterable[int]: ...


def range(*args: int, **kw: int) -> Iterable[int]:
    return Seq(builtins.range(*args, **kw))


@curry_flip(1)
def scan[TSource, TState](
    source: Iterable[TSource],
    scanner: Callable[[TState, TSource], TState],
    state: TState,
) -> Iterable[TState]:
    """Scan elements in sequence.

    Like fold, but computes on-demand and returns the sequence of
    intermediary and final results.

    Args:
        source: The input sequence.
        scanner: A function that updates the state with each element
        state: The initial state.
    """
    return itertools.accumulate(source, scanner, initial=state)


def singleton[TSource](item: TSource) -> Seq[TSource]:
    """Returns a sequence that yields one item only.

    Args:
        item: The input item.

    Returns:
        The result sequence of one item.
    """
    return Seq([item])


@curry_flip(1)
def skip[TSource](source: Iterable[TSource], count: int) -> Iterable[TSource]:
    """Skip elements from sequence.

    Returns a sequence that skips N elements of the underlying
    sequence and then yields the remaining elements of the sequence.

    Args:
        source: The input sequence.
        count: The number of items to skip.
    """

    def gen():
        for i, n in enumerate(source):
            if i >= count:
                yield n

    return SeqGen(gen)


def sum[TSupportsSum: SupportsSum](source: Iterable[TSupportsSum]) -> TSupportsSum | Literal[0]:
    """Returns the sum of the elements in the sequence."""
    return builtins.sum(source)


@curry_flip(1)
def sum_by[TSource, TSupportsSum: SupportsSum](
    source: Iterable[TSource], projection: Callable[[TSource], TSupportsSum]
) -> TSupportsSum | Literal[0]:
    """Sum all elements in sequence.

    Returns the sum of the results generated by applying the function to
    each element of the sequence.
    """
    return sum(projection(x) for x in source)


def tail[TSource](source: Iterable[TSource]) -> Iterable[TSource]:
    """Return tail of sequence.

    Returns a sequence that skips 1 element of the underlying sequence
    and then yields the remaining elements of the sequence.
    """
    proj = cast(Callable[[Iterable[TSource]], Iterable[TSource]], skip(1))
    return proj(source)


@curry_flip(1)
def take[TSource](source: Iterable[TSource], count: int) -> Iterable[TSource]:
    """Returns the first N elements of the sequence.

    Args:
        source: The source sequence.
        count: The number of items to take.

    Returns:
        The result sequence.
    """

    def gen():
        for i, n in enumerate(source):
            yield n

            if i == count - 1:
                break

    if count > 0:
        return SeqGen(gen)
    return Seq()


@curry_flip(1)
def take_while[TSource](source: Iterable[TSource], predicate: Callable[[TSource], bool]) -> Iterable[TSource]:
    """Returns elements while a predicate holds.

    Returns a sequence that yields elements from the underlying
    sequence while the given predicate returns `True`, and then
    skips the remaining elements.

    Args:
        source: The source sequence.
        predicate: A function that evaluates to `False` when no more
            items should be returned.

    Returns:
        The result sequence.
    """

    def gen() -> Iterator[TSource]:
        for item in source:
            if not predicate(item):
                break
            yield item

    return SeqGen(gen)


def to_list[TSource](source: Iterable[TSource]) -> Block[TSource]:
    from .block import Block

    return Block.of_seq(source)


@curry_flip(1)
def try_find_index[TSource](source: Iterable[TSource], predicate: Callable[[TSource], bool]) -> Option[int]:
    """Return the index of the first element matching the predicate, if any.

    Indices are zero-based, and evaluation stops as soon as the predicate
    returns `True`.

    Args:
        source: The input sequence.
        predicate: A function to test each element.

    Returns:
        The first matching index wrapped in `Some`, or `Nothing()` when no
        element matches.

    Example:
        >>> pipe([1, 2, 3], try_find_index(lambda value: value % 2 == 0))
        Some 1
    """
    for index, value in enumerate(source):
        if predicate(value):
            return Some(index)

    return NOTHING


@curry_flip(1)
def try_pick[TSource, TResult](
    source: Iterable[TSource], chooser: Callable[[TSource], Option[TResult]]
) -> Option[TResult]:
    """Return the first value produced by the chooser, if any.

    The chooser is evaluated in sequence order, and evaluation stops as
    soon as it returns `Some`.

    Args:
        source: The input sequence.
        chooser: A function that transforms elements into optional results.

    Returns:
        The first result wrapped in `Some`, or `Nothing()` when the chooser
        returns `Nothing()` for every element.

    Example:
        >>> pipe([1, 2, 3], try_pick(lambda value: option.of_obj(value * 10 if value % 2 == 0 else None)))
        Some 20
    """
    for value in source:
        result = chooser(value)
        if result.is_some():
            return result

    return NOTHING


@curry_flip(1)
def unfold[TState, TSource](
    state: TState, generator: Callable[[TState], Option[tuple[TSource, TState]]]
) -> Iterable[TSource]:
    """Unfold sequence.

    Generates a list that contains the elements generated by the given
    computation. The given initial state argument is passed to the
    element generator.

    Args:
        state: The initial state.
        generator: A function that takes in the current state and
            returns an option tuple of the next element of the list
            and the next state value.

    Returns:
        A partially applied unfold function that takes the state and
        returns the result list.
    """
    while True:
        result = generator(state)
        if result.is_none():
            break

        item, state = result.value
        yield item


def zip[TSource, TResult](
    source1: Iterable[TSource],
) -> Callable[[Iterable[TResult]], Iterable[tuple[TSource, TResult]]]:
    """Zip sequence with other.

    Combines the two sequences into a list of pairs. The two
    sequences need not have equal lengths: when one sequence is
    exhausted any remaining elements in the other sequence are
    ignored.

    Args:
        source1: The first input sequence.

    Returns:
        Partially applied zip function.
    """

    def _zip(source2: Iterable[TResult]) -> Iterable[tuple[TSource, TResult]]:
        """Curried function.

        Combines the two sequences into a list of pairs. The two
        sequences need not have equal lengths: when one sequence is
        exhausted any remaining elements in the other sequence are
        ignored.

        Args:
            source2: The second input sequence.

        Returns:
            The result sequence.
        """
        return builtins.zip(source1, source2)

    return _zip


__all__ = [
    "Seq",
    "append",
    "choose",
    "collect",
    "concat",
    "delay",
    "empty",
    "filter",
    "fold",
    "fold_back",
    "head",
    "iter",
    "map",
    "mapi",
    "max",
    "min",
    "min_by",
    "of",
    "of_iterable",
    "of_list",
    "pairwise",
    "range",
    "scan",
    "singleton",
    "skip",
    "sum",
    "sum_by",
    "tail",
    "take",
    "take_while",
    "try_find_index",
    "try_pick",
    "unfold",
    "zip",
]
