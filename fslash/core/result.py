"""
Result module.

The Result[TSource,TError] type lets you write error-tolerant code that
can be composed. The Result type is typically used in monadic
error-handling, which is often referred to as Railway-oriented
Programming.
"""

from abc import abstractmethod
from typing import TypeVar, Generic, Callable, Iterator, Iterable, Union, List
from .misc import identity
from .pipe import pipe

TSource = TypeVar("TSource")
TResult = TypeVar("TResult")
TError = TypeVar("TError")


class Result(Generic[TSource, TError], Iterable[Union[TSource, TError]]):
    """The result abstract base class."""

    def pipe(self, *args):
        """Pipe result through the given functions."""
        return pipe(self, *args)

    @abstractmethod
    def map(self, mapper: Callable[[TSource], TResult]) -> "Result[TResult, TError]":
        raise NotImplementedError

    @abstractmethod
    def bind(self, mapper: Callable[[TSource], "Result[TResult, TError]"]) -> "Result[TResult, TError]":
        raise NotImplementedError

    @abstractmethod
    def is_error(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def is_ok(self) -> bool:
        raise NotImplementedError

    def __eq__(self, other):
        raise NotImplementedError

    @abstractmethod
    def __iter__(self) -> Iterator[TSource]:
        raise NotImplementedError

    def __repr__(self):
        return str(self)


class Ok(Result[TSource, TError]):
    """The Ok result case class."""

    def __init__(self, value: TSource) -> None:
        self._value = value

    @property
    def value(self):
        return self._value

    def map(self, mapper: Callable[[TSource], TResult]) -> Result[TResult, TError]:
        return Ok(mapper(self._value))

    def bind(self, mapper: Callable[[TSource], Result[TResult, TError]]) -> Result[TResult, TError]:
        return mapper(self._value)

    def map_error(self, mapper: Callable[[TError], TResult]) -> Result[TSource, TResult]:
        return Ok(self._value)

    def is_error(self) -> bool:
        return False

    def is_ok(self) -> bool:
        return True

    def __eq__(self, other):
        if isinstance(other, Ok):
            return self.value == other.value
        return False

    def __iter__(self) -> Iterator[TSource]:
        """Return iterator for Ok case."""
        return (yield self._value)

    def __str__(self):
        return f"Ok {self._value}"


class Error(Result[TSource, TError]):
    """The Error result case class."""

    def __init__(self, error: TError) -> None:
        self._error = error

    @property
    def error(self) -> TError:
        return self._error

    def map(self, mapper: Callable[[TSource], TResult]) -> Result[TResult, TError]:
        return Error(self._error)

    def bind(self, mapper: Callable[[TSource], Result[TResult, TError]]) -> Result[TResult, TError]:
        return Error(self._error)

    def map_error(self, mapper: Callable[[TError], TResult]) -> Result[TSource, TResult]:
        return Error(mapper(self._error))

    def is_error(self) -> bool:
        return True

    def is_ok(self) -> bool:
        return False

    def __eq__(self, other):
        if isinstance(other, Error):
            return self.error == other.error
        return False

    def __iter__(self) -> Iterator[TSource]:
        """Return iterator for Error case."""
        raise ResultException(self._error)
        yield

    def __str__(self):
        return f"Error {self._error}"


class ResultException(Exception):
    """Used for raising errors when a result `Error` case is
    iterated."""

    def __init__(self, error):
        self.error = error


def map(mapper: Callable[[TSource], TResult]) -> Callable[[Result[TSource, TError]], Result[TResult, TError]]:
    def _map(result: Result[TSource, TError]) -> Result[TResult, TError]:
        return result.map(mapper)

    return _map


def bind(
    mapper: Callable[[TSource], Result[TResult, TError]]
) -> Callable[[Result[TSource, TError]], Result[TResult, TError]]:
    def _bind(result: Result[TSource, TError]) -> Result[TResult, TError]:
        return result.bind(mapper)

    return _bind


def traverse(fn: Callable[[TSource], Result[TResult, TError]], lst: List[TSource]) -> Result[List[TResult], TError]:
    """Traverses a list of items.

    Threads an applicative computation though a list of items.
    """

    from fslash.builders import result
    from fslash.collections import Seq

    # flake8: noqa: T484
    @result
    def folder(head: TSource, tail: Result[List[TResult], TError]):
        """Same as:
        >>> fn(head).bind(lambda head: tail.bind(lambda tail: Ok([head] + tail)))
        """
        h = yield from fn(head)
        t = yield from tail
        return [h] + t

    return Seq.fold_back(folder, lst)(Ok([]))  # type: ignore


def sequence(lst: List[Result[TSource, TError]]) -> Result[List[TSource], TError]:
    """Execute a sequence of result returning commands and collect the
    sequence of their response."""

    return traverse(identity, lst)


__all__ = ["Result", "Ok", "Error", "ResultException", "map", "bind", "traverse", "sequence"]
