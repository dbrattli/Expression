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
from enum import Enum
from typing import (
    Any,
    Callable,
    Iterable,
    Iterator,
    List,
    Literal,
    MutableSequence,
    Optional,
    Tuple,
    TypeVar,
    Union,
    get_origin,
    overload,
)

from expression.core import MatchMixin, Option, Some, SupportsSum, pipe

_TSource = TypeVar("_TSource")
_TResult = TypeVar("_TResult")
_TState = TypeVar("_TState")

_TSourceSum = TypeVar("_TSourceSum", bound=SupportsSum)
_T1 = TypeVar("_T1")
_T2 = TypeVar("_T2")
_T3 = TypeVar("_T3")
_T4 = TypeVar("_T4")
_T5 = TypeVar("_T5")
_T6 = TypeVar("_T6")

_Array = Union[List[_TSource], MutableSequence[_TSource]]


class int8(int):
    ...


class int16(int):
    ...


class int32(int):
    ...


class int64(int):
    ...


class uint8(int):
    ...


class uint16(int):
    ...


class uint32(int):
    ...


class uint64(int):
    ...


class float32(float):
    ...


class float64(float):
    ...


class double(float):
    ...


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


def array_from_typecode(
    type_code: TypeCode, initializer: Optional[Iterable[Any]]
) -> _Array[Any]:
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
    initializer: Optional[Iterable[Any]] = None,
) -> Tuple[_Array[Any], TypeCode]:
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
        elif isinstance(arr0, (float64, double)):
            arr = array.array("d", arr)
            type_code = TypeCode.Double

    return arr, type_code


class TypedArray(MutableSequence[_TSource], MatchMixin[Iterable[_TSource]]):
    def __init__(
        self,
        initializer: Optional[Iterable[_TSource]] = None,
        type_code: Optional[TypeCode] = None,
    ) -> None:
        if type_code:
            arr = array_from_typecode(type_code, initializer)
        else:
            arr, type_code = array_from_initializer(initializer)

        self.value: _Array[Any] = arr
        self.type_code = type_code

    def map(self, mapping: Callable[[_TSource], _TResult]) -> TypedArray[_TResult]:
        # print("map1", self.value)
        result = builtins.map(mapping, self.value)
        # print("map1", result)
        return TypedArray(result)

    def choose(
        self, chooser: Callable[[_TSource], Option[_TResult]]
    ) -> TypedArray[_TResult]:
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

    def collect(
        self, mapping: Callable[[_TSource], TypedArray[_TResult]]
    ) -> TypedArray[_TResult]:
        mapped = builtins.map(mapping, self.value)
        xs = (y for x in mapped for y in x)
        return TypedArray(xs)

    def insert(self, index: int, value: _TSource) -> None:
        self.value.insert(index, value)

    def is_empty(self) -> bool:
        """Return `True` if list is empty."""

        return not self.value

    @property
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
        return TypedArray(
            builtins.filter(predicate, self.value), type_code=self.type_code
        )

    def fold(
        self, folder: Callable[[_TState, _TSource], _TState], state: _TState
    ) -> _TState:
        """Applies a function to each element of the array,
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

    @staticmethod
    def of(*args: _TSource) -> TypedArray[_TSource]:
        """Create list from a number of arguments."""
        return TypedArray((*args,))

    @staticmethod
    def of_seq(xs: Iterable[_TSource]) -> TypedArray[_TSource]:
        """Create list from iterable sequence."""
        return TypedArray((*xs,))

    @overload
    def pipe(self, __fn1: Callable[[TypedArray[_TSource]], _TResult]) -> _TResult:
        ...

    @overload
    def pipe(
        self, __fn1: Callable[[TypedArray[_TSource]], _T1], __fn2: Callable[[_T1], _T2]
    ) -> _T2:
        ...

    @overload
    def pipe(
        self,
        __fn1: Callable[[TypedArray[_TSource]], _T1],
        __fn2: Callable[[_T1], _T2],
        __fn3: Callable[[_T2], _T3],
    ) -> _T3:
        ...

    @overload
    def pipe(
        self,
        __fn1: Callable[[TypedArray[_TSource]], _T1],
        __fn2: Callable[[_T1], _T2],
        __fn3: Callable[[_T2], _T3],
        __fn4: Callable[[_T3], _T4],
    ) -> _T4:
        ...

    @overload
    def pipe(
        self,
        __fn1: Callable[[TypedArray[_TSource]], _T1],
        __fn2: Callable[[_T1], _T2],
        __fn3: Callable[[_T2], _T3],
        __fn4: Callable[[_T3], _T4],
        __fn5: Callable[[_T4], _T5],
    ) -> _T5:
        ...

    @overload
    def pipe(
        self,
        __fn1: Callable[[TypedArray[_TSource]], _T1],
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

    def __eq__(self, o: Any) -> bool:
        print("eq:", [self.value, o])
        if len(self) != len(o):
            return False

        for i, x in enumerate(self):
            if x != o[i]:
                return False
        return True

    def __len__(self) -> int:
        print([self.value])
        return len(self.value)

    def __iter__(self) -> Iterator[_TSource]:
        return iter(self.value)

    def __setitem__(self, key: int, value: _TSource) -> None:
        self.value[key] = value

    def __getitem__(self, key: Any) -> Any:
        return self.value[key]

    def __delitem__(self, key: int) -> None:
        del self.value[key]

    def __str__(self) -> str:
        return f"[|{', '.join(self.map(str))}|]"

    def __repr__(self) -> str:
        return str(self)


def map(
    mapper: Callable[[_TSource], _TResult]
) -> Callable[[TypedArray[_TSource]], TypedArray[_TResult]]:
    """Map array.

    Builds a new array whose elements are the results of applying
    the given function to each of the elements of the array.

    Args:
        mapper: The function to transform elements from the input array.

    Returns:
        The array of transformed elements.
    """

    def _map(source: TypedArray[_TSource]) -> TypedArray[_TResult]:
        return source.map(mapper)

    return _map


def sum(
    source: TypedArray[Union[_TSourceSum, Literal[0]]]
) -> Union[_TSourceSum, Literal[0]]:
    return builtins.sum(source.value)


def empty() -> TypedArray[Any]:
    return TypedArray()


def filter(
    predicate: Callable[[_TSource], bool]
) -> Callable[[TypedArray[_TSource]], TypedArray[_TSource]]:
    """Returns a new array containing only the elements of the
    array for which the given predicate returns `True`

    Args:
        predicate: The function to test the input elements.

    Returns:
        Partially applied filter function.
    """

    def _filter(source: TypedArray[_TSource]) -> TypedArray[_TSource]:
        """Returns a new array containing only the elements of the
        array for which the given predicate returns `True`

        Args:
            source: The input array.

        Returns:
            An array containing only the elements that satisfy the
            predicate.
        """
        return source.filter(predicate)

    return _filter


def fold(
    folder: Callable[[_TState, _TSource], _TState], state: _TState
) -> Callable[[TypedArray[_TSource]], _TState]:
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

    def _fold(source: TypedArray[_TSource]) -> _TState:
        return source.fold(folder, state)

    return _fold


def is_empty(source: TypedArray[Any]) -> bool:
    """Returns `True` if the list is empty, `False` otherwise."""
    return source.is_empty()


def of(*args: _TSource) -> TypedArray[_TSource]:
    """Create list from a number of arguments."""
    return TypedArray((*args,))


def of_seq(xs: Iterable[_TSource]) -> TypedArray[_TSource]:
    """Create list from iterable sequence."""
    return TypedArray((*xs,))


def of_option(option: Option[_TSource]) -> TypedArray[_TSource]:
    if isinstance(option, Some):
        return singleton(option.value)
    return empty()


def singleton(value: _TSource) -> TypedArray[_TSource]:
    return TypedArray((value,))


__all__ = [
    "TypedArray",
    "singleton",
    "of_option",
    "of_seq",
    "of",
    "is_empty",
    "empty",
    "sum",
    "map",
]
