from __future__ import annotations

from abc import abstractmethod
from collections.abc import Iterable
from typing import Any, Protocol, TypeVar, get_origin


_T = TypeVar("_T")
_T_co = TypeVar("_T_co", covariant=True)

_Base = TypeVar("_Base")
_Derived = TypeVar("_Derived")


class SupportsLessThan(Protocol):
    @abstractmethod
    def __lt__(self, __other: Any) -> bool:
        raise NotImplementedError


class SupportsSum(Protocol):
    @abstractmethod
    def __radd__(self, __other: Any) -> Any:
        raise NotImplementedError

    def __add__(self, __other: Any) -> Any:
        raise NotImplementedError


class SupportsGreaterThan(Protocol):
    @abstractmethod
    def __gt__(self, __other: Any) -> bool:
        raise NotImplementedError


class SupportsMatch(Protocol[_T_co]):
    """Pattern matching protocol."""

    @abstractmethod
    def __match__(self, pattern: Any) -> Iterable[_T_co]:
        """Match pattern with value.

        Return a singleton iterable item (e.g `[ value ]`) if pattern
        matches value, else an empty iterable (e.g. `[]`).
        """
        raise NotImplementedError


class ModelField:
    """Type mock to avoid taking a hard dependency on pydantic."""

    sub_fields: list[ModelField]

    def validate(self, value: Any, values: dict[str, str], loc: str) -> tuple[Any, Any]: ...


def upcast(type: type[_Base], expr: _Base) -> _Base:
    """Upcast expression from a `Derived` to `Base`.

    Note: F# `:>` or `upcast`.
    """
    return expr


def downcast(type: type[_Derived], expr: Any) -> _Derived:
    """Downcast expression `Derived` to `Base`.

    Checks at compile time that the type of expression Base is a
    supertype of Derived, and checks at runtime that Base is in fact an
    instance of Derived.

    Note: F# `:?>` or `downcast`.
    """
    assert isinstance(expr, type), f"The type of expression {expr} is not a supertype of {type}"
    return expr


def try_downcast(type_: type[_Derived], expr: Any) -> _Derived | None:
    """Downcast expression `Base` to `Derived`.

    Check that the `Derived` type is a supertype of `Base`.

    NOTE: Supports generic types.

    Returns:
        None if `Derived` is not a supertype of `Base`.
    """
    origin: type[_Derived] | None = get_origin(type_) or type_
    if origin is not None and isinstance(expr, origin):
        return expr

    return None


__all__ = [
    "downcast",
    "upcast",
    "try_downcast",
    "SupportsLessThan",
    "SupportsSum",
    "SupportsGreaterThan",
    "SupportsMatch",
]
