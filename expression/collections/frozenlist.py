"""Immutable list module.

NOTE: Should only be used for smaller lists, i.e less than 10K elements.

This is not the fastest or most space efficient implementation of a
list. If that is the goal then use the builin mutable list or array
types instead. Use this list if you need an immutable list for prepend
operations mostly (`O(1)`).

Example:
    >>> xs = Cons(5, Cons(4, Cons(3, Cons(2, Cons(1, Nil)))))
    >>> ys = empty.cons(1).cons(2).cons(3).cons(4).cons(5)
"""

import builtins
import sys
from abc import ABC, abstractmethod
from typing import Any, Callable, Iterable, Iterator, Optional, Sized, Tuple, TypeVar, Union, cast, overload

from expression.core.option import Nothing, Option, Some, pipe

from . import seq

TSource = TypeVar("TSource")
TResult = TypeVar("TResult")
TState = TypeVar("TState")
T1 = TypeVar("T1")
T2 = TypeVar("T2")
T3 = TypeVar("T3")
T4 = TypeVar("T4")


class FrozenList(Iterable[TSource], Sized, ABC):
    """Immutable list type.

    This is not the most space efficient implementation of a list. If
    that is the goal then use the builin mutable list or array types
    instead. Use this list if you need an immutable list for prepend
    operations mostly (`O(1)`).

    Example:
        >>> xs = Cons(5, Cons(4, Cons(3, Cons(2, Cons(1, Nil)))))
        >>> ys = empty.cons(1).cons(2).cons(3).cons(4).cons(5)
    """

    def match(self, *args: Any, **kw: Any) -> Any:
        from pampy import match  # type: ignore

        return match(self, *args, **kw)  # type: ignore

    @overload
    def pipe(self, __fn1: Callable[["FrozenList[TSource]"], TResult]) -> TResult:
        ...

    @overload
    def pipe(self, __fn1: Callable[["FrozenList[TSource]"], T1], __fn2: Callable[[T1], T2]) -> T2:
        ...

    @overload
    def pipe(
        self, __fn1: Callable[["FrozenList[TSource]"], T1], __fn2: Callable[[T1], T2], __fn3: Callable[[T2], T3]
    ) -> T3:
        ...

    @overload
    def pipe(
        self,
        __fn1: Callable[["FrozenList[TSource]"], T1],
        __fn2: Callable[[T1], T2],
        __fn3: Callable[[T2], T3],
        __fn4: Callable[[T3], T4],
    ) -> T4:
        ...

    def pipe(self, *args: Any) -> Any:
        """Pipe list through the given functions."""
        return pipe(self, *args)

    @abstractmethod
    def append(self, other: "FrozenList[TSource]") -> "FrozenList[TSource]":
        raise NotImplementedError

    @abstractmethod
    def choose(self, chooser: Callable[[TSource], Option[TResult]]) -> "FrozenList[TResult]":
        raise NotImplementedError

    @abstractmethod
    def collect(self, mapping: Callable[[TSource], "FrozenList[TResult]"]) -> "FrozenList[TResult]":
        raise NotImplementedError

    @abstractmethod
    def cons(self, element: TSource) -> "FrozenList[TSource]":
        """Add element to front of List."""

        raise NotImplementedError

    @abstractmethod
    def filter(self, predicate: Callable[[TSource], bool]) -> "FrozenList[TSource]":
        raise NotImplementedError

    @abstractmethod
    def head(self) -> TSource:
        """Returns the first element of the list.

        Args:
            source: The input list.

        Returns:
            The first element of the list.

        Raises:
            ValueError: Thrown when the list is empty.
        """

        raise NotImplementedError

    @abstractmethod
    def indexed(self, start: int = 0) -> "FrozenList[Tuple[int, TSource]]":
        """Returns a new list whose elements are the corresponding
        elements of the input list paired with the index (from `start`)
        of each element.

        Args:
            start: Optional index to start from. Defaults to 0.

        Returns:
            The list of indexed elements.
        """
        raise NotImplementedError

    @abstractmethod
    def item(self, index: int) -> TSource:
        """Indexes into the list. The first element has index 0.

        Args:
            index: The index to retrieve.

        Returns:
            The value at the given index.
        """
        raise NotImplementedError

    @abstractmethod
    def is_empty(self) -> bool:
        """Return `True` if list is empty."""

        raise NotImplementedError

    @abstractmethod
    def map(self, mapping: Callable[[TSource], TResult]) -> "FrozenList[TResult]":
        raise NotImplementedError

    @abstractmethod
    def skip(self, count: int) -> "FrozenList[TSource]":
        """Returns the list after removing the first N elements.

        Args:
            count: The number of elements to skip.

        Returns:
            The list after removing the first N elements.
        """
        raise NotImplementedError

    @abstractmethod
    def skip_last(self, count: int) -> "FrozenList[TSource]":
        raise NotImplementedError

    @abstractmethod
    def tail(self) -> "FrozenList[TSource]":
        """Return tail of List."""

        raise NotImplementedError

    @abstractmethod
    def take(self, count: int) -> "FrozenList[TSource]":
        """Returns the first N elements of the list.

        Args:
            count: The number of items to take.

        Returns:
            The result list.
        """
        raise NotImplementedError

    @abstractmethod
    def take_last(self, count: int) -> "FrozenList[TSource]":
        """Returns a specified number of contiguous elements from the
        end of the list.

        Args:
            count: The number of items to take.

        Returns:
            The result list.
        """
        raise NotImplementedError

    @abstractmethod
    def try_head(self) -> Option[TSource]:
        """Returns the first element of the list, or None if the list is
        empty.
        """
        raise NotImplementedError

    def slice(
        self, start: Optional[int] = None, stop: Optional[int] = None, step: Optional[int] = None
    ) -> "FrozenList[TSource]":
        """The slice operator.

        Slices the given list. It is basically a wrapper around the operators
        - skip
        - skip_last
        - take
        - take_last
        - filter_indexed

        The following diagram helps you remember how slices works with streams.

        Positive numbers are relative to the start of the events, while negative
        numbers are relative to the end (close) of the stream.

        ```py
            r---e---a---c---t---i---v---e---!
            0   1   2   3   4   5   6   7   8
           -8  -7  -6  -5  -4  -3  -2  -1   0
        ```

        Examples:
            >>> result = xs.slice(1, 10)
            >>> result = xs.slice(1, -2)
            >>> result = xs.slice(1, -1, 2)

        Args:
            source: Observable to slice

        Returns:
            A sliced list.
        """
        res = self

        _start: int = 0 if start is None else start
        _stop: int = sys.maxsize if stop is None else stop
        _step: int = 1 if step is None else step

        if _stop >= 0:
            try:
                res = res.take(_stop)
            except ValueError:
                res = res

        if _start > 0:
            try:
                res = res.skip(_start)
            except ValueError:
                res = cast(FrozenList[TSource], empty)

        elif _start < 0:
            try:
                res = res.take_last(-_start)
            except ValueError:
                res = cast(FrozenList[TSource], empty)

        if _stop < 0:
            try:
                res = res.skip_last(-_stop)
            except ValueError:
                res = cast(FrozenList[TSource], empty)

        if _step > 1:
            predicate: Callable[[Tuple[int, Any]], bool] = lambda t: t[0] % _step == 0
            res = res.indexed().filter(predicate)

        elif _step < 0:
            # Reversing events is not supported
            raise TypeError("Negative step not supported.")

        return res

    def zip(self, other: "FrozenList[TResult]") -> "FrozenList[Tuple[TSource, TResult]]":
        """Combines the two lists into a list of pairs. The two lists
        must have equal lengths. .

        Args:
            other: The second input list.

        Returns:
            A single list containing pairs of matching elements from the
            input lists.
        """
        raise NotImplementedError

    @abstractmethod
    def __iter__(self) -> Iterator[TSource]:
        """Return iterator for List."""

        raise NotImplementedError

    @abstractmethod
    def __add__(self, other: "FrozenList[TSource]") -> "FrozenList[TSource]":
        """Append list with other list."""

        raise NotImplementedError

    @abstractmethod
    def __eq__(self, other: Any) -> bool:
        """Return true if list equals other list."""

        raise NotImplementedError

    @abstractmethod
    def __len__(self) -> int:
        """Return length of List."""

        raise NotImplementedError

    @overload
    def __getitem__(self, key: builtins.slice) -> "FrozenList[TSource]":
        ...

    @overload
    def __getitem__(self, key: int) -> TSource:
        ...

    def __getitem__(self, key: Union[builtins.slice, int]) -> Union["FrozenList[TSource]", TSource]:
        """
        Pythonic version of `slice`.

        Slices the given list using Python slice notation. The arguments
        to slice are `start`, `stop` and `step` given within brackets
        `[]` and separated by the colons `:`.

        Examples:
            >>> result = source[1:10]
            >>> result = source[1:-2]
            >>> result = source[1:-1:2]

        Args:
            key: Slice object

        Returns:
            Sliced observable sequence.

        Raises:
            TypeError: If key is not of type :code:`int` or :code:`slice`
        """

        if isinstance(key, slice):
            start, stop, step = key.start, key.stop, key.step
            return self.slice(start, stop, step)
        else:
            return self.item(key)


class Cons(FrozenList[TSource]):
    def __init__(self, head: TSource, tail: FrozenList[TSource]):
        self._value = (head, tail)
        self._len = 1 + len(tail)

    def append(self, other: FrozenList[TSource]) -> FrozenList[TSource]:
        head, tail = self._value
        return Cons(head, tail.append(other))

    def choose(self, chooser: Callable[[TSource], Option[TResult]]) -> FrozenList[TResult]:
        head, tail = self._value
        filtered: FrozenList[TResult] = tail.choose(chooser)
        return of_option(chooser(head)).append(filtered)

    def collect(self, mapping: Callable[[TSource], FrozenList[TResult]]) -> FrozenList[TResult]:
        """For each element of the list, applies the given function.
        Concatenates all the results and return the combined list.

        Args:
            mapping: he function to transform each input element into
            a sublist to be concatenated.

        Returns:
            The concatenation of the transformed sublists.
        """
        head, tail = self._value
        return mapping(head).append(tail.collect(mapping))

    def cons(self, element: TSource) -> FrozenList[TSource]:
        """Add element to front of List."""

        return Cons(element, self)

    def filter(self, predicate: Callable[[TSource], bool]) -> FrozenList[TSource]:
        head, tail = self._value

        filtered = tail.filter(predicate)
        return Cons(head, filtered) if predicate(head) else filtered

    def head(self) -> TSource:
        """Returns the first element of the list.

        Args:
            source: The input list.

        Returns:
            The first element of the list.

        Raises:
            ValueError: Thrown when the list is empty.
        """

        head, _ = self._value
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
        head, tail = self._value
        return Cons((start, head), tail.indexed(start + 1))

    def item(self, index: int) -> TSource:
        """Indexes into the list. The first element has index 0.

        Args:
            index: The index to retrieve.

        Returns:
            The value at the given index.
        """
        head, tail = self._value

        return head if not index else tail.item(index - 1)

    def is_empty(self) -> bool:
        """Return `True` if list is empty."""
        return False

    def map(self, mapping: Callable[[TSource], TResult]) -> FrozenList[TResult]:
        head, tail = self._value
        return Cons(mapping(head), tail.map(mapping))

    def skip(self, count: int) -> "FrozenList[TSource]":
        """Returns the list after removing the first N elements."""
        if count == 0:
            return self

        if self._len < count:
            raise ValueError(f"Not enough values to skip (expected at least {count}, got {self._len})")

        _, tail = self._value

        return tail.skip(count - 1)

    def skip_last(self, count: int) -> "FrozenList[TSource]":
        """Returns the list after removing the last N elements."""
        if count == 0:
            return self

        head, tail = self._value
        queue = tail if tail is Nil else tail.skip_last(count)
        return Cons(head, queue) if len(tail) >= count else queue

    def tail(self) -> FrozenList[TSource]:
        """Return tail of List."""

        _, tail = self._value
        return tail

    def take(self, count: int) -> "FrozenList[TSource]":
        """Returns the first N elements of the list.

        Args:
            count: The number of items to take.

        Returns:
            The result list.
        """

        if not count:
            return Nil

        if self._len < count:
            raise ValueError(f"Not enough values to take (expected at least {count}, got {self._len})")

        head, tail = self._value
        tail_ = tail.take(count - 1)
        return Cons(head, tail_)

    def take_last(self, count: int) -> "FrozenList[TSource]":
        """Returns a specified number of contiguous elements from the
        end of the list.

        Args:
            count: The number of items to take.

        Returns:
            The result list.
        """
        if not count:
            return Nil

        head, tail = self._value
        queue = tail if tail is Nil else tail.take_last(count)
        return Cons(head, queue) if len(queue) < count else queue

    def try_head(self) -> Option[TSource]:
        """Returns the first element of the list, or None if the list is
        empty.
        """

        head, _ = self._value
        return Some(head)

    def zip(self, other: FrozenList[TResult]) -> FrozenList[Tuple[TSource, TResult]]:
        """Combines the two lists into a list of pairs. The two lists
        must have equal lengths.

        Args:
            other: The second input list.

        Returns:
            A single list containing pairs of matching elements from the
            input lists.
        """
        if other is Nil:
            raise ValueError("The list must have equal length.")

        head, tail = self._value
        head_, tail_ = other.head(), other.tail()

        return Cons((head, head_), tail.zip(tail_))

    def __add__(self, other: FrozenList[TSource]) -> FrozenList[TSource]:
        """Append list with other list."""

        return self.append(other)

    def __eq__(self, other: Any) -> bool:
        """Return true if list equals other list."""

        if other is Nil:
            return False

        head, tail = self._value
        return head == other.head() and tail == other.tail()

    def __iter__(self):
        head, tail = self._value
        yield head
        yield from tail

    def __len__(self) -> int:
        """Return length of List."""

        return self._len


class _Nil(FrozenList[TSource]):
    """The List Nil case class.

    Do not use. Use the singleton Nil instead.
    """

    def append(self, other: FrozenList[TSource]) -> FrozenList[TSource]:
        return other

    def choose(self, chooser: Callable[[TSource], Option[TResult]]) -> FrozenList[TResult]:
        return Nil

    def collect(self, mapping: Callable[[TSource], FrozenList[TResult]]) -> FrozenList[TResult]:
        """For each element of the list, applies the given function.
        Concatenates all the results and return the combined list.

        Args:
            mapping: he function to transform each input element into
            a sublist to be concatenated.

        Returns:
            The concatenation of the transformed sublists.
        """
        return Nil

    def cons(self, element: TSource) -> FrozenList[TSource]:
        """Add element to front of List."""

        return Cons(element, self)

    def filter(self, predicate: Callable[[TSource], bool]) -> FrozenList[TSource]:
        return Nil

    def head(self) -> TSource:
        """Returns the first element of the list.

        Args:
            source: The input list.

        Returns:
            The first element of the list.

        Raises:
            ValueError: Thrown when the list is empty.
        """

        raise ValueError("List is empty")

    def indexed(self, start: int = 0) -> FrozenList[Tuple[int, TSource]]:
        """Returns a new list whose elements are the corresponding
        elements of the input list paired with the index (from `start`)
        of each element.

        Args:
            start: Optional index to start from. Defaults to 0.

        Returns:
            The list of indexed elements.
        """
        return Nil

    def item(self, index: int) -> TSource:
        """Indexes into the list. The first element has index 0.

        Args:
            index: The index to retrieve.

        Returns:
            The value at the given index.
        """

        raise IndexError("list index out of range")

    def is_empty(self) -> bool:
        """Return `True` if list is empty."""
        return True

    def map(self, mapping: Callable[[TSource], TResult]) -> FrozenList[TResult]:
        return Nil

    def skip(self, count: int) -> "FrozenList[TSource]":
        """Returns the list after removing the first N elements.

        Args:
            count: The number of elements to skip.

        Returns:
            The list after removing the first N elements.

        Raises:
            ValueError if the list is empty.
        """
        if count == 0:
            return self

        raise ValueError("Not enough values to skip.")

    def skip_last(self, count: int) -> "FrozenList[TSource]":
        if count == 0:
            return self

        raise ValueError("Not enough values to skip.")

    def tail(self) -> FrozenList[TSource]:
        """Return tail of List."""

        raise IndexError("List is empty")

    def take(self, count: int) -> "FrozenList[TSource]":
        """Returns the first N elements of the list.

        Args:
            count: The number of items to take.

        Returns:
            The result list.

        Raises:
            ValueError if the list is empty.
        """
        if not count:
            return Nil
        raise ValueError("Not enough values to take.")

    def take_last(self, count: int) -> "FrozenList[TSource]":
        """Returns a specified number of contiguous elements from the
        end of the list.

        Args:
            count: The number of items to take.

        Returns:
            The result list.

        Raises:
            ValueError if the list is empty.
        """
        if not count:
            return Nil
        raise ValueError("Not enough values to take.")

    def try_head(self) -> Option[TSource]:
        """Returns the first element of the list, or None if the list is
        empty.
        """
        return Nothing

    def zip(self, other: FrozenList[TResult]) -> FrozenList[Tuple[TSource, TResult]]:
        """Combines the two lists into a list of pairs. The two lists
        must have equal lengths.

        Args:
            other: The second input list.

        Returns:
            A single list containing pairs of matching elements from the
            input lists.

        Raises:
            ValueError if the list is empty.
        """
        if other is Nil:
            return Nil

        raise ValueError("The list must have equal length.")

    def __add__(self, other: FrozenList[TSource]) -> FrozenList[TSource]:
        """Append list with other list."""

        return other

    def __eq__(self, other: Any) -> bool:
        """Return true if list equals other list."""

        return other is Nil

    def __iter__(self):
        while False:
            yield

    def __len__(self) -> int:
        """Return length of List."""

        return 0


Nil: FrozenList[Any] = _Nil()


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
    def folder(xs: FrozenList[TSource], acc: FrozenList[TSource]) -> FrozenList[TSource]:
        return xs + acc

    return seq.fold_back(folder, sources)(Nil)


empty: FrozenList[Any] = Nil
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
            source: The input list..

        Returns:
            A list containing only the elements that satisfy the predicate.
        """
        return source.filter(predicate)

    return _filter


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

    def _(source: FrozenList[TSource]) -> TSource:
        return source.item(index)

    return _


def is_empty(source: FrozenList[TSource]) -> bool:
    """Returns `True` if the list is empty, `False` otherwise."""
    return source.is_empty()


def map(mapper: Callable[[TSource], TResult]) -> Callable[[FrozenList[TSource]], FrozenList[TResult]]:
    def _map(source: FrozenList[TSource]) -> FrozenList[TResult]:
        return source.map(mapper)

    return _map


def of_seq(xs: Iterable[TSource]) -> FrozenList[TSource]:
    def folder(value: TSource, acc: FrozenList[TSource]) -> FrozenList[TSource]:
        return Cons(value, acc)

    return seq.fold_back(folder, xs)(Nil)


def of_option(option: Option[TSource]) -> FrozenList[TSource]:
    if isinstance(option, Some):
        return singleton(cast(Some[TSource], option).value)
    return empty


def singleton(value: TSource) -> FrozenList[TSource]:
    return Cons(value, Nil)


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
    return source.try_head()


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
    "Cons",
    "Nil",
    "append",
    "choose",
    "collect",
    "concat",
    "empty",
    "filter",
    "head",
    "indexed",
    "item",
    "is_empty",
    "map",
    "of_seq",
    "of_option",
    "singleton",
    "skip",
    "skip_last",
    "tail",
    "take",
    "take_last",
    "try_head",
    "zip",
]
