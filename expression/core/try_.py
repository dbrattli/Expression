"""Result specialized to exception errors, with convenience constructors."""

from .result import Error, Ok, Result


type Try[T] = Result[T, Exception]


def Success[T](value: T) -> Ok[T]:
    """Construct a successful Try value."""
    return Ok(value)


def Failure(error: Exception) -> Error[Exception]:
    """Construct a failed Try value."""
    return Error(error)
