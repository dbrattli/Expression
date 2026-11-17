"""Closed optional values and pipe-friendly operations.

``Option[T]`` is the union of ``Some[T]`` and the singleton case ``Nothing``.
Match the case classes to access their payloads. Iteration and awaiting retain
the computation-expression protocol, including short-circuiting on Nothing.
"""

from __future__ import annotations

import builtins
from collections.abc import Awaitable, Callable, Generator
from typing import (
    TYPE_CHECKING,
    Annotated,
    ClassVar,
    Final,
    Generic,
    Literal,
    Never,
    TypeAlias,
    Unpack,
    final,
)

from typing_extensions import TypeVar

from ._serialization import encode
from ._union_schema import UnionSchema
from .error import EffectError
from .pipe import PipeMixin
from .tagged_union import case, tag


if TYPE_CHECKING:
    from expression.collections.seq import Seq
    from expression.core.result import Error, Ok


_TSourceOut = TypeVar("_TSourceOut", covariant=True)
_TEmpty = TypeVar("_TEmpty", default=Never)


@final
@case
class Some(PipeMixin, Generic[_TSourceOut]):  # noqa: UP046 - Preserve explicit covariance.
    """An optional value that is present, including when its payload is None."""

    some: _TSourceOut
    tag: Literal["some"] = tag()

    def default_value(self, value: object) -> _TSourceOut:
        """Return the present value."""
        return self.some

    def default_with(self, getter: Callable[[], object]) -> _TSourceOut:
        """Return the present value without evaluating the fallback."""
        return self.some

    def map[TResult](self, mapper: Callable[[_TSourceOut], TResult]) -> Some[TResult]:
        """Transform the present value."""
        return Some(mapper(self.some))

    async def amap[TResult](self, mapper: Callable[[_TSourceOut], Awaitable[TResult]]) -> Some[TResult]:
        """Await a mapper and wrap its value, propagating exceptions and cancellation."""
        return Some(await mapper(self.some))

    async def abind[TOption: Some[object] | Nothing](
        self, mapper: Callable[[_TSourceOut], Awaitable[TOption]]
    ) -> TOption:
        """Await an option-returning callback without wrapping its result."""
        return await mapper(self.some)

    def map2[T2, TResult](self, mapper: Callable[[_TSourceOut, T2], TResult], other: Option[T2]) -> Option[TResult]:
        """Transform two present values, or return Nothing."""
        return other.map(lambda value: mapper(self.some, value))

    def apply[TResult](self, function: Option[Callable[[_TSourceOut], TResult]]) -> Option[TResult]:
        """Apply an optional function to the present value."""
        return function.map(lambda mapper: mapper(self.some))

    def starmap[*P, TResult](self: Some[tuple[*P]], mapper: Callable[[Unpack[P]], TResult]) -> Some[TResult]:
        """Apply a function to the unpacked tuple payload."""
        return Some(mapper(*self.some))

    def bind[TOption: Some[object] | Nothing](self, mapper: Callable[[_TSourceOut], TOption]) -> TOption:
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

    tag: Literal["none"] = tag()
    _instance: ClassVar[Nothing | None] = None

    def __new__(cls) -> Nothing:
        if cls._instance is None:
            cls._instance = object.__new__(cls)
        return cls._instance

    def default_value[TResult](self, value: TResult) -> TResult:
        """Return the fallback value."""
        return value

    def default_with[TResult](self, getter: Callable[[], TResult]) -> TResult:
        """Evaluate the fallback factory."""
        return getter()

    def map(self, mapper: Callable[[Never], object]) -> Nothing:
        """Keep the empty option without evaluating the mapper."""
        return self

    async def amap(self, mapper: Callable[[Never], Awaitable[object]]) -> Nothing:
        """Return Nothing without invoking the callback."""
        return self

    async def abind[TOption: Some[object] | Nothing](self, mapper: Callable[[Never], Awaitable[TOption]]) -> Nothing:
        """Return Nothing without invoking the continuation."""
        return self

    def map2[T2](self, mapper: Callable[[Never, T2], object], other: Option[T2]) -> Nothing:
        """Keep the empty option without evaluating the mapper."""
        return self

    def apply(self, function: Option[Callable[[Never], object]]) -> Nothing:
        """Keep the empty option without invoking the optional function."""
        return self

    def starmap(self, mapper: Callable[..., object]) -> Nothing:
        """Keep the empty option without evaluating the mapper."""
        return self

    def bind[TOption: Some[object] | Nothing](self, mapper: Callable[[Never], TOption]) -> Nothing:
        """Keep the empty option without evaluating the continuation."""
        return self

    def or_else[TOption: Some[object] | Nothing](self, if_none: TOption) -> TOption:
        """Return the fallback option."""
        return if_none

    def or_else_with[TOption: Some[object] | Nothing](self, if_none: Callable[[], TOption]) -> TOption:
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

    def to_result[TError](self, error: TError) -> Error[TError]:
        """Return the supplied error as a failed result."""
        from expression.core.result import Error

        return Error(error)

    def to_result_with[TError](self, error: Callable[[], TError]) -> Error[TError]:
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


# Keep an evaluated alias for runtime union introspection and Pydantic schemas.
Option: TypeAlias = Annotated[Some[_TSourceOut] | Nothing, UnionSchema(canonical_values=(NOTHING,))]  # noqa: UP040


# Load functional helpers only after the cases and runtime alias exist.
# Helpers import these definitions; this order avoids partial types at startup.
from ._option_async import (  # noqa: E402
    abind,
    amap,
)
from ._option_sync import (  # noqa: E402
    apply,
    bind,
    default_arg,
    default_value,
    default_with,
    is_none,
    is_some,
    map,
    map2,
    model_dump,
    of_obj,
    of_optional,
    of_result,
    or_else,
    starmap,
    to_list,
    to_optional,
    to_result,
    to_result_with,
    to_seq,
)


# Runtime-only aliases for callable stages pickled before helper extraction.
if not TYPE_CHECKING:
    from ._option_async import (  # noqa: F401
        _AsyncBind,
        _AsyncMap,
    )
    from ._option_sync import (  # noqa: F401
        _DefaultValue,
        _DefaultWith,
    )


__all__ = [
    "NOTHING",
    "Nothing",
    "Option",
    "Some",
    "abind",
    "amap",
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
