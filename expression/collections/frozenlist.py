"""A frozen immutable list module.

This module provides an immutable list type `FrozenList` and  a set of
useful methods and functions for working with the list.

Named "FrozenList" to avoid conflicts with the builtin Python List type.

A FrozenList is actually a Python tuple. Tuples in Python are
immutable and gives us a high performant implementation of immutable
lists.

Example:
    >>> xs = frozenlist.of_list([1, 2, 3, 4, 5])
    >>> ys = frozenlist.empty.cons(1).cons(2).cons(3).cons(4).cons(5)
    >>> zs = pipe(
...     xs,
...     frozenlist.filter(lambda x: x<10)
... )
"""
from __future__ import annotations

import builtins
import functools
import itertools
from typing import (
    Any,
    Callable,
    Generic,
    Iterable,
    Iterator,
    List,
    Optional,
    Tuple,
    TypeVar,
    cast,
    get_origin,
    overload,
)

from expression.core import Case, Nothing, Option, Some, SupportsLessThan, pipe

from . import seq

_TSource = TypeVar("_TSource")
_TSourceSortable = TypeVar("_TSourceSortable", bound=SupportsLessThan)
_TSourceIn = TypeVar("_TSourceIn", contravariant=True)
_TResult = TypeVar("_TResult")
_TResultOut = TypeVar("_TResultOut", covariant=True)
_TState = TypeVar("_TState")

_T1 = TypeVar("_T1")
_T2 = TypeVar("_T2")
_T3 = TypeVar("_T3")
_T4 = TypeVar("_T4")
_T5 = TypeVar("_T5")
_T6 = TypeVar("_T6")


class FrozenList(Generic[_TSource]):
    """Immutable list type.

    Is faster than `List` for prepending, but slower for
    appending.

    Count: 200K

    | Operation | FrozenList | List   |
    |-----------|------------|--------|
    | Append    | 3.29 s     | 0.02 s |
    | Prepend   | 0.05 s     | 7.02 s |

    Example:
        >>> xs = Cons(5, Cons(4, Cons(3, Cons(2, Cons(1, Nil)))))
        >>> ys = empty.cons(1).cons(2).cons(3).cons(4).cons(5)
    """

    def __init__(self, value: Optional[Iterable[_TSource]] = None) -> None:
        # Use composition instead of inheritance since generic tuples
        # are not suppored by mypy.
        self.value: Tuple[_TSource, ...] = tuple(value) if value else tuple()

    def match(self, pattern: Any) -> Any:
        case: Case[_TSource] = Case(self)
        return case(pattern) if pattern else case

    @overload
    def pipe(self, __fn1: Callable[[FrozenList[_TSource]], _TResult]) -> _TResult:
        ...

    @overload
    def pipe(
        self, __fn1: Callable[[FrozenList[_TSource]], _T1], __fn2: Callable[[_T1], _T2]
    ) -> _T2:
        ...

    @overload
    def pipe(
        self,
        __fn1: Callable[[FrozenList[_TSource]], _T1],
        __fn2: Callable[[_T1], _T2],
        __fn3: Callable[[_T2], _T3],
    ) -> _T3:
        ...

    @overload
    def pipe(
        self,
        __fn1: Callable[[FrozenList[_TSource]], _T1],
        __fn2: Callable[[_T1], _T2],
        __fn3: Callable[[_T2], _T3],
        __fn4: Callable[[_T3], _T4],
    ) -> _T4:
        ...

    @overload
    def pipe(
        self,
        __fn1: Callable[[FrozenList[_TSource]], _T1],
        __fn2: Callable[[_T1], _T2],
        __fn3: Callable[[_T2], _T3],
        __fn4: Callable[[_T3], _T4],
        __fn5: Callable[[_T4], _T5],
    ) -> _T5:
        ...

    @overload
    def pipe(
        self,
        __fn1: Callable[[FrozenList[_TSource]], _T1],
        __fn2: Callable[[_T1], _T2],
        __fn3: Callable[[_T2], _T3],
        __fn4: Callable[[_T3], _T4],
        __fn5: Callable[[_T4], _T5],
        __fn6: Callable[[_T5], _T6],
    ) -> _T6:
        ...

    def pipe(self, *args: Any) -> Any:
        """Pipe list through the given functions."""
        return pipe(self, *args)

    def append(self, other: FrozenList[_TSource]) -> FrozenList[_TSource]:
        """Append frozen list to end of the frozen list."""

        return FrozenList(self.value + other.value)

    def choose(
        self, chooser: Callable[[_TSource], Option[_TResult]]
    ) -> FrozenList[_TResult]:
        """Choose items from the list.

        Applies the given function to each element of the list. Returns
        the list comprised of the results x for each element where the
        function returns `Some(x)`.

        Args:
            chooser: The function to generate options from the elements.

        Returns:
            The list comprising the values selected from the chooser
            function.
        """

        def mapper(x: _TSource) -> FrozenList[_TResult]:
            return FrozenList(chooser(x).to_seq())

        return self.collect(mapper)

    def collect(
        self, mapping: Callable[[_TSource], FrozenList[_TResult]]
    ) -> FrozenList[_TResult]:
        mapped = builtins.map(mapping, self.value)
        xs = (y for x in mapped for y in x)
        return FrozenList(xs)

    def cons(self, element: _TSource) -> FrozenList[_TSource]:
        """Add element to front of list."""

        return FrozenList((element,) + self.value)  # NOTE: Faster than (element, *self)

    @staticmethod
    def empty() -> FrozenList[Any]:
        """Returns empty list."""

        return FrozenList()

    def filter(self, predicate: Callable[[_TSource], bool]) -> FrozenList[_TSource]:
        """Filter list.

        Returns a new collection containing only the elements of the
        collection for which the given predicate returns `True`.

        Args:
            predicate: The function to test the input elements.

        Returns:
            A list containing only the elements that satisfy the
            predicate.
        """
        return FrozenList(builtins.filter(predicate, self.value))

    def fold(
        self, folder: Callable[[_TState, _TSource], _TState], state: _TState
    ) -> _TState:
        """Applies a function to each element of the collection,
        threading an accumulator argument through the computation. Take
        the second argument, and apply the function to it and the first
        element of the list. Then feed this result into the function
        along with the second element and so on. Return the final
        result. If the input function is f and the elements are i0...iN
        then computes f (... (f s i0) i1 ...) iN.

        Args:
            folder: The function to update the state given the input
                elements.

            state: The initial state.

        Returns:
            Partially applied fold function that takes the source list
            and returns the final state value.
        """
        return functools.reduce(folder, self, state)

    def forall(self, predicate: Callable[[_TSource], bool]) -> bool:
        """Tests if all elements of the collection satisfy the given
        predicate.

        Args:
            predicate: The function to test the input elements.

        Returns:
            True if all of the elements satisfy the predicate.
        """
        return all(predicate(x) for x in self)

    def head(self) -> _TSource:
        """Returns the first element of the list.

        Args:
            source: The input list.

        Returns:
            The first element of the list.

        Raises:
            ValueError: Thrown when the list is empty.
        """

        head, *_ = self
        return head

    def indexed(self, start: int = 0) -> FrozenList[Tuple[int, _TSource]]:
        """Returns a new list whose elements are the corresponding
        elements of the input list paired with the index (from `start`)
        of each element.

        Args:
            start: Optional index to start from. Defaults to 0.

        Returns:
            The list of indexed elements.
        """
        return of_seq(enumerate(self))

    def item(self, index: int) -> _TSource:
        """Indexes into the list. The first element has index 0.

        Args:
            index: The index to retrieve.

        Returns:
            The value at the given index.
        """
        return self[index]

    def is_empty(self) -> bool:
        """Return `True` if list is empty."""

        return not bool(self)

    def map(self, mapping: Callable[[_TSource], _TResult]) -> FrozenList[_TResult]:
        """Map list.

        Builds a new collection whose elements are the results of
        applying the given function to each of the elements of the
        collection.

        Args:
            mapping: The function to transform elements from the input
                list.

        Returns:
            The list of transformed elements.
        """
        return FrozenList((*builtins.map(mapping, self),))

    @overload
    def starmap(
        self: FrozenList[Tuple[_T1, _T2]], mapping: Callable[[_T1, _T2], _TResult]
    ) -> FrozenList[_TResult]:
        ...

    @overload
    def starmap(
        self: FrozenList[Tuple[_T1, _T2, _T3]],
        mapping: Callable[[_T1, _T2, _T3], _TResult],
    ) -> FrozenList[_TResult]:
        ...

    @overload
    def starmap(
        self: FrozenList[Tuple[_T1, _T2, _T3, _T4]],
        mapping: Callable[[_T1, _T2, _T3, _T4], _TResult],
    ) -> FrozenList[_TResult]:
        ...

    def starmap(
        self: FrozenList[Tuple[Any, ...]], mapping: Callable[..., Any]
    ) -> FrozenList[Any]:
        """Starmap source sequence.

        Unpack arguments grouped as tuple elements. Builds a new collection
        whose elements are the results of applying the given function to the
        unpacked arguments to each of the elements of the collection.

        Args:
            mapping: A function to transform items from the input sequence.

        Returns:
            Partially applied map function.
        """
        return FrozenList(starmap(mapping)(self))

    def mapi(
        self, mapping: Callable[[int, _TSource], _TResult]
    ) -> FrozenList[_TResult]:
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
        return FrozenList((*itertools.starmap(mapping, enumerate(self)),))

    @staticmethod
    def of(*args: _TSource) -> FrozenList[_TSource]:
        """Create list from a number of arguments."""
        return FrozenList((*args,))

    @staticmethod
    def of_seq(xs: Iterable[_TSource]) -> FrozenList[_TSource]:
        """Create list from iterable sequence."""
        return FrozenList((*xs,))

    @staticmethod
    def of_option(option: Option[_TSource]) -> FrozenList[_TSource]:
        return of_option(option)

    @overload
    @staticmethod
    def range(stop: int) -> FrozenList[int]:
        ...

    @overload
    @staticmethod
    def range(start: int, stop: int) -> FrozenList[int]:
        ...

    @overload
    @staticmethod
    def range(start: int, stop: int, step: int) -> FrozenList[int]:
        ...

    @staticmethod
    def range(*args: int, **kw: int) -> FrozenList[int]:
        return range(*args, **kw)

    @staticmethod
    def singleton(item: _TSource) -> FrozenList[_TSource]:
        return singleton(item)

    def skip(self, count: int) -> FrozenList[_TSource]:
        """Returns the list after removing the first N elements.

        Args:
            count: The number of elements to skip.

        Returns:
            The list after removing the first N elements.
        """
        return FrozenList(self.value[count:])

    def skip_last(self, count: int) -> FrozenList[_TSource]:
        return FrozenList(self.value[:-count])

    def tail(self) -> FrozenList[_TSource]:
        """Return tail of List."""

        _, *tail = self.value
        return FrozenList(tail)

    def sort(
        self: FrozenList[_TSourceSortable], reverse: bool = False
    ) -> FrozenList[_TSourceSortable]:
        """Sort list directly.

        Returns a new sorted collection.

        Args:
            reverse: Sort in reversed order.

        Returns:
            A sorted list.
        """
        return FrozenList(builtins.sorted(self.value, reverse=reverse))

    def sort_with(
        self, func: Callable[[_TSource], Any], reverse: bool = False
    ) -> FrozenList[_TSource]:
        """Sort list with supplied function.

        Returns a new sorted collection.

        Args:
            func: The function to extract a comparison key from each element in list.
            reverse: Sort in reversed order.

        Returns:
            A sorted list.
        """
        return FrozenList(builtins.sorted(self.value, key=func, reverse=reverse))

    def take(self, count: int) -> FrozenList[_TSource]:
        """Returns the first N elements of the list.

        Args:
            count: The number of items to take.

        Returns:
            The result list.
        """
        return FrozenList(self.value[:count])

    def take_last(self, count: int) -> FrozenList[_TSource]:
        """Returns a specified number of contiguous elements from the
        end of the list.

        Args:
            count: The number of items to take.

        Returns:
            The result list.
        """
        return FrozenList(self.value[-count:])

    def try_head(self) -> Option[_TSource]:
        """Returns the first element of the list, or None if the list is
        empty.
        """
        if self.value:
            value = cast("_TSource", self.value[0])
            return Some(value)

        return Nothing

    @staticmethod
    def unfold(
        generator: Callable[[_TState], Option[Tuple[_TSource, _TState]]], state: _TState
    ) -> FrozenList[_TSource]:
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

    def zip(self, other: FrozenList[_TResult]) -> FrozenList[Tuple[_TSource, _TResult]]:
        """Combines the two lists into a list of pairs. The two lists
        must have equal lengths. .

        Args:
            other: The second input list.

        Returns:
            A single list containing pairs of matching elements from the
            input lists.
        """
        return of_seq(builtins.zip(self.value, other.value))

    def __add__(self, other: FrozenList[_TSource]) -> FrozenList[_TSource]:
        return FrozenList(self.value + other.value)

    @overload
    def __getitem__(self, key: slice) -> FrozenList[_TSource]:
        ...

    @overload
    def __getitem__(self, key: int) -> _TSource:
        ...

    def __getitem__(self, key: Any) -> Any:
        return self.value[key]

    def __iter__(self) -> Iterator[_TSource]:
        return iter(self.value)

    def __eq__(self, o: Any) -> bool:
        return self.value == o

    def __len__(self) -> int:
        return len(self.value)

    def __match__(self, pattern: Any) -> Iterable[List[_TSource]]:
        if self == pattern:
            return [[val for val in self]]

        try:
            origin: Any = get_origin(pattern)
            if isinstance(self, origin or pattern):
                return [[val for val in self]]
        except TypeError:
            pass

        return []

    def __str__(self) -> str:
        return f"[{', '.join(self.map(str))}]"

    def __repr__(self) -> str:
        return str(self)


def append(
    source: FrozenList[_TSource],
) -> Callable[[FrozenList[_TSource]], FrozenList[_TSource]]:
    def _append(other: FrozenList[_TSource]) -> FrozenList[_TSource]:
        return source.append(other)

    return _append


def choose(
    chooser: Callable[[_TSource], Option[_TResult]]
) -> Callable[[FrozenList[_TSource]], FrozenList[_TResult]]:
    def _choose(source: FrozenList[_TSource]) -> FrozenList[_TResult]:
        return source.choose(chooser)

    return _choose


def collect(
    mapping: Callable[[_TSource], FrozenList[_TResult]]
) -> Callable[[FrozenList[_TSource]], FrozenList[_TResult]]:
    """For each element of the list, applies the given function.
    Concatenates all the results and return the combined list.

    Args:
        mapping: he function to transform each input element into
        a sublist to be concatenated.

    Returns:
        A partially applied collect function that takes the source
        list and returns the concatenation of the transformed sublists.
    """

    def _collect(source: FrozenList[_TSource]) -> FrozenList[_TResult]:
        """For each element of the list, applies the given function.
        Concatenates all the results and return the combined list.

        Args:
            source: The input list.

        Returns:
            The concatenation of the transformed sublists.
        """
        return source.collect(mapping)

    return _collect


def concat(sources: Iterable[FrozenList[_TSource]]) -> FrozenList[_TSource]:
    """Concatenate sequence of FrozenList's"""

    def reducer(
        t: FrozenList[_TSource], s: FrozenList[_TSource]
    ) -> FrozenList[_TSource]:
        return t.append(s)

    return pipe(sources, seq.fold(reducer, empty))


def cons(head: _TSource, tail: FrozenList[_TSource]) -> FrozenList[_TSource]:
    return FrozenList((head, *tail))


nil: FrozenList[Any] = FrozenList()
empty: FrozenList[Any] = nil
"""The empty list."""


def filter(
    predicate: Callable[[_TSource], bool]
) -> Callable[[FrozenList[_TSource]], FrozenList[_TSource]]:
    """Returns a new collection containing only the elements of the
    collection for which the given predicate returns `True`

    Args:
        predicate: The function to test the input elements.

    Returns:
        Partially applied filter function.
    """

    def _filter(source: FrozenList[_TSource]) -> FrozenList[_TSource]:
        """Returns a new collection containing only the elements of the
        collection for which the given predicate returns `True`

        Args:
            source: The input list.

        Returns:
            A list containing only the elements that satisfy the
            predicate.
        """
        return source.filter(predicate)

    return _filter


def fold(
    folder: Callable[[_TState, _TSource], _TState], state: _TState
) -> Callable[[FrozenList[_TSource]], _TState]:
    """Applies a function to each element of the collection, threading
    an accumulator argument through the computation. Take the second
    argument, and apply the function to it and the first element of the
    list. Then feed this result into the function along with the second
    element and so on. Return the final result. If the input function is
    f and the elements are i0...iN then computes f (... (f s i0) i1 ...)
    iN.

    Args:
        folder: The function to update the state given the input
            elements.

        state: The initial state.

    Returns:
        Partially applied fold function that takes the source list
        and returns the final state value.
    """

    def _fold(source: FrozenList[_TSource]) -> _TState:
        return source.fold(folder, state)

    return _fold


def forall(
    predicate: Callable[[_TSource], bool]
) -> Callable[[FrozenList[_TSource]], bool]:
    """Tests if all elements of the collection satisfy the given
    predicate.

    Args:
        predicate: The function to test the input elements.

    Returns:
        True if all of the elements satisfy the predicate.
    """

    def _forall(source: FrozenList[_TSource]) -> bool:
        return source.forall(predicate)

    return _forall


def head(source: FrozenList[_TSource]) -> _TSource:
    """Returns the first element of the list.

    Args:
        source: The input list.

    Returns:
        The first element of the list.

    Raises:
         ValueError: Thrown when the list is empty.
    """
    return source.head()


def indexed(source: FrozenList[_TSource]) -> FrozenList[Tuple[int, _TSource]]:
    """Returns a new list whose elements are the corresponding
    elements of the input list paired with the index (from 0)
    of each element.

    Returns:
        The list of indexed elements.
    """
    return source.indexed()


def item(index: int) -> Callable[[FrozenList[_TSource]], _TSource]:
    """Indexes into the list. The first element has index 0.

    Args:
        index: The index to retrieve.

    Returns:
        The value at the given index.
    """

    def _item(source: FrozenList[_TSource]) -> _TSource:
        return source.item(index)

    return _item


def is_empty(source: FrozenList[Any]) -> bool:
    """Returns `True` if the list is empty, `False` otherwise."""
    return source.is_empty()


def map(
    mapper: Callable[[_TSource], _TResult]
) -> Callable[[FrozenList[_TSource]], FrozenList[_TResult]]:
    """Map list.

    Builds a new collection whose elements are the results of applying
    the given function to each of the elements of the collection.

    Args:
        mapper: The function to transform elements from the input list.

    Returns:
        The list of transformed elements.
    """

    def _map(source: FrozenList[_TSource]) -> FrozenList[_TResult]:
        return source.map(mapper)

    return _map


@overload
def starmap(
    mapper: Callable[[_T1, _T2], _TResult]
) -> Callable[[FrozenList[Tuple[_T1, _T2]]], FrozenList[_TResult]]:
    ...


@overload
def starmap(
    mapper: Callable[[_T1, _T2, _T3], _TResult]
) -> Callable[[FrozenList[Tuple[_T1, _T2, _T3]]], FrozenList[_TResult]]:
    ...


@overload
def starmap(
    mapper: Callable[[_T1, _T2, _T3, _T4], _TResult]
) -> Callable[[FrozenList[Tuple[_T1, _T2, _T3, _T4]]], FrozenList[_TResult]]:
    ...


def starmap(
    mapper: Callable[..., Any]
) -> Callable[[FrozenList[Tuple[Any, ...]]], FrozenList[Any]]:
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
) -> Callable[[FrozenList[Tuple[_T1, _T2]]], FrozenList[_TResult]]:
    return starmap(mapper)


def map3(
    mapper: Callable[[_T1, _T2, _T3], _TResult]
) -> Callable[[FrozenList[Tuple[_T1, _T2, _T3]]], FrozenList[_TResult]]:
    return starmap(mapper)


def mapi(
    mapper: Callable[[int, _TSource], _TResult]
) -> Callable[[FrozenList[_TSource]], FrozenList[_TResult]]:
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

    def _mapi(source: FrozenList[_TSource]) -> FrozenList[_TResult]:
        return source.mapi(mapper)

    return _mapi


def of(*args: _TSource) -> FrozenList[_TSource]:
    """Create list from a number of arguments."""
    return FrozenList((*args,))


def of_seq(xs: Iterable[_TSource]) -> FrozenList[_TSource]:
    """Create list from iterable sequence."""
    return FrozenList((*xs,))


def of_option(option: Option[_TSource]) -> FrozenList[_TSource]:
    if isinstance(option, Some):
        return singleton(option.value)
    return empty


@overload
def range(stop: int) -> FrozenList[int]:
    ...


@overload
def range(start: int, stop: int) -> FrozenList[int]:
    ...


@overload
def range(start: int, stop: int, step: int) -> FrozenList[int]:
    ...


def range(*args: int, **kw: int) -> FrozenList[int]:
    return FrozenList((*builtins.range(*args, **kw),))


def singleton(value: _TSource) -> FrozenList[_TSource]:
    return FrozenList((value,))


def skip(count: int) -> Callable[[FrozenList[_TSource]], FrozenList[_TSource]]:
    """Returns the list after removing the first N elements.

    Args:
        count: The number of elements to skip.

    Returns:
        The list after removing the first N elements.
    """

    def _skip(source: FrozenList[_TSource]) -> FrozenList[_TSource]:
        return source.skip(count)

    return _skip


def skip_last(count: int) -> Callable[[FrozenList[_TSource]], FrozenList[_TSource]]:
    """Returns the list after removing the last N elements.

    Args:
        count: The number of elements to skip.

    Returns:
        The list after removing the last N elements.
    """

    def _skip_last(source: FrozenList[_TSource]) -> FrozenList[_TSource]:
        return source.skip_last(count)

    return _skip_last


def sort(
    reverse: bool = False,
) -> Callable[[FrozenList[_TSourceSortable]], FrozenList[_TSourceSortable]]:
    """Returns a new sorted collection

    Args:
        reverse: Sort in reversed order.

    Returns:
        Partially applied sort function.
    """

    def _sort(source: FrozenList[_TSourceSortable]) -> FrozenList[_TSourceSortable]:
        """Returns a new sorted collection

        Args:
            source: The input list.

        Returns:
            A sorted list.
        """
        return source.sort(reverse)

    return _sort


def sort_with(
    func: Callable[[_TSource], Any], reverse: bool = False
) -> Callable[[FrozenList[_TSource]], FrozenList[_TSource]]:
    """Returns a new collection sorted using "func" key function.

    Args:
        func: The function to extract a comparison key from each element in list.
        reverse: Sort in reversed order.

    Returns:
        Partially applied sort function.
    """

    def _sort_with(source: FrozenList[_TSource]) -> FrozenList[_TSource]:
        """Returns a new collection sorted using "func" key function.

        Args:
            source: The input list.

        Returns:
            A sorted list.
        """
        return source.sort_with(func, reverse)

    return _sort_with


def tail(source: FrozenList[_TSource]) -> FrozenList[_TSource]:
    return source.tail()


def take(count: int) -> Callable[[FrozenList[_TSource]], FrozenList[_TSource]]:
    """Returns the first N elements of the list.

    Args:
        count: The number of items to take.

    Returns:
        The result list.
    """

    def _take(source: FrozenList[_TSource]) -> FrozenList[_TSource]:
        return source.take(count)

    return _take


def take_last(count: int) -> Callable[[FrozenList[_TSource]], FrozenList[_TSource]]:
    """Returns a specified number of contiguous elements from the end of
    the list.

    Args:
        count: The number of items to take.

    Returns:
        The result list.
    """

    def _take(source: FrozenList[_TSource]) -> FrozenList[_TSource]:
        return source.take_last(count)

    return _take


def try_head(source: FrozenList[_TSource]) -> Option[_TSource]:
    """Try to get the first element from the list.

    Returns the first element of the list, or None if the list is empty.

    Args:
        source: The input list.

    Returns:
        The first element of the list or `Nothing`.
    """
    return source.try_head()


def unfold(
    generator: Callable[[_TState], Option[Tuple[_TSource, _TState]]]
) -> Callable[[_TState], FrozenList[_TSource]]:
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

    def _unfold(state: _TState) -> FrozenList[_TSource]:
        xs = pipe(state, seq.unfold(generator))
        return FrozenList(xs)

    return _unfold


def zip(
    other: FrozenList[_TResult],
) -> Callable[[FrozenList[_TSource]], FrozenList[Tuple[_TSource, _TResult]]]:
    """Combines the two lists into a list of pairs. The two lists
    must have equal lengths.

    Args:
        other: The second input list.

    Returns:
        Paritally applied zip function that takes the source list and
        returns s single list containing pairs of matching elements from
        the input lists.
    """

    def _zip(source: FrozenList[_TSource]) -> FrozenList[Tuple[_TSource, _TResult]]:
        """Combines the two lists into a list of pairs. The two lists
        must have equal lengths.

        Args:
            source: The source input list.

        Returns:
            A single list containing pairs of matching elements from the
            input lists.
        """
        return source.zip(other)

    return _zip


__all__ = [
    "FrozenList",
    "append",
    "choose",
    "collect",
    "concat",
    "empty",
    "filter",
    "fold",
    "head",
    "indexed",
    "item",
    "is_empty",
    "map",
    "mapi",
    "of_seq",
    "of_option",
    "singleton",
    "skip",
    "skip_last",
    "sort",
    "sort_with",
    "tail",
    "take",
    "take_last",
    "try_head",
    "unfold",
    "zip",
]
