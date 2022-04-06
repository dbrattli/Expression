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
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Iterable,
    Iterator,
    Optional,
    Tuple,
    TypeVar,
    cast,
    overload,
)

from expression.core import (
    Case,
    Option,
    SupportsGreaterThan,
    SupportsLessThan,
    SupportsSum,
    identity,
    pipe,
)

if TYPE_CHECKING:
    from .frozenlist import FrozenList

_TSource = TypeVar("_TSource")
_TResult = TypeVar("_TResult")
_TState = TypeVar("_TState")
_TSupportsGreaterThan = TypeVar("_TSupportsGreaterThan", bound=SupportsGreaterThan)
_TSupportsLessThan = TypeVar("_TSupportsLessThan", bound=SupportsLessThan)
_TSupportsSum = TypeVar("_TSupportsSum", bound=SupportsSum)
_T1 = TypeVar("_T1")
_T2 = TypeVar("_T2")
_T3 = TypeVar("_T3")
_T4 = TypeVar("_T4")


class Seq(Iterable[_TSource]):
    """Sequence type.

    Contains instance methods for dot-chaining operators methods on
    sequences.

    Example:
        >>> xs = Seq([1, 2, 3])
        >>> ys = xs.map(lambda x: x + 1).filter(lambda x: x < 3)
    """

    def __init__(self, iterable: Iterable[_TSource] = []) -> None:
        self._value = iterable

    @classmethod
    def of(cls, *args: _TSource) -> Seq[_TSource]:
        return cls(args)

    @classmethod
    def of_iterable(cls, source: Iterable[_TSource]) -> Seq[_TSource]:
        return cls(source)

    def append(self, *others: Iterable[_TSource]) -> Seq[_TSource]:
        """Wraps the two given enumerations as a single concatenated
        enumeration."""
        return Seq(concat(self._value, *others))

    def filter(self, predicate: Callable[[_TSource], bool]) -> Seq[_TSource]:
        return Seq(filter(predicate)(self))

    def choose(self, chooser: Callable[[_TSource], Option[_TResult]]) -> Seq[_TResult]:
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

    def collect(self, mapping: Callable[[_TSource], "Seq[_TResult]"]) -> Seq[_TResult]:
        xs = pipe(self, collect(mapping))
        return Seq(xs)

    @staticmethod
    def delay(generator: Callable[[], Iterable[_TSource]]) -> Iterable[_TSource]:
        """Returns a sequence that is built from the given delayed specification of a
        sequence.

        The input function is evaluated each time an IEnumerator for the sequence
        is requested.

        Args:
            generator: The generating function for the sequence.
        """

        return delay(generator)

    @staticmethod
    def empty() -> Seq[_TSource]:
        """Returns empty sequence."""
        return Seq()

    def fold(
        self, folder: Callable[[_TState, _TSource], _TState], state: _TState
    ) -> _TState:
        """Applies a function to each element of the collection,
        threading an accumulator argument through the computation. If
        the input function is f and the elements are i0...iN then
        computes f (... (f s i0)...) iN

        Args:
            folder: A function that updates the state with each element
                from the sequence.
            state: The initial state.
        Returns:
            The state object after the folding function is applied to
            each element of the sequence.
        """
        return functools.reduce(folder, self, state)

    def head(self) -> _TSource:
        """Returns the first element of the sequence."""

        return head(self)

    def length(self) -> int:
        """Returns the length of the sequence."""
        return length(self)

    def map(self, mapper: Callable[[_TSource], _TResult]) -> Seq[_TResult]:
        """Map sequence.

        Builds a new collection whose elements are the results of
        applying the given function to each of the elements of the
        collection.

        Args:
            mapping: A function to transform items from the input sequence.

        Returns:
            The result sequence.
        """

        return Seq(pipe(self, map(mapper)))

    @overload
    def starmap(
        self: Seq[Tuple[_T1, _T2]], mapping: Callable[[_T1, _T2], _TResult]
    ) -> Seq[_TResult]:
        ...

    @overload
    def starmap(
        self: Seq[Tuple[_T1, _T2, _T3]],
        mapping: Callable[[_T1, _T2, _T3], _TResult],
    ) -> Seq[_TResult]:
        ...

    @overload
    def starmap(
        self: Seq[Tuple[_T1, _T2, _T3, _T4]],
        mapping: Callable[[_T1, _T2, _T3, _T4], _TResult],
    ) -> Seq[_TResult]:
        ...

    def starmap(self: Seq[Tuple[Any, ...]], mapping: Callable[..., Any]) -> Seq[Any]:
        """Starmap source sequence.

        Unpack arguments grouped as tuple elements. Builds a new collection
        whose elements are the results of applying the given function to the
        unpacked arguments to each of the elements of the collection.

        Args:
            mapping: A function to transform items from the input sequence.

        Returns:
            Partially applied map function.
        """

        return Seq(starmap(mapping)(self))

    def mapi(self, mapping: Callable[[int, _TSource], _TResult]) -> Seq[_TResult]:
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

    @overload
    def match(self) -> Case[Iterable[_TSource]]:
        ...

    @overload
    def match(self, pattern: Any) -> Iterable[Iterable[_TSource]]:
        ...

    def match(self, pattern: Optional[Any] = None) -> Any:
        case: Case[Iterable[_TSource]] = Case(self)
        return case(pattern) if pattern else case

    @overload
    def pipe(self, __fn1: Callable[["Seq[_TSource]"], _TResult]) -> _TResult:
        ...

    @overload
    def pipe(
        self,
        __fn1: Callable[["Seq[_TSource]"], _T1],
        __fn2: Callable[[_T1], _T2],
    ) -> _T2:
        ...

    @overload
    def pipe(
        self,
        __fn1: Callable[["Seq[_TSource]"], _T1],
        __fn2: Callable[[_T1], _T2],
        __fn3: Callable[[_T2], _T3],
    ) -> _T3:
        ...

    @overload
    def pipe(
        self,
        __fn1: Callable[["Seq[_TSource]"], _T1],
        __fn2: Callable[[_T1], _T2],
        __fn3: Callable[[_T2], _T3],
        __fn4: Callable[[_T3], _T4],
    ) -> _T4:
        ...

    def pipe(self, *args: Any) -> Any:
        """Pipe sequence through the given functions."""
        return pipe(self, *args)

    @overload
    @staticmethod
    def range(stop: int) -> Iterable[int]:
        ...

    @overload
    @staticmethod
    def range(start: int, stop: int) -> Iterable[int]:
        ...

    @overload
    @staticmethod
    def range(start: int, stop: int, step: int) -> Iterable[int]:
        ...

    @staticmethod
    def range(*args: int, **kw: int) -> Iterable[int]:
        return range(*args, **kw)

    def scan(
        self, scanner: Callable[[_TState, _TSource], _TState], state: _TState
    ) -> Iterable[_TState]:
        """Like fold, but computes on-demand and returns the sequence of
        intermediary and final results.

        Args:
            scanner: A function that updates the state with each element
                from the sequence.
            state: The initial state.

        Returns:
            The resulting sequence of computed states.
        """
        return Seq(itertools.accumulate(self._value, scanner, initial=state))

    def skip(self, count: int) -> Seq[_TSource]:
        """Returns a sequence that skips N elements of the underlying
        sequence and then yields the remaining elements of the sequence.

        Args:
            count: The number of items to skip.
        """
        return Seq(pipe(self, skip(count)))

    def sum(self: Seq[_TSupportsSum]) -> _TSupportsSum:
        """Returns the sum of the elements in the sequence."""
        return sum(self)

    def sum_by(self, projection: Callable[[_TSource], _TSupportsSum]) -> _TSupportsSum:
        """Returns the sum of the results generated by applying the
        function to each element of the sequence."""
        return pipe(self, sum_by(projection))

    def tail(self) -> Seq[_TSource]:
        """Returns a sequence that skips 1 element of the underlying
        sequence and then yields the remaining elements of the
        sequence."""
        return self.skip(1)

    def take(self, count: int) -> Seq[_TSource]:
        """Returns the first N elements of the sequence.

        Args:
            count: The number of items to take.
        """
        return Seq(pipe(self, take(count)))

    def to_list(self) -> "FrozenList[_TSource]":
        return to_list(self)

    @classmethod
    def unfold(
        cls,
        generator: Callable[[_TState], Option[Tuple[_TSource, _TState]]],
        state: _TState,
    ) -> Iterable[_TSource]:
        """Returns a list that contains the elements generated by the
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

    def zip(self, other: Iterable[_TResult]) -> Iterable[Tuple[_TSource, _TResult]]:
        """Combines the two sequences into a list of pairs. The two
        sequences need not have equal lengths: when one sequence is
        exhausted any remaining elements in the other sequence are
        ignored.

        Args:
            other: The second input sequence.

        Returns:
            The result sequence.
        """
        return builtins.zip(self, other)

    def __iter__(self) -> Iterator[_TSource]:
        """Return iterator for sequence."""
        return builtins.iter(self._value)

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


class SeqGen(Iterable[_TSource]):
    """Sequence from a generator function.

    We use this to allow multiple iterations over the same sequence
    generated by a generator function."""

    def __init__(self, gen: Callable[[], Iterable[_TSource]]) -> None:
        self.gen = gen

    def __iter__(self) -> Iterator[_TSource]:
        xs = self.gen()
        return builtins.iter(xs)


def append(
    *others: Iterable[_TSource],
) -> Callable[[Iterable[_TSource]], Iterable[_TSource]]:
    """Wraps the given enumerations as a single concatenated
    enumeration."""

    def _(source: Iterable[_TSource]) -> Iterable[_TSource]:
        return concat(source, *others)

    return _


def choose(
    chooser: Callable[[_TSource], Option[_TResult]]
) -> Callable[[Iterable[_TSource]], Iterable[_TResult]]:
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

    def _choose(source: Iterable[_TSource]) -> Iterable[_TResult]:
        def mapper(x: _TSource) -> Iterable[_TResult]:
            return chooser(x).to_seq()

        return pipe(source, collect(mapper))

    return _choose


def collect(
    mapping: Callable[[_TSource], Iterable[_TResult]]
) -> Callable[[Iterable[_TSource]], Iterable[_TResult]]:
    def _collect(source: Iterable[_TSource]) -> Iterable[_TResult]:
        def gen():
            for xs in source:
                for x in mapping(xs):
                    yield x

        return SeqGen(gen)

    return _collect


def concat(*iterables: Iterable[_TSource]) -> Iterable[_TSource]:
    """Combines the given variable number of enumerations and/or
    enumeration-of-enumerations as a single concatenated
    enumeration.

    Args:
        iterables: The input enumeration-of-enumerations.

    Returns:
        The result sequence.
    """

    def gen():
        for it in iterables:
            for element in it:
                yield element

    return SeqGen(gen)


def delay(generator: Callable[[], Iterable[_TSource]]) -> Iterable[_TSource]:
    """Returns a sequence that is built from the given delayed
    specification of a sequence.

    The input function is evaluated each time an Iterator for the
    sequence is requested.

    Args:
        generator: The generating function for the sequence.
    """
    return SeqGen(generator)


empty: Seq[Any] = Seq()
"""The empty sequence."""


def filter(
    predicate: Callable[[_TSource], bool]
) -> Callable[[Iterable[_TSource]], Iterable[_TSource]]:
    """Filter sequence.

    Filters the sequence to a new sequence containing only the
    elements of the sequence for which the given predicate returns
    `True`.

    Args:
        predicate: A function to test whether each item in the
            input sequence should be included in the output.
        source: (curried) The input sequence to to filter.

    Returns:
        A partially applied filter function.
    """

    def _filter(source: Iterable[_TSource]) -> Iterable[_TSource]:
        """Filter sequence (partially applied).

        Args:
            source: The input sequence to to filter.

        Returns:
            Returns a new collection containing only the elements
            of the collection for which the given predicate returns
            `True`.
        """
        return builtins.filter(predicate, source)

    return _filter


def fold(
    folder: Callable[[_TState, _TSource], _TState], state: _TState
) -> Callable[[Iterable[_TSource]], _TState]:
    """Applies a function to each element of the collection,
    threading an accumulator argument through the computation. If
    the input function is f and the elements are i0...iN then
    computes f (... (f s i0)...) iN

    Args:
        folder: A function that updates the state with each element
            from the sequence.
        state: The initial state.

    Returns:
        Partially applied fold function that takes a source sequence and
        returns the state object after the folding function is applied
        to each element of the sequence.
    """

    def _fold(source: Iterable[_TSource]) -> _TState:
        """Partially applied fold function.
        Returns:
            The state object after the folding function is applied
            to each element of the sequence.
        """
        return functools.reduce(folder, source, state)

    return _fold


def fold_back(
    folder: Callable[[_TSource, _TState], _TState], source: Iterable[_TSource]
) -> Callable[[_TState], _TState]:
    """Applies a function to each element of the collection,
    starting from the end, threading an accumulator argument through
    the computation. If the input function is f and the elements are
    i0...iN then computes f i0 (... (f iN s)...)

    Args:
        folder: A function that updates the state with each element
            from the sequence.
        state: The initial state.

    Returns:
        Partially applied fold_back function.
    """

    def _fold_back(state: _TState) -> _TState:
        """Partially applied fold_back function.

        Returns:
            The state object after the folding function is applied
            to each element of the sequence.
        """
        return functools.reduce(
            lambda x, y: folder(y, x), reversed(list(source)), state
        )

    return _fold_back


def head(source: Iterable[_TSource]) -> _TSource:
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


def init_infinite(initializer: Callable[[int], _TSource]) -> Iterable[_TSource]:
    """Generates a new sequence which, when iterated, will return
    successive elements by calling the given function. The results of
    calling the function will not be saved, that is the function will be
    reapplied as necessary to regenerate the elements. The function is
    passed the index of the item being generated.

    Iteration can continue up to `sys.maxsize`.
    """

    class Infinite(Iterable[_TResult]):
        """An infinite iterable where each iterator starts counting at
        0."""

        def __init__(self, initializer: Callable[[int], _TResult]) -> None:
            self.initializer = initializer

        def __iter__(self) -> Iterator[_TResult]:
            return builtins.map(self.initializer, itertools.count(0, 1))

    return Infinite(initializer)


infinite: Iterable[int] = init_infinite(identity)
"""An infinite iterable."""


def iter(action: Callable[[_TSource], None]) -> Callable[[Iterable[_TSource]], None]:
    """Applies the given function to each element of the collection.

    Args:
        action: A function to apply to each element of the sequence.

    Returns:
        A partially applied iter function.
    """

    def _iter(source: Iterable[_TSource]) -> None:
        """A partially applied iter function.

        Note that this function is a pure side effect and returns nothing.

        Args:
            source: The input sequence to apply action to.

        Returns:
            None
        """
        for x in source:
            action(x)

    return _iter


def length(source: Seq[Any]) -> int:
    """Return the length of the sequence."""
    return builtins.sum(1 for _ in source)


def map(
    mapper: Callable[[_TSource], _TResult]
) -> Callable[[Iterable[_TSource]], Iterable[_TResult]]:
    """Map source sequence.

    Builds a new collection whose elements are the results of
    applying the given function to each of the elements of the
    collection.

    Args:
        mapping: A function to transform items from the input sequence.

    Returns:
        Partially applied map function.
    """

    def _map(source: Iterable[_TSource]) -> Iterable[_TResult]:
        """Partially applied map function.

        Args:
            source: The input sequence.
        Returns:
            The result sequence.
        """

        def gen():
            for x in source:
                yield mapper(x)

        return SeqGen(gen)

    return _map


@overload
def starmap(
    mapper: Callable[[_T1, _T2], _TResult]
) -> Callable[[Iterable[Tuple[_T1, _T2]]], Iterable[_TResult]]:
    ...


@overload
def starmap(
    mapper: Callable[[_T1, _T2, _T3], _TResult]
) -> Callable[[Iterable[Tuple[_T1, _T2, _T3]]], Iterable[_TResult]]:
    ...


@overload
def starmap(
    mapper: Callable[[_T1, _T2, _T3, _T4], _TResult]
) -> Callable[[Iterable[Tuple[_T1, _T2, _T3, _T4]]], Iterable[_TResult]]:
    ...


def starmap(
    mapper: Callable[..., Any]
) -> Callable[[Iterable[Tuple[Any, ...]]], Iterable[Any]]:
    """Starmap source sequence.

    Unpack arguments grouped as tuple elements. Builds a new collection
    whose elements are the results of applying the given function to the
    unpacked arguments to each of the elements of the collection.

    Args:
        mapping: A function to transform items from the input sequence.

    Returns:
        Partially applied map function.
    """

    def mapper_(args: Tuple[Any, ...]) -> Any:
        return mapper(*args)

    return map(mapper_)


def map2(
    mapper: Callable[[_T1, _T2], _TResult]
) -> Callable[[Iterable[Tuple[_T1, _T2]]], Iterable[_TResult]]:
    return starmap(mapper)


def map3(
    mapper: Callable[[_T1, _T2, _T3], _TResult]
) -> Callable[[Iterable[Tuple[_T1, _T2, _T3]]], Iterable[_TResult]]:
    return starmap(mapper)


def mapi(
    mapping: Callable[[int, _TSource], _TResult]
) -> Callable[[Iterable[_TSource]], Iterable[_TResult]]:
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

    def _mapi(source: Iterable[_TSource]) -> Iterable[_TResult]:
        return (*itertools.starmap(mapping, builtins.enumerate(source)),)

    return _mapi


def max(source: Iterable[_TSupportsGreaterThan]) -> _TSupportsGreaterThan:
    """Returns the greatest of all elements of the sequence,
    compared via `max()`."""

    value: _TSupportsGreaterThan = builtins.max(source)
    return value


def max_by(
    projection: Callable[[_TSource], _TSupportsGreaterThan]
) -> Callable[[Iterable[_TSource]], _TSupportsGreaterThan]:
    def _max_by(source: Iterable[_TSource]) -> _TSupportsGreaterThan:
        return builtins.max(projection(x) for x in source)

    return _max_by


def min(source: Iterable[_TSupportsLessThan]) -> _TSupportsLessThan:
    """Returns the smallest of all elements of the sequence,
    compared via `max()`."""

    return builtins.min(source)


def min_by(
    projection: Callable[[_TSource], _TSupportsLessThan]
) -> Callable[[Iterable[_TSource]], _TSupportsLessThan]:
    def _min_by(source: Iterable[_TSource]) -> _TSupportsLessThan:
        return builtins.min(projection(x) for x in source)

    return _min_by


def of(*args: _TSource) -> Seq[_TSource]:
    """Create sequence from iterable.

    Enables fluent dot chaining on the created sequence object.
    """
    return Seq(args)


def of_iterable(source: Iterable[_TSource]) -> Seq[_TSource]:
    """Alias to `Seq.of`."""
    return Seq(source)


of_list = of_iterable
"""Alias to `seq.of_iterable`."""


@overload
def range(stop: int) -> Iterable[int]:
    ...


@overload
def range(
    start: int,
    stop: int,
) -> Iterable[int]:
    ...


@overload
def range(start: int, stop: int, step: int) -> Iterable[int]:
    ...


def range(*args: int, **kw: int) -> Iterable[int]:
    return Seq(builtins.range(*args, **kw))


def scan(
    scanner: Callable[[_TState, _TSource], _TState], state: _TState
) -> Callable[[Iterable[_TSource]], Iterable[_TState]]:
    """Like fold, but computes on-demand and returns the sequence of
    intermediary and final results.

    Args:
        scanner: A function that updates the state with each element
        state: The initial state.
    """

    def _scan(source: Iterable[_TSource]) -> Iterable[_TState]:
        """Partially applied scan function.
        Args:
            source: The input sequence.
        Returns:
            The resulting sequence of computed states.
        """
        return itertools.accumulate(source, scanner, initial=state)

    return _scan


def singleton(item: _TSource) -> Seq[_TSource]:
    """Returns a sequence that yields one item only.

    Args:
        item: The input item.

    Returns:
        The result sequence of one item.
    """
    return Seq([item])


def skip(count: int) -> Callable[[Iterable[_TSource]], Iterable[_TSource]]:
    """Returns a sequence that skips N elements of the underlying
    sequence and then yields the remaining elements of the sequence.

    Args:
        count: The number of items to skip.
    """

    def _skip(source: Iterable[_TSource]) -> Iterable[_TSource]:
        def gen():
            for i, n in enumerate(source):
                if i >= count:
                    yield n

        return SeqGen(gen)

    return _skip


def sum(source: Iterable[_TSupportsSum]) -> _TSupportsSum:
    """Returns the sum of the elements in the sequence."""
    ret = builtins.sum(source)
    return cast(_TSupportsSum, ret)


def sum_by(
    projection: Callable[[_TSource], _TSupportsSum]
) -> Callable[[Iterable[_TSource]], _TSupportsSum]:
    """Returns the sum of the results generated by applying the
    function to each element of the sequence."""

    def _(source: Iterable[_TSource]) -> _TSupportsSum:
        return sum(projection(x) for x in source)

    return _


def tail(source: Iterable[_TSource]) -> Iterable[_TSource]:
    """Returns a sequence that skips 1 element of the underlying
    sequence and then yields the remaining elements of the
    sequence."""
    proj = cast(Callable[[Iterable[_TSource]], Iterable[_TSource]], skip(1))
    return proj(source)


def take(count: int) -> Callable[[Iterable[_TSource]], Iterable[_TSource]]:
    """Returns the first N elements of the sequence.

    Args:
        count: The number of items to take.

    Returns:
        The result sequence.
    """

    def _take(source: Iterable[_TSource]) -> Iterable[_TSource]:
        def gen():
            for i, n in enumerate(source):
                if i < count:
                    yield n

        return SeqGen(gen)

    return _take


def to_list(source: Iterable[_TSource]) -> "FrozenList[_TSource]":
    from .frozenlist import FrozenList

    return FrozenList.of_seq(source)


def unfold(
    generator: Callable[[_TState], Option[Tuple[_TSource, _TState]]]
) -> Callable[[_TState], Iterable[_TSource]]:
    """Generates a list that contains the elements generated by the
    given computation. The given initial state argument is passed to
    the element generator.

    Args:
        generator: A function that takes in the current state and
            returns an option tuple of the next element of the list
            and the next state value.

    Returns:
        A partially applied unfold function that takes the state and
        returns the result list.
    """

    def _unfold(state: _TState) -> Iterable[_TSource]:
        """Returns a list that contains the elements generated by the
        given computation. The given initial state argument is passed to
        the element generator.

        Args:
            state: The initial state.

        Returns:
            The result list.
        """
        while True:
            result = generator(state)
            if result.is_none():
                break

            item, state = result.value
            yield item

    return _unfold


def zip(
    source1: Iterable[_TSource],
) -> Callable[[Iterable[_TResult]], Iterable[Tuple[_TSource, _TResult]]]:
    """Combines the two sequences into a list of pairs. The two
    sequences need not have equal lengths: when one sequence is
    exhausted any remaining elements in the other sequence are
    ignored.

    Args:
        source1: The first input sequence.

    Returns:
        Partially applied zip function.
    """

    def _zip(source2: Iterable[_TResult]) -> Iterable[Tuple[_TSource, _TResult]]:
        """Combines the two sequences into a list of pairs. The two
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
    "concat",
    "collect",
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
    "of_list",
    "of_iterable",
    "range",
    "scan",
    "skip",
    "singleton",
    "sum",
    "sum_by",
    "tail",
    "take",
    "unfold",
    "zip",
]
