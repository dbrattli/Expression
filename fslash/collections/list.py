from abc import abstractmethod
from typing import Iterable, Iterator, Sized, TypeVar, Callable, cast

from fslash.core import Option_, Some, Nothing, pipe
from . import seq as Seq

TSource = TypeVar("TSource")
TResult = TypeVar("TResult")
TState = TypeVar("TState")


class List(Iterable[TSource], Sized):
    """Immutable list type.

    This is not the most space efficient implementation of a list. If
    that is the goal then use the builin mutable list or array types
    instead. Use this list if you need an immutable list for prepend
    operations mostly (`O(1)`).
    """

    def pipe(self, *args):
        """Pipe list through the given functions."""
        return pipe(self, *args)


    @abstractmethod
    def append(self, other: "List[TSource]") -> "List[TSource]":
        raise NotImplementedError

    @abstractmethod
    def choose(sef, chooser: Callable[[TSource], Option_[TResult]]) -> "List[TResult]":
        raise NotImplementedError

    @abstractmethod
    def collect(self, mapping: Callable[[TSource], "List[TResult]"]) -> "List[TResult]":
        raise NotImplementedError

    @abstractmethod
    def cons(self, element: TSource) -> "List[TSource]":
        """Add element to front of List."""

        raise NotImplementedError

    @abstractmethod
    def filter(self, predicate: Callable[[TSource], bool]) -> "List[TSource]":
        raise NotImplementedError

    @abstractmethod
    def head(self) -> TSource:
        """Retrive first element in List."""

        raise NotImplementedError

    @abstractmethod
    def is_empty(self) -> bool:
        """Return `True` if list is empty."""

        raise NotImplementedError

    @abstractmethod
    def map(self, mapper: Callable[[TSource], TResult]) -> "List[TResult]":
        raise NotImplementedError

    @abstractmethod
    def tail(self) -> "List[TSource]":
        """Return tail of List."""

        raise NotImplementedError

    @abstractmethod
    def take(self, count: int) -> "List[TSource]":
        """Returns the first N elements of the list.

        Args:
            count: The number of items to take.

        Returns:
            The result list.
        """
        raise NotImplementedError

    @abstractmethod
    def try_head(self) -> Option_[TSource]:
        """Returns the first element of the list, or None if the list is
        empty.
        """
        raise NotImplementedError

    @abstractmethod
    def __iter__(self) -> Iterator:
        """Return iterator for List."""

        raise NotImplementedError

    @abstractmethod
    def __add__(self, other) -> "List[TSource]":
        """Append list with other list."""

        raise NotImplementedError

    @abstractmethod
    def __eq__(self, other) -> bool:
        """Return true if list equals other list."""

        raise NotImplementedError

    @abstractmethod
    def __len__(self) -> int:
        """Return length of List."""

        raise NotImplementedError


class Cons(List[TSource]):
    def __init__(self, head: TSource, tail: List[TSource]):
        self._value = (head, tail)

    def append(self, other: List[TSource]) -> List[TSource]:
        head, tail = self._value
        return Cons(head, tail.append(other))

    def choose(self, chooser: Callable[[TSource], Option_[TResult]]) -> List[TResult]:
        head, tail = self._value
        filtered: List[TResult] = tail.choose(chooser)
        return cast(List[TResult], of_option(chooser(head))).append(filtered)

    def collect(self, mapping: Callable[[TSource], List[TResult]]) -> List[TResult]:
        head, tail = self._value
        return mapping(head).append(tail.collect(mapping))

    def cons(self, element: TSource) -> List[TSource]:
        """Add element to front of List."""

        return Cons(element, self)

    def filter(self, predicate: Callable[[TSource], bool]) -> List[TSource]:
        head, tail = self._value

        filtered = tail.filter(predicate)
        return Cons(head, filtered) if predicate(head) else filtered

    def head(self) -> TSource:
        """Retrive first element in List."""

        head, _ = self._value
        return head

    def is_empty(self) -> bool:
        """Return `True` if list is empty."""
        return False

    def map(self, mapper: Callable[[TSource], TResult]) -> List[TResult]:
        head, tail = self._value
        return Cons(mapper(head), tail.map(mapper))

    def tail(self) -> List[TSource]:
        """Return tail of List."""

        _, tail = self._value
        return tail

    def take(self, count: int) -> "List[TSource]":
        """Returns the first N elements of the list.

        Args:
            count: The number of items to take.

        Returns:
            The result list.
        """

        if not count:
            return Nil
        head, tail = self._value
        return Cons(head, tail.take(count - 1))

    def try_head(self) -> Option_[TSource]:
        """Returns the first element of the list, or None if the list is
        empty.
        """

        head, _ = self._value
        return Some(head)

    def __add__(self, other) -> List[TSource]:
        """Append list with other list."""

        return self.append(other)

    def __eq__(self, other) -> bool:
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

        _, tail = self._value
        return 1 + len(tail)


class _Nil(List[TSource]):
    """The List Nil case class.

    Do not use. Use the singleton Nil instead.
    """

    def append(self, other: List[TSource]) -> List[TSource]:
        return other

    def choose(self, chooser: Callable[[TSource], Option_[TResult]]) -> List[TResult]:
        return Nil

    def collect(self, mapping: Callable[[TSource], List[TResult]]) -> List[TResult]:
        return Nil

    def is_empty(self) -> bool:
        """Return `True` if list is empty."""
        return True

    def cons(self, element: TSource) -> List[TSource]:
        """Add element to front of List."""

        return Cons(element, self)

    def filter(self, predicate: Callable[[TSource], bool]) -> List[TSource]:
        return Nil

    def head(self) -> TSource:
        """Retrive first element in List."""

        raise IndexError("List is empty")

    def map(self, mapping: Callable[[TSource], TResult]) -> List[TResult]:
        return Nil

    def tail(self) -> List[TSource]:
        """Return tail of List."""

        raise IndexError("List is empty")

    def take(self, count: int) -> "List[TSource]":
        """Returns the first N elements of the list.

        Args:
            count: The number of items to take.

        Returns:
            The result list.
        """
        return Nil

    def try_head(self) -> Option_[TSource]:
        """Returns the first element of the list, or None if the list is
        empty.
        """
        return Nothing

    def __add__(self, other) -> List[TSource]:
        """Append list with other list."""

        return other

    def __eq__(self, other) -> bool:
        """Return true if list equals other list."""

        return other is Nil

    def __iter__(self):
        while False:
            yield

    def __len__(self) -> int:
        """Return length of List."""

        return 0


Nil: _Nil = _Nil()


def append(source: List[TSource]) -> Callable[[List[TSource]], List[TSource]]:
    def _append(other: List[TSource]) -> List[TSource]:
        return source.append(other)

    return _append


def choose(sef, chooser: Callable[[TSource], Option_[TResult]]) -> Callable[[List[TSource]], List[TResult]]:
    def _choose(source: List[TSource]) -> List[TResult]:
        return source.choose(chooser)

    return _choose


def collect(mapping: Callable[[TSource], List[TResult]]) -> Callable[[List[TSource]], List[TResult]]:
    def _collect(source: List[TSource]) -> List[TResult]:
        return source.collect(mapping)

    return _collect


def concat(sources: Iterable[List[TSource]]) -> List[TSource]:
    def folder(xs: List[TSource], acc: List[TSource]) -> List[TSource]:
        return xs + acc

    return Seq.fold_back(folder, sources)(Nil)


empty = Nil


def filter(predicate: Callable[[TSource], bool]) -> Callable[[List[TSource]], List[TSource]]:
    def _filter(source: List[TSource]) -> List[TSource]:
        return source.filter(predicate)

    return _filter


def head(source: List[TSource]) -> TSource:
    return source.head()


def is_empty(source: List[TSource]) -> bool:
    return source.is_empty()


def map(mapper: Callable[[TSource], TResult]) -> Callable[[List[TSource]], List[TResult]]:
    def _map(source: List[TSource]) -> List[TResult]:
        return source.map(mapper)

    return _map


def of_seq(xs: Iterable[TSource]) -> List[TSource]:
    def folder(value: TSource, acc: List[TSource]) -> List[TSource]:
        return Cons(value, acc)

    return Seq.fold_back(folder, xs)(Nil)


def of_option(option: Option_[TSource]) -> List[TSource]:
    if isinstance(option, Some):
        return singleton(option.value)
    return empty


def singleton(value: TSource) -> List[TSource]:
    return Cons(value, Nil)


def tail(source: List[TSource]) -> List[TSource]:
    return source.tail()


def take(count: int) -> Callable[[List[TSource]], List[TSource]]:
    """Returns the first N elements of the list.

    Args:
        count: The number of items to take.

    Returns:
        The result list.
    """
    def _take(source: List[TSource]) -> List[TSource]:
        return source.take(count)

    return _take


def try_head(self) -> Callable[[List[TSource]], Option_[TSource]]:
    """Returns the first element of the list, or None if the list is
    empty.
    """
    def _try_head(source: List[TSource]) -> Option_[TSource]:
        return source.try_head()

    return _try_head


__all__ = [
    "List",
    "Cons",
    "Nil",
    "append",
    "choose",
    "collect",
    "concat",
    "empty",
    "filter",
    "head",
    "is_empty",
    "map",
    "of_seq",
    "of_option",
    "singleton",
    "tail",
]
