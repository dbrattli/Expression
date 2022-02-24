"""The `Try` type  is a simpler `Result` type that pins the error type
to Exception.

Everything else is the same as `Result`, just simpler to use.
"""

from typing import TypeVar

from .result import Error, Ok, Result

_TSource = TypeVar("_TSource")

Try = Result[_TSource, Exception]


class Success(Ok[_TSource, Exception]):
    """The successful Try case.

    Same as result `Ok` but with error type pinned to an exception, i.e:
    `Ok[TSource, Exception]`
    """

    ...


class Failure(Error[_TSource, Exception]):
    """The failure Try case.

    Same as result `Error` but with error type pinned to an exception,
    i.e: `Error[TSource, Exception]`
    """

    ...
