from abc import abstractmethod
from typing import Iterable, Iterator, Sized, TypeVar, Callable
from .seq import SeqModule as Seq

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

    @abstractmethod
    def append(self, other: 'List[TSource]') -> 'List[TSource]':
        raise NotImplementedError

    @abstractmethod
    def collect(self, mapping: Callable[[TSource], 'List[TResult]']) -> 'List[TResult]':
        raise NotImplementedError

    @abstractmethod
    def cons(self, element: TSource) -> 'List[TSource]':
        """Add element to front of List."""

        raise NotImplementedError

    @abstractmethod
    def head(self) -> TSource:
        """Retrive first element in List."""

        raise NotImplementedError

    @abstractmethod
    def tail(self) -> 'List[TSource]':
        """Return tail of List."""

        raise NotImplementedError

    @abstractmethod
    def is_empty(self) -> bool:
        """Return `True` if list is empty."""

        raise NotImplementedError

    @abstractmethod
    def map(self, mapper: Callable[[TSource], TResult]) -> 'List[TResult]':
        raise NotImplementedError

    @abstractmethod
    def __iter__(self) -> Iterator:
        """Return iterator for List."""

        raise NotImplementedError

    @abstractmethod
    def __add__(self, other) -> 'List[TSource]':
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

    def append(self, other: 'List[TSource]') -> 'List[TSource]':
        head, tail = self._value
        return Cons(head, tail.append(other))

    def collect(self, mapping: Callable[[TSource], 'List[TResult]']) -> 'List[TResult]':
        head, tail = self._value
        return mapping(head).append(tail.collect(mapping))

    def cons(self, element: TSource) -> 'List[TSource]':
        """Add element to front of List."""

        return Cons(element, self)

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

    def tail(self) -> 'List[TSource]':
        """Return tail of List."""

        _, tail = self._value
        return tail

    def __add__(self, other) -> 'List[TSource]':
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

    def append(self, other: 'List[TSource]') -> 'List[TSource]':
        return other

    def collect(self, mapping: Callable[[TSource], 'List[TResult]']) -> 'List[TResult]':
        return Nil

    def is_empty(self) -> bool:
        """Return `True` if list is empty."""
        return True

    def cons(self, element: TSource) -> 'List[TSource]':
        """Add element to front of List."""

        return Cons(element, self)

    def head(self) -> TSource:
        """Retrive first element in List."""

        raise IndexError("List is empty")

    def map(self, mapping: Callable[[TSource], TResult]) -> List[TResult]:
        return Nil

    def tail(self) -> 'List[TSource]':
        """Return tail of List."""

        raise IndexError("List is empty")

    def __add__(self, other) -> 'List[TSource]':
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


class ListModule:
    @staticmethod
    def append(source: 'List[TSource]') -> 'Callable[[List[TSource]], List[TSource]]':
        def _append(other: List[TSource]) -> List[TSource]:
            return source.append(other)
        return _append

    @staticmethod
    def collect(mapping: 'Callable[[TSource], List[TResult]]') -> 'Callable[[List[TSource]], List[TResult]]':
        def _collect(source: List[TSource]) -> List[TResult]:
            return source.collect(mapping)
        return _collect

    @staticmethod
    def concat(sources: 'Iterable[List[TSource]]') -> 'List[TSource]':
        def folder(xs: List[TSource], acc: List[TSource]) -> List[TSource]:
            return xs + acc
        return Seq.fold_back(folder, sources)(Nil)

    empty = Nil

    @staticmethod
    def head(source: List[TSource]) -> TSource:
        return source.head()

    @staticmethod
    def is_empty(source: List[TSource]) -> bool:
        return source.is_empty()

    @staticmethod
    def map(mapper: Callable[[TSource], TResult]) -> 'Callable[[List[TSource]], List[TResult]]':
        def _map(source: List[TSource]) -> List[TResult]:
            return source.map(mapper)
        return _map

    @staticmethod
    def of_seq(xs: Iterable[TSource]) -> 'List[TSource]':
        def folder(value: TSource, acc: List[TSource]) -> List[TSource]:
            return Cons(value, acc)
        return Seq.fold_back(folder, xs)(Nil)

    @staticmethod
    def singleton(value: TSource) -> 'List[TSource]':
        return Cons(value, Nil)

    @staticmethod
    def tail(source: List[TSource]) -> List[TSource]:
        return source.tail()


__all__ = ['ListModule', 'List', 'Cons', 'Nil']
