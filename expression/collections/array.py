"""A typed array module.

This module provides an typed array type `TypedArray` and a set of
useful methods and functions for working with the array. The internal
backing storage is `bytearray`, `array.array` or `list` depending on
type of input.

"""

from __future__ import annotations

import array
import builtins
import functools
from collections.abc import Callable, Iterable, Iterator, MutableSequence
from enum import Enum
from typing import Any, TypeVar, cast

from expression.core import (
    Nothing,
    Option,
    PipeMixin,
    Some,
    SupportsLessThan,
    SupportsSum,
    curry_flip,
    pipe,
)

from . import seq


_TSource = TypeVar("_TSource")
_TResult = TypeVar("_TResult")
_TState = TypeVar("_TState")

_TSourceSortable = TypeVar("_TSourceSortable", bound=SupportsLessThan)

_TSourceSum = TypeVar("_TSourceSum", bound=SupportsSum)
_Array = list[_TSourceSum] | MutableSequence[_TSourceSum]


class int8(int): ...


class int16(int): ...


class int32(int): ...


class int64(int): ...


class uint8(int): ...


class uint16(int): ...


class uint32(int): ...


class uint64(int): ...


class float32(float): ...


class float64(float): ...


class double(float): ...


class TypeCode(Enum):
    Byte = "y"
    Int8 = "b"
    Int16 = "h"
    Int32 = "l"
    Int64 = "q"
    Uint8 = "B"
    Uint16 = "H"
    Uint32 = "L"
    Uint64 = "Q"
    Double = "d"
    Float = "f"
    # String = "s"
    Any = "a"


def array_from_typecode(type_code: TypeCode, initializer: Iterable[Any] | None) -> _Array[Any]:
    arr: _Array[Any] = list(initializer if initializer else [])
    if type_code == TypeCode.Byte:
        return bytearray(arr)
    elif type_code == TypeCode.Int8:
        return array.array("b", arr)
    elif type_code == TypeCode.Uint8:
        return array.array("B", arr)
    elif type_code == TypeCode.Int16:
        return array.array("h", arr)
    elif type_code == TypeCode.Uint16:
        return array.array("H", arr)
    elif type_code == TypeCode.Int32:
        return array.array("l", arr)
    elif type_code == TypeCode.Uint32:
        return array.array("L", arr)
    elif type_code == TypeCode.Int64:
        return array.array("q", arr)
    elif type_code == TypeCode.Uint64:
        return array.array("Q", arr)
    elif type_code == TypeCode.Float:
        return array.array("f", arr)
    elif type_code == TypeCode.Double:
        return array.array("d", arr)
    return arr


def array_from_initializer(
    initializer: Iterable[Any] | None = None,
) -> tuple[_Array[Any], TypeCode]:
    # Use list as the default array
    arr: _Array[Any] = list(initializer if initializer else [])
    type_code = TypeCode.Any

    if isinstance(initializer, bytearray):
        arr = initializer
        type_code = TypeCode.Byte
    elif isinstance(initializer, bytes):
        arr = bytearray(initializer)
        type_code = TypeCode.Byte
    elif arr:
        arr0 = arr[0]
        if isinstance(arr0, int8):
            arr = array.array("b", arr)
            type_code = TypeCode.Int8
        elif isinstance(arr0, int16):
            arr = array.array("h", arr)
            type_code = TypeCode.Int16
        elif isinstance(arr0, int32):
            arr = array.array("l", arr)
            type_code = TypeCode.Int32
        elif isinstance(arr0, int64):
            arr = array.array("l", arr)
            type_code = TypeCode.Int64
        elif isinstance(arr0, uint8):
            arr = array.array("B", arr)
            type_code = TypeCode.Uint8
        elif isinstance(arr0, uint16):
            arr = array.array("H", arr)
            type_code = TypeCode.Uint16
        elif isinstance(arr0, uint32):
            arr = array.array("L", arr)
            type_code = TypeCode.Uint32
        elif isinstance(arr0, uint64):
            arr = array.array("Q", arr)
            type_code = TypeCode.Uint64
        elif isinstance(arr0, float32):
            arr = array.array("f", arr)
            type_code = TypeCode.Float
        elif isinstance(arr0, float64 | double):
            arr = array.array("d", arr)
            type_code = TypeCode.Double

    return arr, type_code


class TypedArray(MutableSequence[_TSource], PipeMixin):
    __match_args__ = (
        "initializer",
        "typecode",
    )

    def __init__(
        self,
        initializer: Iterable[_TSource] | None = None,
        typecode: TypeCode | None = None,
    ) -> None:
        if typecode:
            arr = array_from_typecode(typecode, initializer)
        else:
            arr, typecode = array_from_initializer(initializer)

        self.value: _Array[Any] = arr
        self.typecode = typecode

    def map(self, mapping: Callable[[_TSource], _TResult]) -> TypedArray[_TResult]:
        result = builtins.map(mapping, self.value)
        return TypedArray(result)

    def choose(self, chooser: Callable[[_TSource], Option[_TResult]]) -> TypedArray[_TResult]:
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

        def mapper(x: _TSource) -> TypedArray[_TResult]:
            return TypedArray(chooser(x).to_seq())

        return self.collect(mapper)

    def collect(self, mapping: Callable[[_TSource], TypedArray[_TResult]]) -> TypedArray[_TResult]:
        mapped = builtins.map(mapping, self.value)
        xs = (y for x in mapped for y in x)
        return TypedArray(xs)

    def insert(self, index: int, value: _TSource) -> None:
        self.value.insert(index, value)

    def is_empty(self) -> bool:
        """Return `True` if list is empty."""
        return not self.value

    @classmethod
    def empty(cls) -> TypedArray[Any]:
        """Returns empty array."""
        return TypedArray()

    def filter(self, predicate: Callable[[_TSource], bool]) -> TypedArray[_TSource]:
        """Filter list.

        Returns a new collection containing only the elements of the
        collection for which the given predicate returns `True`.

        Args:
            predicate: The function to test the input elements.

        Returns:
            A list containing only the elements that satisfy the
            predicate.
        """
        return TypedArray(builtins.filter(predicate, self.value), typecode=self.typecode)

    def fold(self, folder: Callable[[_TState, _TSource], _TState], state: _TState) -> _TState:
        """Fold array.

        Applies a function to each element of the array,
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
        """Test all elements.

        Tests if all elements of the collection satisfy the given
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

    def indexed(self, start: int = 0) -> TypedArray[tuple[int, _TSource]]:
        """Index array elements.

        Returns a new array whose elements are the corresponding
        elements of the input array paired with the index (from `start`)
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
        return self.value[index]

    @staticmethod
    def of(*args: _TSource) -> TypedArray[_TSource]:
        """Create list from a number of arguments."""
        return TypedArray((*args,))

    @staticmethod
    def of_seq(xs: Iterable[_TSource]) -> TypedArray[_TSource]:
        """Create list from iterable sequence."""
        return TypedArray((*xs,))

    def skip(self, count: int) -> TypedArray[_TSource]:
        """Returns the array after removing the first N elements.

        Args:
            count: The number of elements to skip.

        Returns:
            The array after removing the first N elements.
        """
        return TypedArray(self.value[count:])

    def skip_last(self, count: int) -> TypedArray[_TSource]:
        return TypedArray(self.value[:-count])

    def sort(self: TypedArray[_TSourceSortable], reverse: bool = False) -> TypedArray[_TSourceSortable]:
        """Sort array directly.

        Returns a new sorted collection.

        Args:
            reverse: Sort in reversed order.

        Returns:
            A sorted array.
        """
        return TypedArray(builtins.sorted(self.value, reverse=reverse))

    def sort_with(self, func: Callable[[_TSource], Any], reverse: bool = False) -> TypedArray[_TSource]:
        """Sort array with supplied function.

        Returns a new sorted collection.

        Args:
            func: The function to extract a comparison key from each element in list.
            reverse: Sort in reversed order.

        Returns:
            A sorted array.
        """
        return TypedArray(builtins.sorted(self.value, key=func, reverse=reverse))

    def sum(self: TypedArray[_TSourceSum]) -> int:
        return sum(self)

    def sum_by(self, projection: Callable[[_TSource], _TSourceSum]) -> int:
        return pipe(
            self,
            sum_by(projection),
        )

    def tail(self) -> TypedArray[_TSource]:
        """Return tail of List."""
        _, *tail = self.value
        return TypedArray(tail)

    def take(self, count: int) -> TypedArray[_TSource]:
        """Returns the first N elements of the list.

        Args:
            count: The number of items to take.

        Returns:
            The result list.
        """
        return TypedArray(self.value[:count])

    def take_last(self, count: int) -> TypedArray[_TSource]:
        """Take last elements.

        Returns a specified number of contiguous elements from the
        end of the list.

        Args:
            count: The number of items to take.

        Returns:
            The result list.
        """
        return TypedArray(self.value[-count:])

    def try_head(self) -> Option[_TSource]:
        """Try to return first element.

        Returns the first element of the list, or None if the list is
        empty.
        """
        if self.value:
            value = cast("_TSource", self.value[0])
            return Some(value)

        return Nothing

    @staticmethod
    def unfold(
        generator: Callable[[_TState], Option[tuple[_TSource, _TState]]], state: _TState
    ) -> TypedArray[_TSource]:
        """Unfold array.

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

    def __eq__(self, o: Any) -> bool:
        if len(self) != len(o):
            return False

        for i, x in enumerate(self):
            if x != o[i]:
                return False
        return True

    def __len__(self) -> int:
        return len(self.value)

    def __iter__(self) -> Iterator[_TSource]:
        return iter(self.value)

    def __setitem__(self, key: slice | int, value: Any) -> None:
        self.value[key] = value

    def __getitem__(self, key: Any) -> Any:
        return self.value[key]

    def __delitem__(self, key: slice | int) -> None:
        del self.value[key]

    def __str__(self) -> str:
        return f"[|{', '.join(self.map(str))}|]"

    def __repr__(self) -> str:
        return str(self)


@curry_flip(1)
def map(source: TypedArray[_TSource], mapper: Callable[[_TSource], _TResult]) -> TypedArray[_TResult]:
    """Map array.

    Builds a new array whose elements are the results of applying
    the given function to each of the elements of the array.

    Args:
        source: The source array to map.
        mapper: The function to transform elements from the input array.

    Returns:
        A new array of transformed elements.
    """
    return source.map(mapper)


def empty() -> TypedArray[Any]:
    return TypedArray()


@curry_flip(1)
def filter(source: TypedArray[_TSource], predicate: Callable[[_TSource], bool]) -> TypedArray[_TSource]:
    """Filter array.

    Returns a new array containing only the elements of the
    array for which the given predicate returns `True`.

    Args:
        source: The source array to filter.
        predicate: The function to test the input elements.

    Returns:
        Partially applied filter function.
    """
    return source.filter(predicate)


@curry_flip(1)
def fold(
    source: TypedArray[_TSource],
    folder: Callable[[_TState, _TSource], _TState],
    state: _TState,
) -> _TState:
    """Fold the array.

    Applies a function to each element of the collection, threading
    an accumulator argument through the computation. Take the second
    argument, and apply the function to it and the first element of the
    list. Then feed this result into the function along with the second
    element and so on. Return the final result. If the input function is
    f and the elements are i0...iN then computes f (... (f s i0) i1 ...)
    iN.

    Args:
        source: The source array to fold.
        folder: The function to update the state given the input
            elements.

        state: The initial state.

    Returns:
        Partially applied fold function that takes the source list
        and returns the final state value.
    """
    return source.fold(folder, state)


@curry_flip(1)
def indexed(
    source: TypedArray[_TSource],
    start: int = 0,
) -> TypedArray[tuple[int, _TSource]]:
    return source.indexed()


def is_empty(source: TypedArray[Any]) -> bool:
    """Returns `True` if the list is empty, `False` otherwise."""
    return source.is_empty()


@curry_flip(1)
def item(source: TypedArray[_TSource], index: int) -> _TSource:
    return source.item(index)


def of(*args: _TSource) -> TypedArray[_TSource]:
    """Create list from a number of arguments."""
    return TypedArray((*args,))


def of_seq(xs: Iterable[_TSource]) -> TypedArray[_TSource]:
    """Create list from iterable sequence."""
    return TypedArray((*xs,))


def of_option(option: Option[_TSource]) -> TypedArray[_TSource]:
    match option:
        case Option(tag="some", some=value):
            return singleton(value)
        case _:
            return empty()


def singleton(value: _TSource) -> TypedArray[_TSource]:
    return TypedArray((value,))


def sum(source: TypedArray[_TSourceSum]) -> int:
    return builtins.sum(source.value)


@curry_flip(1)
def sum_by(source: TypedArray[_TSource], projection: Callable[[_TSource], _TSourceSum]) -> int:
    return builtins.sum(source.map(projection).value)


@curry_flip(1)
def take(source: TypedArray[_TSource], count: int) -> TypedArray[_TSource]:
    """Return the first N elements of the array.

    Args:
        source: The source array to take from.
        count: The number of items to take.

    Returns:
        The result array.
    """
    return source.take(count)


@curry_flip(1)
def take_last(source: TypedArray[_TSource], count: int) -> TypedArray[_TSource]:
    """Take last elements.

    Returns a specified number of contiguous elements from the end of
    the list.

    Args:
        source: The source array to take from.
        count: The number of items to take.

    Returns:
        The result list.
    """
    return source.take_last(count)


def try_head(source: TypedArray[_TSource]) -> Option[_TSource]:
    """Try to get the first element from the list.

    Returns the first element of the list, or None if the list is empty.

    Args:
        source: The input list.

    Returns:
        The first element of the list or `Nothing`.
    """
    return source.try_head()


@curry_flip(1)
def unfold(state: _TState, generator: Callable[[_TState], Option[tuple[_TSource, _TState]]]) -> TypedArray[_TSource]:
    """Unfold array.

    Returns a list that contains the elements generated by the
    given computation. The given initial state argument is passed to
    the element generator.

    Args:
        state: The initial state.
        generator: A function that takes in the current state and
            returns an option tuple of the next element of the list
            and the next state value.

    Returns:
        The result list.
    """
    xs = pipe(state, seq.unfold(generator))
    return TypedArray(xs)


__all__ = [
    "empty",
    "filter",
    "fold",
    "indexed",
    "is_empty",
    "item",
    "map",
    "of_option",
    "of_seq",
    "of",
    "sum",
    "sum_by",
    "singleton",
    "take",
    "take_last",
    "try_head",
    "TypedArray",
    "unfold",
]
