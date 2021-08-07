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

TSource = TypeVar("TSource")
TSourceSortable = TypeVar("TSourceSortable", bound=SupportsLessThan)
TSourceIn = TypeVar("TSourceIn", contravariant=True)
TResult = TypeVar("TResult")
TResultOut = TypeVar("TResultOut", covariant=True)
TState = TypeVar("TState")

T1 = TypeVar("T1")
T2 = TypeVar("T2")
T3 = TypeVar("T3")
T4 = TypeVar("T4")
T5 = TypeVar("T5")
T6 = TypeVar("T6")


class FrozenList(Generic[TSource]):
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

    def __init__(self, value: Optional[Iterable[TSource]] = None) -> None:
        # Use composition instead of inheritance since generic tuples
        # are not suppored by mypy.
        self.value: Tuple[TSource, ...] = tuple(value) if value else tuple()

    def match(self, pattern: Any) -> Any:
        case: Case[TSource] = Case(self)
        return case(pattern) if pattern else case

    @overload
    def pipe(self, __fn1: Callable[[FrozenList[TSource]], TResult]) -> TResult:
        ...

    @overload
    def pipe(self, __fn1: Callable[[FrozenList[TSource]], T1], __fn2: Callable[[T1], T2]) -> T2:
        ...

    @overload
    def pipe(
        self, __fn1: Callable[[FrozenList[TSource]], T1], __fn2: Callable[[T1], T2], __fn3: Callable[[T2], T3]
    ) -> T3:
        ...

    @overload
    def pipe(
        self,
        __fn1: Callable[[FrozenList[TSource]], T1],
        __fn2: Callable[[T1], T2],
        __fn3: Callable[[T2], T3],
        __fn4: Callable[[T3], T4],
    ) -> T4:
        ...

    @overload
    def pipe(
        self,
        __fn1: Callable[[FrozenList[TSource]], T1],
        __fn2: Callable[[T1], T2],
        __fn3: Callable[[T2], T3],
        __fn4: Callable[[T3], T4],
        __fn5: Callable[[T4], T5],
    ) -> T5:
        ...

    @overload
    def pipe(
        self,
        __fn1: Callable[[FrozenList[TSource]], T1],
        __fn2: Callable[[T1], T2],
        __fn3: Callable[[T2], T3],
        __fn4: Callable[[T3], T4],
        __fn5: Callable[[T4], T5],
        __fn6: Callable[[T5], T6],
    ) -> T6:
        ...

    def pipe(self, *args: Any) -> Any:
        """Pipe list through the given functions."""
        return pipe(self, *args)

    def append(self, other: FrozenList[TSource]) -> FrozenList[TSource]:
        """Append frozen list to end of the frozen list."""

        return FrozenList(self.value + other.value)

    def choose(self, chooser: Callable[[TSource], Option[TResult]]) -> FrozenList[TResult]:
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

        def mapper(x: TSource) -> FrozenList[TResult]:
            return FrozenList(chooser(x).to_seq())

        return self.collect(mapper)

    def collect(self, mapping: Callable[[TSource], FrozenList[TResult]]) -> FrozenList[TResult]:
        mapped = builtins.map(mapping, self.value)
        xs = (y for x in mapped for y in x)
        return FrozenList(xs)

    def cons(self, element: TSource) -> FrozenList[TSource]:
        """Add element to front of list."""

        return FrozenList((element,) + self.value)  # NOTE: Faster than (element, *self)

    @staticmethod
    def empty() -> FrozenList[TSource]:
        """Returns empty list."""

        return FrozenList()

    def filter(self, predicate: Callable[[TSource], bool]) -> FrozenList[TSource]:
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

    def fold(self, folder: Callable[[TState, TSource], TState], state: TState) -> TState:
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

    def forall(self, predicate: Callable[[TSource], bool]) -> bool:
        """Tests if all elements of the collection satisfy the given
        predicate.

        Args:
            predicate: The function to test the input elements.

        Returns:
            True if all of the elements satisfy the predicate.
        """
        return all(predicate(x) for x in self)

    def head(self) -> TSource:
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

    def indexed(self, start: int = 0) -> FrozenList[Tuple[int, TSource]]:
        """Returns a new list whose elements are the corresponding
        elements of the input list paired with the index (from `start`)
        of each element.

        Args:
            start: Optional index to start from. Defaults to 0.

        Returns:
            The list of indexed elements.
        """
        return of_seq(enumerate(self))

    def item(self, index: int) -> TSource:
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

    def map(self, mapping: Callable[[TSource], TResult]) -> FrozenList[TResult]:
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

    def mapi(self, mapping: Callable[[int, TSource], TResult]) -> FrozenList[TResult]:
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
    def of(*args: TSource) -> FrozenList[TSource]:
        """Create list from a number of arguments."""
        return FrozenList((*args,))

    @staticmethod
    def of_seq(xs: Iterable[TSource]) -> FrozenList[TSource]:
        """Create list from iterable sequence."""
        return FrozenList((*xs,))

    @staticmethod
    def of_option(option: Option[TSource]) -> FrozenList[TSource]:
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
    def singleton(item: TSource) -> FrozenList[TSource]:
        return singleton(item)

    def skip(self, count: int) -> FrozenList[TSource]:
        """Returns the list after removing the first N elements.

        Args:
            count: The number of elements to skip.

        Returns:
            The list after removing the first N elements.
        """
        return FrozenList(self.value[count:])

    def skip_last(self, count: int) -> FrozenList[TSource]:
        return FrozenList(self.value[:-count])

    def tail(self) -> FrozenList[TSource]:
        """Return tail of List."""

        _, *tail = self.value
        return FrozenList(tail)

    def sort(self: FrozenList[TSourceSortable], reverse: bool = False) -> FrozenList[TSourceSortable]:
        """Sort list directly.

        Returns a new sorted collection.

        Args:
            reverse: Sort in reversed order.

        Returns:
            A sorted list.
        """
        return FrozenList(builtins.sorted(self.value, reverse=reverse))

    def sort_with(self, func: Callable[[TSource], Any], reverse: bool = False) -> FrozenList[TSource]:
        """Sort list with supplied function.

        Returns a new sorted collection.

        Args:
            func: The function to extract a comparison key from each element in list.
            reverse: Sort in reversed order.

        Returns:
            A sorted list.
        """
        return FrozenList(builtins.sorted(self.value, key=func, reverse=reverse))

    def take(self, count: int) -> FrozenList[TSource]:
        """Returns the first N elements of the list.

        Args:
            count: The number of items to take.

        Returns:
            The result list.
        """
        return FrozenList(self.value[:count])

    def take_last(self, count: int) -> FrozenList[TSource]:
        """Returns a specified number of contiguous elements from the
        end of the list.

        Args:
            count: The number of items to take.

        Returns:
            The result list.
        """
        return FrozenList(self.value[-count:])

    def try_head(self) -> Option[TSource]:
        """Returns the first element of the list, or None if the list is
        empty.
        """
        if self.value:
            value = cast("TSource", self.value[0])
            return Some(value)

        return Nothing

    @staticmethod
    def unfold(generator: Callable[[TState], Option[Tuple[TSource, TState]]], state: TState) -> FrozenList[TSource]:
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

    def zip(self, other: FrozenList[TResult]) -> FrozenList[Tuple[TSource, TResult]]:
        """Combines the two lists into a list of pairs. The two lists
        must have equal lengths. .

        Args:
            other: The second input list.

        Returns:
            A single list containing pairs of matching elements from the
            input lists.
        """
        return of_seq(builtins.zip(self.value, other.value))

    def __add__(self, other: FrozenList[TSource]) -> FrozenList[TSource]:
        return FrozenList(self.value + other.value)

    @overload
    def __getitem__(self, key: slice) -> FrozenList[TSource]:
        ...

    @overload
    def __getitem__(self, key: int) -> TSource:
        ...

    def __getitem__(self, key: Any) -> Any:
        return self.value[key]

    def __iter__(self) -> Iterator[TSource]:
        return iter(self.value)

    def __eq__(self, o: Any) -> bool:
        return self.value == o

    def __len__(self) -> int:
        return len(self.value)

    def __match__(self, pattern: Any) -> Iterable[List[TSource]]:
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


def append(source: FrozenList[TSource]) -> Callable[[FrozenList[TSource]], FrozenList[TSource]]:
    def _append(other: FrozenList[TSource]) -> FrozenList[TSource]:
        return source.append(other)

    return _append


def choose(chooser: Callable[[TSource], Option[TResult]]) -> Callable[[FrozenList[TSource]], FrozenList[TResult]]:
    def _choose(source: FrozenList[TSource]) -> FrozenList[TResult]:
        return source.choose(chooser)

    return _choose


def collect(mapping: Callable[[TSource], FrozenList[TResult]]) -> Callable[[FrozenList[TSource]], FrozenList[TResult]]:
    """For each element of the list, applies the given function.
    Concatenates all the results and return the combined list.

    Args:
        mapping: he function to transform each input element into
        a sublist to be concatenated.

    Returns:
        A partially applied collect function that takes the source
        list and returns the concatenation of the transformed sublists.
    """

    def _collect(source: FrozenList[TSource]) -> FrozenList[TResult]:
        """For each element of the list, applies the given function.
        Concatenates all the results and return the combined list.

        Args:
            source: The input list.

        Returns:
            The concatenation of the transformed sublists.
        """
        return source.collect(mapping)

    return _collect


def concat(sources: Iterable[FrozenList[TSource]]) -> FrozenList[TSource]:
    """Concatenate sequence of FrozenList's"""

    def reducer(t: FrozenList[TSource], s: FrozenList[TSource]) -> FrozenList[TSource]:
        return t.append(s)

    return pipe(sources, seq.fold(reducer, empty))


def cons(head: TSource, tail: FrozenList[TSource]) -> FrozenList[TSource]:
    return FrozenList((head, *tail))


nil: FrozenList[Any] = FrozenList()
empty: FrozenList[Any] = nil
"""The empty list."""


def filter(predicate: Callable[[TSource], bool]) -> Callable[[FrozenList[TSource]], FrozenList[TSource]]:
    """Returns a new collection containing only the elements of the
    collection for which the given predicate returns `True`

    Args:
        predicate: The function to test the input elements.

    Returns:
        Partially applied filter function.
    """

    def _filter(source: FrozenList[TSource]) -> FrozenList[TSource]:
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


def fold(folder: Callable[[TState, TSource], TState], state: TState) -> Callable[[FrozenList[TSource]], TState]:
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

    def _fold(source: FrozenList[TSource]) -> TState:
        return source.fold(folder, state)

    return _fold


def forall(predicate: Callable[[TSource], bool]) -> Callable[[FrozenList[TSource]], bool]:
    """Tests if all elements of the collection satisfy the given
    predicate.

    Args:
        predicate: The function to test the input elements.

    Returns:
        True if all of the elements satisfy the predicate.
    """

    def _forall(source: FrozenList[TSource]) -> bool:
        return source.forall(predicate)

    return _forall


def head(source: FrozenList[TSource]) -> TSource:
    """Returns the first element of the list.

    Args:
        source: The input list.

    Returns:
        The first element of the list.

    Raises:
         ValueError: Thrown when the list is empty.
    """
    return source.head()


def indexed(source: FrozenList[TSource]) -> FrozenList[Tuple[int, TSource]]:
    """Returns a new list whose elements are the corresponding
    elements of the input list paired with the index (from 0)
    of each element.

    Returns:
        The list of indexed elements.
    """
    return source.indexed()


def item(index: int) -> Callable[[FrozenList[TSource]], TSource]:
    """Indexes into the list. The first element has index 0.

    Args:
        index: The index to retrieve.

    Returns:
        The value at the given index.
    """

    def _item(source: FrozenList[TSource]) -> TSource:
        return source.item(index)

    return _item


def is_empty(source: FrozenList[Any]) -> bool:
    """Returns `True` if the list is empty, `False` otherwise."""
    return source.is_empty()


def map(mapper: Callable[[TSource], TResult]) -> Callable[[FrozenList[TSource]], FrozenList[TResult]]:
    """Map list.

    Builds a new collection whose elements are the results of applying
    the given function to each of the elements of the collection.

    Args:
        mapper: The function to transform elements from the input list.

    Returns:
        The list of transformed elements.
    """

    def _map(source: FrozenList[TSource]) -> FrozenList[TResult]:
        return source.map(mapper)

    return _map


def mapi(mapper: Callable[[int, TSource], TResult]) -> Callable[[FrozenList[TSource]], FrozenList[TResult]]:
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

    def _mapi(source: FrozenList[TSource]) -> FrozenList[TResult]:
        return source.mapi(mapper)

    return _mapi


def of(*args: TSource) -> FrozenList[TSource]:
    """Create list from a number of arguments."""
    return FrozenList((*args,))


def of_seq(xs: Iterable[TSource]) -> FrozenList[TSource]:
    """Create list from iterable sequence."""
    return FrozenList((*xs,))


def of_option(option: Option[TSource]) -> FrozenList[TSource]:
    if isinstance(option, Some):
        return singleton(cast(Some[TSource], option).value)
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


def singleton(value: TSource) -> FrozenList[TSource]:
    return FrozenList((value,))


def skip(count: int) -> Callable[[FrozenList[TSource]], FrozenList[TSource]]:
    """Returns the list after removing the first N elements.

    Args:
        count: The number of elements to skip.

    Returns:
        The list after removing the first N elements.
    """

    def _skip(source: FrozenList[TSource]) -> FrozenList[TSource]:
        return source.skip(count)

    return _skip


def skip_last(count: int) -> Callable[[FrozenList[TSource]], FrozenList[TSource]]:
    """Returns the list after removing the last N elements.

    Args:
        count: The number of elements to skip.

    Returns:
        The list after removing the last N elements.
    """

    def _skip_last(source: FrozenList[TSource]) -> FrozenList[TSource]:
        return source.skip_last(count)

    return _skip_last


def sort(reverse: bool = False) -> Callable[[FrozenList[TSourceSortable]], FrozenList[TSourceSortable]]:
    """Returns a new sorted collection

    Args:
        reverse: Sort in reversed order.

    Returns:
        Partially applied sort function.
    """

    def _sort(source: FrozenList[TSourceSortable]) -> FrozenList[TSourceSortable]:
        """Returns a new sorted collection

        Args:
            source: The input list.

        Returns:
            A sorted list.
        """
        return source.sort(reverse)

    return _sort


def sort_with(
    func: Callable[[TSource], Any], reverse: bool = False
) -> Callable[[FrozenList[TSource]], FrozenList[TSource]]:
    """Returns a new collection sorted using "func" key function.

    Args:
        func: The function to extract a comparison key from each element in list.
        reverse: Sort in reversed order.

    Returns:
        Partially applied sort function.
    """

    def _sort_with(source: FrozenList[TSource]) -> FrozenList[TSource]:
        """Returns a new collection sorted using "func" key function.

        Args:
            source: The input list.

        Returns:
            A sorted list.
        """
        return source.sort_with(func, reverse)

    return _sort_with


def tail(source: FrozenList[TSource]) -> FrozenList[TSource]:
    return source.tail()


def take(count: int) -> Callable[[FrozenList[TSource]], FrozenList[TSource]]:
    """Returns the first N elements of the list.

    Args:
        count: The number of items to take.

    Returns:
        The result list.
    """

    def _take(source: FrozenList[TSource]) -> FrozenList[TSource]:
        return source.take(count)

    return _take


def take_last(count: int) -> Callable[[FrozenList[TSource]], FrozenList[TSource]]:
    """Returns a specified number of contiguous elements from the end of
    the list.

    Args:
        count: The number of items to take.

    Returns:
        The result list.
    """

    def _take(source: FrozenList[TSource]) -> FrozenList[TSource]:
        return source.take_last(count)

    return _take


def try_head(source: FrozenList[TSource]) -> Option[TSource]:
    """Try to get the first element from the list.

    Returns the first element of the list, or None if the list is empty.

    Args:
        source: The input list.

    Returns:
        The first element of the list or `Nothing`.
    """
    return source.try_head()


def unfold(generator: Callable[[TState], Option[Tuple[TSource, TState]]]) -> Callable[[TState], FrozenList[TSource]]:
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

    def _unfold(state: TState) -> FrozenList[TSource]:
        xs = pipe(state, seq.unfold(generator))
        return FrozenList(xs)

    return _unfold


def zip(other: FrozenList[TResult]) -> Callable[[FrozenList[TSource]], FrozenList[Tuple[TSource, TResult]]]:
    """Combines the two lists into a list of pairs. The two lists
    must have equal lengths.

    Args:
        other: The second input list.

    Returns:
        Paritally applied zip function that takes the source list and
        returns s single list containing pairs of matching elements from
        the input lists.
    """

    def _zip(source: FrozenList[TSource]) -> FrozenList[Tuple[TSource, TResult]]:
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
