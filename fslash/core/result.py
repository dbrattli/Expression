"""
Result module.
"""

from abc import abstractmethod
from typing import TypeVar, Generic, Callable, Iterator, Iterable, Union

TSource = TypeVar("TSource")
TResult = TypeVar("TResult")
TError = TypeVar("TError")


class ResultModule(Generic[TSource, TError]):
    @staticmethod
    def map(mapper: Callable[[TSource], TResult]) -> "Callable[[Result[TSource, TError]], Result[TResult, TError]]":
        def _map(result: Result[TSource, TError]) -> "Result[TResult, TError]":
            return result.map(mapper)

        return _map

    @staticmethod
    def bind(
        mapper: Callable[[TSource], "Result[TResult, TError]"]
    ) -> "Callable[[Result[TSource, TError]], Result[TResult, TError]]":
        def _bind(result: Result[TSource, TError]) -> Result[TResult, TError]:
            return result.bind(mapper)

        return _bind


class Result(Generic[TSource, TError], Iterable[Union[TSource, TError]]):
    """The result abstract base class."""

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


__all__ = ["ResultModule", "Result", "Ok", "Error", "ResultException"]
