from __future__ import annotations

from abc import abstractmethod
from collections.abc import Iterable
from typing import Any, Protocol


class SupportsLessThan(Protocol):
    @abstractmethod
    def __lt__(self, __other: Any) -> bool:
        raise NotImplementedError


class SupportsLessThanAndHash(SupportsLessThan, Protocol):
    def __hash__(self) -> int:
        return super().__hash__()


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


class SupportsMatch[T_co](Protocol):
    """Pattern matching protocol."""

    @abstractmethod
    def __match__(self, pattern: Any) -> Iterable[T_co]:
        """Match pattern with value.

        Return a singleton iterable item (e.g `[ value ]`) if pattern
        matches value, else an empty iterable (e.g. `[]`).
        """
        raise NotImplementedError


class ModelField:
    """Type mock to avoid taking a hard dependency on pydantic."""

    sub_fields: list[ModelField]

    def validate(self, value: Any, values: dict[str, str], loc: str) -> tuple[Any, Any]: ...


# TODO: In the next major Expression release, use upcast(Base)(value) so the
# target type is fixed before checking the value, allowing static rejection
# of invalid upcasts. Keep the uncurried API for compatibility in this release.
def upcast[Base](type: type[Base], expr: object) -> Base:
    """View a value as the requested base type without converting it.

    The target alone determines the return type. Python's type inference
    cannot enforce the widening relationship in this two-argument API,
    so compatibility is checked at runtime using `downcast`. A mismatch
    raises `TypeError`, including under `python -O`.

    Targets must support `isinstance`; parameterized generics are unsupported.
    """
    return downcast(type, expr)


def downcast[Derived](type: type[Derived], expr: object) -> Derived:
    """Narrow a value to the requested runtime type without converting it.

    Return the original value if it is an instance of the target type;
    otherwise raise `TypeError`. The check remains active under `python -O`.
    The source and target inheritance relationship is not checked statically.

    Targets must support `isinstance`. Parameterized generics such as
    `list[int]` are unsupported and raise `TypeError`.
    """
    if isinstance(expr, type):
        return expr
    raise TypeError(f"Cannot cast value to {type!r}: incompatible runtime type")


def try_downcast[Derived](type_: type[Derived], expr: object) -> Derived | None:
    """Return the original value if it matches the target type, or `None`.

    Targets follow the same `isinstance` rules as `downcast`. Unsupported
    targets, including parameterized generics, raise `TypeError` rather
    than being treated as a value mismatch. Generic arguments are not erased.
    """
    if isinstance(expr, type_):
        return expr

    return None


__all__ = [
    "SupportsGreaterThan",
    "SupportsLessThan",
    "SupportsMatch",
    "SupportsSum",
    "downcast",
    "try_downcast",
    "upcast",
]
