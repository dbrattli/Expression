from abc import abstractmethod
from typing import Any, Optional, TypeVar, cast, get_origin

from typing_extensions import Protocol

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C", bound="Comparable")
TSource = TypeVar("TSource")
TResult = TypeVar("TResult")
Base = TypeVar("Base")
Derived = TypeVar("Derived")


class Comparable(Protocol):
    @abstractmethod
    def __eq__(self, other: Any) -> bool:
        pass

    @abstractmethod
    def __lt__(self: C, other: C) -> bool:
        pass

    def __gt__(self: C, other: C) -> bool:
        return (not self < other) and self != other

    def __le__(self: C, other: C) -> bool:
        return self < other or self == other

    def __ge__(self: C, other: C) -> bool:
        return not self < other


def downcast(type: Base, expr: Derived) -> Base:
    """Downcast expression `Derived` to `Base`

    Checks at compile time that the type of expression E is a supertype
    of T, and checks at runtime that E is in fact an instance of T.

    Note: F# `:?>` or `downcast`.
    """
    assert isinstance(expr, type), f"The type of expression {expr} is not a supertype of {type}"
    return expr


def upcast(type: Derived, expr: Base) -> Derived:
    """Upcast expression `Base` to `Derived`.

    Check that the `Derived` type is a supertype of Base.

    Note: F# `:>` or `upcast`.
    """

    assert isinstance(expr, type), f"The expression {expr} is not derived from type {type}"
    return expr


def try_upcast(type_: Derived, expr: Base) -> Optional[Derived]:
    """Upcast expression `Base` to `Derived`.

    Check that the `Derived` type is a supertype of `Base`.

    NOTE: Supports generic types.

    Returns:
        None if `Derived` is not a supertype of `Base`.
    """
    origin: Optional[Derived] = get_origin(type_) or type_
    if origin is not None and isinstance(expr, origin):
        derived = cast(type(type_), expr)
        return derived
    else:
        return None


__all__ = ["Comparable"]
