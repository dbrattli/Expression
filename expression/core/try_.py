"""The `Try` type  is a simpler `Result` type that pins the error type
to Exception.

Everything else is the same as `Result`.
"""

from typing import TypeVar

from .result import Error, Ok, Result

TSource = TypeVar("TSource")

Try = Result[TSource, Exception]


class Success(Ok[TSource, Exception]):
    ...


class Failure(Error[TSource, Exception]):
    ...
