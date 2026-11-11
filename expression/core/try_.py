"""Result specialized to exception errors, with convenience constructors."""

from typing import TypeAlias, TypeVar

from .result import Error, Ok, Result


_T = TypeVar("_T")
Try: TypeAlias = Result[_T, Exception]


def Success(value: _T) -> Ok[_T]:
    """Construct a successful Try value."""
    return Ok(value)


def Failure(error: Exception) -> Error[Exception]:
    """Construct a failed Try value."""
    return Error(error)
