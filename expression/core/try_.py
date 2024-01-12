"""Try result class.

The `Try` type  is a simpler `Result` type that pins the error type to
Exception.

Everything else is the same as `Result`, just simpler to use.
"""

from typing import Any, TypeVar

from .result import Result


_TSource = TypeVar("_TSource")


class Try(Result[_TSource, Exception]):
    """A try result.

    Same as `Result` but with error type pinned to `Exception`. Making it simpler
    to use when the error type is an exception.
    """

    def __str__(self) -> str:
        """Return a string representation of the Try."""
        match self:
            case Try(tag="ok", ok=ok):
                return f"Success {ok}"
            case Try(error=error):
                return f"Failure {error}"


def Success(value: _TSource) -> Try[_TSource]:
    """The successful Try case.

    Same as result `Ok` but with error type pinned to an exception, i.e:
    `Ok[TSource, Exception]`
    """
    return Try[_TSource](ok=value)


def Failure(error: Exception) -> Try[Any]:
    """The failure Try case.

    Same as result `Error` but with error type pinned to an exception,
    i.e: `Error[TSource, Exception]`
    """
    return Try[Any](error=error)
