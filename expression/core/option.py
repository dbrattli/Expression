"""Closed optional values and pipe-friendly operations.

``Option[T]`` is the union of ``Some[T]`` and the singleton case ``Nothing``.
Match the case classes to access their payloads. Iteration and awaiting retain
the computation-expression protocol, including short-circuiting on Nothing.
"""

from __future__ import annotations

import builtins
from collections.abc import Callable, Generator
from typing import (
    TYPE_CHECKING,
    Annotated,
    ClassVar,
    Final,
    Generic,
    Literal,
    Never,
    TypeAlias,
    TypeGuard,
    final,
    overload,
)

from typing_extensions import TypeVar, TypeVarTuple, Unpack

from ._serialization import encode
from ._union_schema import UnionSchema
from .curry import curry_flip
from .error import EffectError
from .pipe import PipeMixin
from .tagged_union import case, tag


if TYPE_CHECKING:
    from expression.collections.seq import Seq
    from expression.core.result import Error, Ok, Result


_TSourceOut = TypeVar("_TSourceOut", covariant=True)
_TSource = TypeVar("_TSource")
_TResult = TypeVar("_TResult")
_TError = TypeVar("_TError")
_TEmpty = TypeVar("_TEmpty", default=Never)
_T1 = TypeVar("_T1")
_T2 = TypeVar("_T2")
_TOption = TypeVar("_TOption", bound="Some[object] | Nothing")
_P = TypeVarTuple("_P")


@final
@case
class Some(PipeMixin, Generic[_TSourceOut]):
    """An optional value that is present, including when its payload is None."""

    some: _TSourceOut
    tag: Literal["some"] = tag("some")

    def default_value(self, value: object) -> _TSourceOut:
        """Return the present value."""
        return self.some

    def default_with(self, getter: Callable[[], object]) -> _TSourceOut:
        """Return the present value without evaluating the fallback."""
        return self.some

    def map(self, mapper: Callable[[_TSourceOut], _TResult]) -> Some[_TResult]:
        """Transform the present value."""
        return Some(mapper(self.some))

    def map2(self, mapper: Callable[[_TSourceOut, _T2], _TResult], other: Option[_T2]) -> Option[_TResult]:
        """Transform two present values, or return Nothing."""
        return other.map(lambda value: mapper(self.some, value))

    def apply(self, function: Option[Callable[[_TSourceOut], _TResult]]) -> Option[_TResult]:
        """Apply an optional function to the present value."""
        return function.map(lambda mapper: mapper(self.some))

    def starmap(self: Some[tuple[*_P]], mapper: Callable[[Unpack[_P]], _TResult]) -> Some[_TResult]:
        """Apply a function to the unpacked tuple payload."""
        return Some(mapper(*self.some))

    def bind(self, mapper: Callable[[_TSourceOut], _TOption]) -> _TOption:
        """Apply a function returning another option."""
        return mapper(self.some)

    def or_else(self, if_none: Option[object]) -> Some[_TSourceOut]:
        """Keep the present value."""
        return self

    def or_else_with(self, if_none: Callable[[], Option[object]]) -> Some[_TSourceOut]:
        """Keep the present value without evaluating the fallback."""
        return self

    def filter(self, predicate: Callable[[_TSourceOut], bool]) -> Option[_TSourceOut]:
        """Keep the value when the predicate holds."""
        return self if predicate(self.some) else NOTHING

    def to_list(self) -> list[_TSourceOut]:
        """Return a one-element list."""
        return [self.some]

    def to_seq(self) -> Seq[_TSourceOut]:
        """Return a one-element sequence."""
        from expression.collections.seq import Seq

        return Seq.of(self.some)

    def is_some(self) -> bool:
        """Return True; use isinstance or the free guard for narrowing."""
        return True

    def is_none(self) -> bool:
        """Return False."""
        return False

    def to_optional(self) -> _TSourceOut:
        """Return the present value, erasing the option wrapper."""
        return self.some

    def to_result(self, error: object) -> Ok[_TSourceOut]:
        """Return the present value as a successful result."""
        from expression.core.result import Ok

        return Ok(self.some)

    def to_result_with(self, error: Callable[[], object]) -> Ok[_TSourceOut]:
        """Return a successful result without evaluating the error factory."""
        from expression.core.result import Ok

        return Ok(self.some)

    def dict(self) -> builtins.dict[str, object]:
        """Encode a tagged value, preserving None and nested option cases."""
        return {"tag": "some", "some": encode(self.some)}

    @property
    def value(self) -> _TSourceOut:
        """Return the payload; use matching when the case is not known."""
        return self.some

    def __iter__(self) -> Generator[_TSourceOut, _TSourceOut, _TSourceOut]:
        return (yield self.some)

    def __await__(self) -> Generator[_TSourceOut, _TSourceOut, _TSourceOut]:
        return self.some
        yield

    def __str__(self) -> str:
        return f"Some {self.some}"


@final
@case
class Nothing(PipeMixin):
    """The empty option case, constructed and matched as ``Nothing()``.

    Construction, copying, pickling, and Option decoding preserve one canonical
    instance. Use ``NOTHING`` to reuse it without calling the constructor.
    """

    tag: Literal["none"] = tag("none")
    _instance: ClassVar[Nothing | None] = None

    def __new__(cls) -> Nothing:
        if cls._instance is None:
            cls._instance = object.__new__(cls)
        return cls._instance

    def default_value(self, value: _TResult) -> _TResult:
        """Return the fallback value."""
        return value

    def default_with(self, getter: Callable[[], _TResult]) -> _TResult:
        """Evaluate the fallback factory."""
        return getter()

    def map(self, mapper: Callable[[Never], object]) -> Nothing:
        """Keep the empty option without evaluating the mapper."""
        return self

    def map2(self, mapper: Callable[[Never, _T2], object], other: Option[_T2]) -> Nothing:
        """Keep the empty option without evaluating the mapper."""
        return self

    def apply(self, function: Option[Callable[[Never], object]]) -> Nothing:
        """Keep the empty option without invoking the optional function."""
        return self

    def starmap(self, mapper: Callable[..., object]) -> Nothing:
        """Keep the empty option without evaluating the mapper."""
        return self

    def bind(self, mapper: Callable[[Never], _TOption]) -> Nothing:
        """Keep the empty option without evaluating the continuation."""
        return self

    def or_else(self, if_none: _TOption) -> _TOption:
        """Return the fallback option."""
        return if_none

    def or_else_with(self, if_none: Callable[[], _TOption]) -> _TOption:
        """Evaluate the fallback option factory."""
        return if_none()

    def filter(self, predicate: Callable[[Never], bool]) -> Nothing:
        """Keep the empty option without evaluating the predicate."""
        return self

    def to_list(self) -> list[_TEmpty]:
        """Return an empty list."""
        return []

    def to_seq(self) -> Seq[_TEmpty]:
        """Return an empty sequence."""
        from expression.collections.seq import Seq

        return Seq()

    def is_some(self) -> bool:
        """Return False."""
        return False

    def is_none(self) -> bool:
        """Return True; use isinstance or the free guard for narrowing."""
        return True

    def to_optional(self) -> None:
        """Return None."""
        return None

    def to_result(self, error: _TError) -> Error[_TError]:
        """Return the supplied error as a failed result."""
        from expression.core.result import Error

        return Error(error)

    def to_result_with(self, error: Callable[[], _TError]) -> Error[_TError]:
        """Evaluate the error factory and return a failed result."""
        from expression.core.result import Error

        return Error(error())

    def dict(self) -> builtins.dict[str, object]:
        """Encode the empty case with an explicit tag."""
        return {"tag": "none"}

    @property
    def value(self) -> Never:
        """Raise ValueError because this option has no payload."""
        raise ValueError("There is no value.")

    def __iter__(self) -> Generator[Never, object, Never]:
        raise EffectError(self)
        yield

    def __await__(self) -> Generator[Never, object, Never]:
        raise EffectError(self)
        yield

    def __str__(self) -> str:
        return "Nothing"


NOTHING: Final = Nothing()
"""The canonical empty option, available without a constructor call."""


Option: TypeAlias = Annotated[Some[_TSourceOut] | Nothing, UnionSchema(canonical_values=(NOTHING,))]


def bind(mapper: Callable[[_TSource], _TOption]) -> Callable[[Option[_TSource]], _TOption | Nothing]:
    """Apply an option-returning function to a present value."""

    def apply(source: Option[_TSource]) -> _TOption | Nothing:
        return source.bind(mapper)

    return apply


class _DefaultValue(Generic[_T1]):
    def __init__(self, value: _T1) -> None:
        self._value = value

    @overload
    def __call__(self, source: Some[_TSource]) -> _TSource: ...

    @overload
    def __call__(self, source: Nothing) -> _T1: ...

    def __call__(self, source: Option[_TSource]) -> _TSource | _T1:
        return source.default_value(self._value)


def default_value(value: _T1) -> _DefaultValue[_T1]:
    """Return an operation selecting the payload or a fallback value."""
    return _DefaultValue(value)


class _DefaultWith(Generic[_T1]):
    def __init__(self, getter: Callable[[], _T1]) -> None:
        self._getter = getter

    @overload
    def __call__(self, source: Some[_TSource]) -> _TSource: ...

    @overload
    def __call__(self, source: Nothing) -> _T1: ...

    def __call__(self, source: Option[_TSource]) -> _TSource | _T1:
        return source.default_with(self._getter)


def default_with(getter: Callable[[], _T1]) -> _DefaultWith[_T1]:
    """Return an operation selecting the payload or evaluating a fallback."""
    return _DefaultWith(getter)


def is_none(option: Option[object]) -> TypeGuard[Nothing]:
    """Narrow an option to its empty case."""
    return isinstance(option, Nothing)


def is_some(option: Option[_TSource]) -> TypeGuard[Some[_TSource]]:
    """Narrow an option to its present case."""
    return isinstance(option, Some)


@curry_flip(1)
def map(option: Option[_TSource], mapper: Callable[[_TSource], _TResult]) -> Option[_TResult]:
    return option.map(mapper)


@curry_flip(2)
def map2(opt1: Option[_T1], opt2: Option[_T2], mapper: Callable[[_T1, _T2], _TResult]) -> Option[_TResult]:
    return opt1.map2(mapper, opt2)


@overload
def apply(function: Nothing) -> Callable[[Option[object]], Nothing]: ...


@overload
def apply(function: Option[Callable[[_TSource], _TResult]]) -> Callable[[Option[_TSource]], Option[_TResult]]: ...


def apply(function: Option[Callable[[_TSource], _TResult]]) -> Callable[[Option[_TSource]], Option[_TResult]]:
    """Apply an optional function to an optional value."""

    def apply(source: Option[_TSource]) -> Option[_TResult]:
        return source.apply(function)

    return apply


@curry_flip(1)
def starmap(option: Option[tuple[*_P]], mapper: Callable[[Unpack[_P]], _TResult]) -> Option[_TResult]:
    return option.starmap(mapper)


def or_else(option: Option[_TSource], if_none: Option[_TResult]) -> Option[_TSource | _TResult]:
    """Return the first present option, allowing a different fallback type."""
    return option.or_else(if_none)


def to_list(option: Option[_TEmpty]) -> list[_TEmpty]:
    return option.to_list()


def to_seq(option: Option[_TEmpty]) -> Seq[_TEmpty]:
    from expression.collections.seq import Seq

    return Seq(option.to_list())


@overload
def to_optional(value: Some[_TSource]) -> _TSource: ...


@overload
def to_optional(value: Nothing) -> None: ...


def to_optional(value: Option[_TSource]) -> _TSource | None:
    """Erase the option wrapper, mapping Nothing to None."""
    return value.to_optional()


@overload
def of_optional(value: None) -> Nothing: ...


@overload
def of_optional(value: _TSource | None) -> Option[_TSource]: ...


def of_optional(value: _TSource | None) -> Option[_TSource]:
    """Wrap a value, treating None as absence."""
    return NOTHING if value is None else Some(value)


@overload
def of_obj(value: None) -> Nothing: ...


@overload
def of_obj(value: _TSource | None) -> Option[_TSource]: ...


def of_obj(value: _TSource | None) -> Option[_TSource]:
    """Wrap a value, treating None as absence."""
    return of_optional(value)


@overload
def of_result(result: Ok[_TSource]) -> Some[_TSource]: ...


@overload
def of_result(result: Error[object]) -> Nothing: ...


def of_result(result: Result[_TSource, object]) -> Option[_TSource]:
    """Keep the successful result payload, or return Nothing."""
    from expression.core.result import Ok

    return Some(result.ok) if isinstance(result, Ok) else NOTHING


@overload
def to_result(value: Some[_TSource], error: object) -> Ok[_TSource]: ...


@overload
def to_result(value: Nothing, error: _TError) -> Error[_TError]: ...


def to_result(value: Option[_TSource], error: _TError) -> Result[_TSource, _TError]:
    return value.to_result(error)


@overload
def to_result_with(value: Some[_TSource], error: Callable[[], object]) -> Ok[_TSource]: ...


@overload
def to_result_with(value: Nothing, error: Callable[[], _TError]) -> Error[_TError]: ...


def to_result_with(value: Option[_TSource], error: Callable[[], _TError]) -> Result[_TSource, _TError]:
    return value.to_result_with(error)


def model_dump(value: Option[object]) -> builtins.dict[str, object]:
    """Encode an option using its tagged wire representation."""
    return value.dict()


def default_arg(value: Option[_TSource], default_value: _T1) -> _TSource | _T1:
    """Return the payload or an uncurried fallback value."""
    return value.default_value(default_value)


__all__ = [
    "NOTHING",
    "Nothing",
    "Option",
    "Some",
    "apply",
    "bind",
    "default_arg",
    "default_value",
    "default_with",
    "is_none",
    "is_some",
    "map",
    "map2",
    "model_dump",
    "of_obj",
    "of_optional",
    "of_result",
    "or_else",
    "starmap",
    "to_list",
    "to_optional",
    "to_result",
    "to_result_with",
    "to_seq",
]
