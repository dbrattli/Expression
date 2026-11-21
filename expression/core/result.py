"""Closed result cases and pipe-friendly operations.

``Result[T, E]`` is the union of ``Ok[T]`` and ``Error[E]``. Match the
case classes to access their payloads. Iteration and awaiting retain the
computation-expression protocol, including short-circuiting on Error.
"""

from __future__ import annotations

import builtins
from collections.abc import Awaitable, Callable, Generator
from typing import (
    TYPE_CHECKING,
    Generic,
    Literal,
    Never,
    TypeAlias,
    final,
)

from typing_extensions import TypeVar

from ._serialization import encode
from .error import EffectError
from .option import NOTHING, Nothing
from .pipe import PipeMixin
from .tagged_union import TaggedUnion, case, tag


if TYPE_CHECKING:
    from .option import Some


if TYPE_CHECKING:
    _T = TypeVar("_T", covariant=True, default=Never)
    _E = TypeVar("_E", covariant=True, default=Never)
else:
    # Never supports static inference, but bare Result payloads must remain
    # unconstrained when Pydantic generates their runtime schemas.
    _T = TypeVar("_T", covariant=True)
    _E = TypeVar("_E", covariant=True)
_A = TypeVar("_A", default=object)
_U = TypeVar("_U", default=Never)
_F = TypeVar("_F", default=Never)
_R = TypeVar("_R", bound="Ok[object] | Error[object]", default=Never)


@final
@case
class Ok(PipeMixin, Generic[_T]):  # noqa: UP046 - Python 3.12 cannot express type parameter defaults.
    """A successful result containing a value."""

    ok: _T
    tag: Literal["ok"] = tag()

    def default_value(self, value: object) -> _T:
        """Return the successful value."""
        return self.ok

    def default_with(self, getter: Callable[[Never], object]) -> _T:
        """Return the successful value without evaluating the fallback."""
        return self.ok

    def map(self, mapper: Callable[[_T], _U]) -> Ok[_U]:
        """Transform the successful value."""
        return Ok(mapper(self.ok))

    async def amap(self, mapper: Callable[[_T], Awaitable[_U]]) -> Ok[_U]:
        """Await a mapper and wrap its value, propagating exceptions and cancellation."""
        return Ok(await mapper(self.ok))

    async def abind(self, mapper: Callable[[_T], Awaitable[_R]]) -> _R:
        """Await a result-returning callback without wrapping its result."""
        return await mapper(self.ok)

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
class Error(PipeMixin, Generic[_E]):  # noqa: UP046 - Python 3.12 cannot express type parameter defaults.
    """A failed result containing an error."""

    error: _E
    tag: Literal["error"] = tag()

    def default_value(self, value: _U) -> _U:
        """Return the fallback value."""
        return value

    def default_with(self, getter: Callable[[_E], _U]) -> _U:
        """Compute a fallback from the error."""
        return getter(self.error)

    def map(self, mapper: Callable[[Never], _U]) -> Error[_E]:
        """Preserve the error without evaluating the mapper."""
        return self

    async def amap(self, mapper: Callable[[Never], Awaitable[_U]]) -> Error[_E]:
        """Preserve this error without invoking the callback."""
        return self

    async def abind(self, mapper: Callable[[Never], Awaitable[_R]]) -> Error[_E]:
        """Preserve this error without invoking the continuation."""
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


# Keep an evaluated alias for runtime union introspection and Pydantic schemas.
Result: TypeAlias = TaggedUnion[Ok[_T] | Error[_E]]  # noqa: UP040


# Load functional helpers only after the cases and runtime alias exist.
# Helpers import these definitions; this order avoids partial types at startup.
from ._result_async import (  # noqa: E402
    abind,
    amap,
)
from ._result_sync import (  # noqa: E402
    apply,
    bind,
    default_value,
    default_with,
    dict,
    filter,
    filter_with,
    is_error,
    is_ok,
    map,
    map2,
    map_error,
    merge,
    of_option,
    of_option_with,
    or_else,
    or_else_with,
    swap,
    to_option,
)


__all__ = [
    "Error",
    "Ok",
    "Result",
    "abind",
    "amap",
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
