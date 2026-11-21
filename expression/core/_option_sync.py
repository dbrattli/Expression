"""Private synchronous functional helpers for Option."""

from __future__ import annotations

import builtins
from collections.abc import Callable
from typing import TYPE_CHECKING, Never, TypeGuard, Unpack, overload

from typing_extensions import TypeVar

from .curry import curry_flip
from .option import NOTHING, Nothing, Option, Some


if TYPE_CHECKING:
    from expression.collections.seq import Seq
    from expression.core.result import Error, Ok, Result


_TEmpty = TypeVar("_TEmpty", default=Never)


def bind[TOption: Some[object] | Nothing, TSource](
    mapper: Callable[[TSource], TOption],
) -> Callable[[Option[TSource]], TOption | Nothing]:
    """Apply an option-returning function to a present value."""

    def apply(source: Option[TSource]) -> TOption | Nothing:
        return source.bind(mapper)

    return apply


class _DefaultValue[T1]:
    def __init__(self, value: T1) -> None:
        self._value = value

    @overload
    def __call__[TSource](self, source: Some[TSource]) -> TSource: ...

    @overload
    def __call__(self, source: Nothing) -> T1: ...

    def __call__[TSource](self, source: Option[TSource]) -> TSource | T1:
        return source.default_value(self._value)


def default_value[T1](value: T1) -> _DefaultValue[T1]:
    """Return an operation selecting the payload or a fallback value."""
    return _DefaultValue(value)


class _DefaultWith[T1]:
    def __init__(self, getter: Callable[[], T1]) -> None:
        self._getter = getter

    @overload
    def __call__[TSource](self, source: Some[TSource]) -> TSource: ...

    @overload
    def __call__(self, source: Nothing) -> T1: ...

    def __call__[TSource](self, source: Option[TSource]) -> TSource | T1:
        return source.default_with(self._getter)


def default_with[T1](getter: Callable[[], T1]) -> _DefaultWith[T1]:
    """Return an operation selecting the payload or evaluating a fallback."""
    return _DefaultWith(getter)


def is_none(option: Option[object]) -> TypeGuard[Nothing]:
    """Narrow an option to its empty case."""
    return isinstance(option, Nothing)


def is_some[TSource](option: Option[TSource]) -> TypeGuard[Some[TSource]]:
    """Narrow an option to its present case."""
    return isinstance(option, Some)


@curry_flip(1)
def map[TSource, TResult](option: Option[TSource], mapper: Callable[[TSource], TResult]) -> Option[TResult]:
    return option.map(mapper)


@curry_flip(2)
def map2[T1, T2, TResult](opt1: Option[T1], opt2: Option[T2], mapper: Callable[[T1, T2], TResult]) -> Option[TResult]:
    return opt1.map2(mapper, opt2)


@overload
def apply(function: Nothing) -> Callable[[Option[object]], Nothing]: ...


@overload
def apply[TSource, TResult](
    function: Option[Callable[[TSource], TResult]],
) -> Callable[[Option[TSource]], Option[TResult]]: ...


def apply[TSource, TResult](
    function: Option[Callable[[TSource], TResult]],
) -> Callable[[Option[TSource]], Option[TResult]]:
    """Apply an optional function to an optional value."""

    def apply(source: Option[TSource]) -> Option[TResult]:
        return source.apply(function)

    return apply


@curry_flip(1)
def starmap[*P, TResult](option: Option[tuple[*P]], mapper: Callable[[Unpack[P]], TResult]) -> Option[TResult]:
    return option.starmap(mapper)


def or_else[TSource, TResult](option: Option[TSource], if_none: Option[TResult]) -> Option[TSource | TResult]:
    """Return the first present option, allowing a different fallback type."""
    return option.or_else(if_none)


def to_list(option: Option[_TEmpty]) -> list[_TEmpty]:
    return option.to_list()


def to_seq(option: Option[_TEmpty]) -> Seq[_TEmpty]:
    from expression.collections.seq import Seq

    return Seq(option.to_list())


@overload
def to_optional[TSource](value: Some[TSource]) -> TSource: ...


@overload
def to_optional(value: Nothing) -> None: ...


def to_optional[TSource](value: Option[TSource]) -> TSource | None:
    """Erase the option wrapper, mapping Nothing to None."""
    return value.to_optional()


@overload
def of_optional(value: None) -> Nothing: ...


@overload
def of_optional[TSource](value: TSource | None) -> Option[TSource]: ...


def of_optional[TSource](value: TSource | None) -> Option[TSource]:
    """Wrap a value, treating None as absence."""
    return NOTHING if value is None else Some(value)


@overload
def of_obj(value: None) -> Nothing: ...


@overload
def of_obj[TSource](value: TSource | None) -> Option[TSource]: ...


def of_obj[TSource](value: TSource | None) -> Option[TSource]:
    """Wrap a value, treating None as absence."""
    return of_optional(value)


@overload
def of_result[TSource](result: Ok[TSource]) -> Some[TSource]: ...


@overload
def of_result(result: Error[object]) -> Nothing: ...


def of_result[TSource](result: Result[TSource, object]) -> Option[TSource]:
    """Keep the successful result payload, or return Nothing."""
    from expression.core.result import Ok

    return Some(result.ok) if isinstance(result, Ok) else NOTHING


@overload
def to_result[TSource](value: Some[TSource], error: object) -> Ok[TSource]: ...


@overload
def to_result[TError](value: Nothing, error: TError) -> Error[TError]: ...


def to_result[TSource, TError](value: Option[TSource], error: TError) -> Result[TSource, TError]:
    return value.to_result(error)


@overload
def to_result_with[TSource](value: Some[TSource], error: Callable[[], object]) -> Ok[TSource]: ...


@overload
def to_result_with[TError](value: Nothing, error: Callable[[], TError]) -> Error[TError]: ...


def to_result_with[TSource, TError](value: Option[TSource], error: Callable[[], TError]) -> Result[TSource, TError]:
    return value.to_result_with(error)


def model_dump(value: Option[object]) -> builtins.dict[str, object]:
    """Encode an option using its tagged wire representation."""
    return value.dict()


def default_arg[TSource, T1](value: Option[TSource], default_value: T1) -> TSource | T1:
    """Return the payload or an uncurried fallback value."""
    return value.default_value(default_value)
