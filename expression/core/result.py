"""Closed result cases and pipe-friendly operations.

``Result[T, E]`` is the union of ``Ok[T]`` and ``Error[E]``. Match the
case classes to access their payloads. Iteration and awaiting retain the
computation-expression protocol, including short-circuiting on Error.
"""

from __future__ import annotations

import builtins
from collections.abc import Callable, Generator
from typing import (
    TYPE_CHECKING,
    Generic,
    Literal,
    Never,
    Protocol,
    TypeAlias,
    TypeGuard,
    final,
    overload,
)

from typing_extensions import TypeVar

from ._serialization import encode
from .error import EffectError
from .option import NOTHING, Nothing
from .pipe import PipeMixin
from .tagged_union import TaggedUnion, case, tag


if TYPE_CHECKING:
    from .option import Option, Some


if TYPE_CHECKING:
    _T = TypeVar("_T", covariant=True, default=Never)
    _E = TypeVar("_E", covariant=True, default=Never)
else:
    # Never supports static inference, but bare Result payloads must remain
    # unconstrained when Pydantic generates their runtime schemas.
    _T = TypeVar("_T", covariant=True)
    _E = TypeVar("_E", covariant=True)
_A = TypeVar("_A", default=object)
_B = TypeVar("_B", default=object)
_U = TypeVar("_U", default=Never)
_F = TypeVar("_F", default=Never)
_R = TypeVar("_R", bound="Ok[object] | Error[object]", default=Never)
_Input = TypeVar("_Input", contravariant=True)
_Output = TypeVar("_Output", covariant=True)
_Failure = TypeVar("_Failure", covariant=True)


@final
@case
class Ok(PipeMixin, Generic[_T]):
    """A successful result containing a value."""

    ok: _T
    tag: Literal["ok"] = tag("ok")

    def default_value(self, value: object) -> _T:
        """Return the successful value."""
        return self.ok

    def default_with(self, getter: Callable[[Never], object]) -> _T:
        """Return the successful value without evaluating the fallback."""
        return self.ok

    def map(self, mapper: Callable[[_T], _U]) -> Ok[_U]:
        """Transform the successful value."""
        return Ok(mapper(self.ok))

    def map2(self, other: Result[_A, _F], mapper: Callable[[_T, _A], _U]) -> Result[_U, _F]:
        """Map two successful results, preserving the other result's error."""
        return other.map(lambda value: mapper(self.ok, value))

    def apply(self, function: Result[Callable[[_T], _U], _F]) -> Result[_U, _F]:
        """Apply a successful function to the value."""
        return function.map(lambda mapper: mapper(self.ok))

    def map_error(self, mapper: Callable[[Never], _F]) -> Ok[_T]:
        """Preserve this successful result."""
        return self

    def bind(self, mapper: Callable[[_T], _R]) -> _R:
        """Apply a result-returning function to the value."""
        return mapper(self.ok)

    def is_error(self) -> Literal[False]:
        return False

    def is_ok(self) -> Literal[True]:
        return True

    def filter(self, predicate: Callable[[_T], bool], default: _F) -> Result[_T, _F]:
        """Keep a value satisfying the predicate or return the supplied error."""
        return self if predicate(self.ok) else Error(default)

    def filter_with(self, predicate: Callable[[_T], bool], default: Callable[[_T], _F]) -> Result[_T, _F]:
        """Keep a value satisfying the predicate or compute an error."""
        return self if predicate(self.ok) else Error(default(self.ok))

    def dict(self) -> builtins.dict[str, object]:
        """Encode this case and its payload as a tagged mapping."""
        return {"tag": "ok", "ok": encode(self.ok)}

    def swap(self) -> Error[_T]:
        """Move the successful value into the error channel."""
        return Error(self.ok)

    def or_else(self, other: Result[object, object]) -> Ok[_T]:
        """Preserve this successful result."""
        return self

    def or_else_with(self, other: Callable[[Never], Result[object, object]]) -> Ok[_T]:
        """Preserve this result without evaluating the fallback."""
        return self

    def merge(self) -> _T:
        """Return this case's payload."""
        return self.ok

    def to_option(self) -> Some[_T]:
        """Wrap the value in Some."""
        from .option import Some

        return Some(self.ok)

    def __iter__(self) -> Generator[_T, _T, _T]:
        return (yield self.ok)

    def __await__(self) -> Generator[_T, _T, _T]:
        return self.ok
        yield

    def __str__(self) -> str:
        return f"Ok {self.ok}"


@final
@case
class Error(PipeMixin, Generic[_E]):
    """A failed result containing an error."""

    error: _E
    tag: Literal["error"] = tag("error")

    def default_value(self, value: _U) -> _U:
        """Return the fallback value."""
        return value

    def default_with(self, getter: Callable[[_E], _U]) -> _U:
        """Compute a fallback from the error."""
        return getter(self.error)

    def map(self, mapper: Callable[[Never], _U]) -> Error[_E]:
        """Preserve the error without evaluating the mapper."""
        return self

    def map2(self, other: Result[_A, _F], mapper: Callable[[Never, _A], _U]) -> Error[_E]:
        """Preserve this error without evaluating the mapper."""
        return self

    def apply(self, function: Result[Callable[[Never], object], _F]) -> Error[_E] | Error[_F]:
        """Preserve the error, preferring a function error when both fail."""
        match function:
            case Error():
                return function
            case Ok():
                return self

    def map_error(self, mapper: Callable[[_E], _F]) -> Error[_F]:
        """Transform the error."""
        return Error(mapper(self.error))

    def bind(self, mapper: Callable[[Never], _R]) -> Error[_E]:
        """Preserve the error without evaluating the continuation."""
        return self

    def is_error(self) -> Literal[True]:
        return True

    def is_ok(self) -> Literal[False]:
        return False

    def filter(self, predicate: Callable[[Never], bool], default: object) -> Error[_E]:
        """Preserve the existing error."""
        return self

    def filter_with(self, predicate: Callable[[Never], bool], default: Callable[[Never], object]) -> Error[_E]:
        """Preserve the existing error without evaluating callbacks."""
        return self

    def dict(self) -> builtins.dict[str, object]:
        """Encode this case and its payload as a tagged mapping."""
        return {"tag": "error", "error": encode(self.error)}

    def swap(self) -> Ok[_E]:
        """Move the error into the success channel."""
        return Ok(self.error)

    def or_else(self, other: _R) -> _R:
        """Return the fallback result."""
        return other

    def or_else_with(self, other: Callable[[_E], _R]) -> _R:
        """Compute a fallback result from the error."""
        return other(self.error)

    def merge(self) -> _E:
        """Return this case's payload."""
        return self.error

    def to_option(self) -> Nothing:
        """Discard the error and return Nothing."""
        return NOTHING

    def __iter__(self) -> Generator[Never, object, Never]:
        raise EffectError(self)
        yield

    def __await__(self) -> Generator[Never, object, Never]:
        raise EffectError(self)
        yield

    def __str__(self) -> str:
        return f"Error {self.error}"


Result: TypeAlias = TaggedUnion[Ok[_T] | Error[_E]]


# Case-specific callable overloads preserve the untouched channel when a pipe
# dispatches over a union. A generic closure instead leaks unsolved type variables.
class _DefaultValue(Generic[_U]):
    def __init__(self, value: _U) -> None:
        self._value = value

    @overload
    def __call__(self, source: Ok[_A]) -> _A: ...

    @overload
    def __call__(self, source: Error[object]) -> _U: ...

    def __call__(self, source: Result[_A, object]) -> _A | _U:
        return source.default_value(self._value)


def default_value(value: _U) -> _DefaultValue[_U]:
    """Return an operation selecting the value or a fallback."""
    return _DefaultValue(value)


class _DefaultWith(Generic[_A, _U]):
    def __init__(self, getter: Callable[[_A], _U]) -> None:
        self._getter = getter

    @overload
    def __call__(self, source: Ok[_B]) -> _B: ...

    @overload
    def __call__(self, source: Error[_A]) -> _U: ...

    def __call__(self, source: Result[_B, _A]) -> _B | _U:
        return source.default_with(self._getter)


def default_with(getter: Callable[[_A], _U]) -> _DefaultWith[_A, _U]:
    """Return an operation selecting the value or computing a fallback."""
    return _DefaultWith(getter)


class _Map(Generic[_A, _U]):
    def __init__(self, mapper: Callable[[_A], _U]) -> None:
        self._mapper = mapper

    @overload
    def __call__(self, source: Ok[_A]) -> Ok[_U]: ...

    @overload
    def __call__(self, source: Error[_F]) -> Error[_F]: ...

    def __call__(self, source: Result[_A, _F]) -> Result[_U, _F]:
        return source.map(self._mapper)


def map(mapper: Callable[[_A], _U]) -> _Map[_A, _U]:
    return _Map(mapper)


class _ResultOperation(Protocol[_Input, _Output, _Failure]):
    @overload
    def __call__(self, source: Ok[_Input], /) -> Result[_Output, _Failure]: ...

    @overload
    def __call__(self, source: Error[_E], /) -> Error[_E] | Error[_Failure]: ...


class _Map2Ok(_ResultOperation[_B, _U, Never], Generic[_A, _B, _U]):
    def __init__(self, value: _A, mapper: Callable[[_A, _B], _U]) -> None:
        self._value = value
        self._mapper = mapper

    @overload
    def __call__(self, other: Ok[_B]) -> Ok[_U]: ...

    @overload
    def __call__(self, other: Error[_F]) -> Error[_F]: ...

    def __call__(self, other: Result[_B, _F]) -> Result[_U, _F]:
        return other.map(lambda value: self._mapper(self._value, value))


class _Map2Error(_ResultOperation[object, Never, _E], Generic[_E]):
    def __init__(self, source: Error[_E]) -> None:
        self._source = source

    def __call__(self, other: Result[object, object]) -> Error[_E]:
        return self._source


class _Map2(Generic[_A, _B, _U]):
    def __init__(self, mapper: Callable[[_A, _B], _U]) -> None:
        self._mapper = mapper

    @overload
    def __call__(self, source: Ok[_A]) -> _Map2Ok[_A, _B, _U]: ...

    @overload
    def __call__(self, source: Error[_E]) -> _Map2Error[_E]: ...

    @overload
    def __call__(self, source: Result[_A, _E]) -> _ResultOperation[_B, _U, _E]: ...

    def __call__(self, source: Result[_A, _E]) -> _ResultOperation[_B, _U, _E]:
        match source:
            case Ok(value):
                return _Map2Ok(value, self._mapper)
            case Error():
                return _Map2Error(source)


def map2(mapper: Callable[[_A, _B], _U]) -> _Map2[_A, _B, _U]:
    """Map two results in source order, preserving the first error."""
    return _Map2(mapper)


class _ApplyOk(_ResultOperation[_A, _U, Never], Generic[_A, _U]):
    def __init__(self, mapper: Callable[[_A], _U]) -> None:
        self._mapper = mapper

    @overload
    def __call__(self, source: Ok[_A]) -> Ok[_U]: ...

    @overload
    def __call__(self, source: Error[_E]) -> Error[_E]: ...

    def __call__(self, source: Result[_A, _E]) -> Result[_U, _E]:
        return source.map(self._mapper)


class _ApplyError(_ResultOperation[object, Never, _F], Generic[_F]):
    def __init__(self, error: Error[_F]) -> None:
        self._error = error

    def __call__(self, source: Result[object, object]) -> Error[_F]:
        return self._error


@overload
def apply(function: Ok[Callable[[_A], _U]]) -> _ApplyOk[_A, _U]: ...


@overload
def apply(function: Error[_F]) -> _ApplyError[_F]: ...


@overload
def apply(function: Result[Callable[[_A], _U], _F]) -> _ResultOperation[_A, _U, _F]: ...


def apply(function: Result[Callable[[_A], _U], _F]) -> _ResultOperation[_A, _U, _F]:
    """Apply a function result, preferring its error when both inputs fail."""
    match function:
        case Ok(mapper):
            return _ApplyOk(mapper)
        case Error():
            return _ApplyError(function)


class _MapError(Generic[_A, _U]):
    def __init__(self, mapper: Callable[[_A], _U]) -> None:
        self._mapper = mapper

    @overload
    def __call__(self, source: Ok[_B]) -> Ok[_B]: ...

    @overload
    def __call__(self, source: Error[_A]) -> Error[_U]: ...

    def __call__(self, source: Result[_B, _A]) -> Result[_B, _U]:
        return source.map_error(self._mapper)


def map_error(mapper: Callable[[_A], _U]) -> _MapError[_A, _U]:
    return _MapError(mapper)


class _Bind(Generic[_A, _R]):
    def __init__(self, mapper: Callable[[_A], _R]) -> None:
        self._mapper = mapper

    @overload
    def __call__(self, source: Ok[_A]) -> _R: ...

    @overload
    def __call__(self, source: Error[_F]) -> Error[_F]: ...

    def __call__(self, source: Result[_A, _F]) -> _R | Error[_F]:
        return source.bind(self._mapper)


def bind(mapper: Callable[[_A], _R]) -> _Bind[_A, _R]:
    """Bind a result while retaining both possible error channels."""
    return _Bind(mapper)


def dict(source: Result[object, object]) -> builtins.dict[str, object]:
    return source.dict()


def is_ok(source: Result[_A, object]) -> TypeGuard[Ok[_A]]:
    """Narrow a result to its successful case."""
    return isinstance(source, Ok)


def is_error(source: Result[object, _F]) -> TypeGuard[Error[_F]]:
    """Narrow a result to its error case."""
    return isinstance(source, Error)


class _Filter(Generic[_A, _F]):
    def __init__(self, predicate: Callable[[_A], bool], default: _F) -> None:
        self._predicate = predicate
        self._default = default

    @overload
    def __call__(self, source: Ok[_A]) -> Result[_A, _F]: ...

    @overload
    def __call__(self, source: Error[_E]) -> Error[_E]: ...

    def __call__(self, source: Result[_A, _E]) -> Result[_A, _F | _E]:
        return source.filter(self._predicate, self._default)


def filter(predicate: Callable[[_A], bool], default: _F) -> _Filter[_A, _F]:
    return _Filter(predicate, default)


class _FilterWith(Generic[_A, _F]):
    def __init__(self, predicate: Callable[[_A], bool], default: Callable[[_A], _F]) -> None:
        self._predicate = predicate
        self._default = default

    @overload
    def __call__(self, source: Ok[_A]) -> Result[_A, _F]: ...

    @overload
    def __call__(self, source: Error[_E]) -> Error[_E]: ...

    def __call__(self, source: Result[_A, _E]) -> Result[_A, _F | _E]:
        return source.filter_with(self._predicate, self._default)


def filter_with(predicate: Callable[[_A], bool], default: Callable[[_A], _F]) -> _FilterWith[_A, _F]:
    return _FilterWith(predicate, default)


@overload
def swap(source: Ok[_A]) -> Error[_A]: ...


@overload
def swap(source: Error[_F]) -> Ok[_F]: ...


def swap(source: Result[_A, _F]) -> Result[_F, _A]:
    return source.swap()


class _OrElse(Generic[_R]):
    def __init__(self, other: _R) -> None:
        self._other = other

    @overload
    def __call__(self, source: Ok[_A]) -> Ok[_A]: ...

    @overload
    def __call__(self, source: Error[object]) -> _R: ...

    def __call__(self, source: Result[_A, object]) -> Ok[_A] | _R:
        return source.or_else(self._other)


def or_else(other: _R) -> _OrElse[_R]:
    return _OrElse(other)


class _OrElseWith(Generic[_A, _R]):
    def __init__(self, other: Callable[[_A], _R]) -> None:
        self._other = other

    @overload
    def __call__(self, source: Ok[_B]) -> Ok[_B]: ...

    @overload
    def __call__(self, source: Error[_A]) -> _R: ...

    def __call__(self, source: Result[_B, _A]) -> Ok[_B] | _R:
        return source.or_else_with(self._other)


def or_else_with(other: Callable[[_A], _R]) -> _OrElseWith[_A, _R]:
    return _OrElseWith(other)


@overload
def merge(source: Ok[_A]) -> _A: ...


@overload
def merge(source: Error[_B]) -> _B: ...


def merge(source: Result[_A, _B]) -> _A | _B:
    return source.merge()


@overload
def to_option(source: Ok[_A]) -> Some[_A]: ...


@overload
def to_option(source: Error[object]) -> Nothing: ...


def to_option(source: Result[_A, object]) -> Option[_A]:
    return source.to_option()


@overload
def of_option(value: Some[_A], error: object) -> Ok[_A]: ...


@overload
def of_option(value: Nothing, error: _F) -> Error[_F]: ...


def of_option(value: Option[_A], error: _F) -> Result[_A, _F]:
    return value.to_result(error)


@overload
def of_option_with(value: Some[_A], error: Callable[[], object]) -> Ok[_A]: ...


@overload
def of_option_with(value: Nothing, error: Callable[[], _F]) -> Error[_F]: ...


def of_option_with(value: Option[_A], error: Callable[[], _F]) -> Result[_A, _F]:
    return value.to_result_with(error)


__all__ = [
    "Error",
    "Ok",
    "Result",
    "apply",
    "bind",
    "default_value",
    "default_with",
    "dict",
    "filter",
    "filter_with",
    "is_error",
    "is_ok",
    "map",
    "map2",
    "map_error",
    "merge",
    "of_option",
    "of_option_with",
    "or_else",
    "or_else_with",
    "swap",
    "to_option",
]
