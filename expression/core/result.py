"""Result module.

The Result[TSource,TError] type lets you write error-tolerant code that
can be composed. The Result type is typically used in monadic
error-handling, which is often referred to as Railway-oriented
Programming.

There is also a simplifyed alias of this type called `Maybe` that pins
the Result type to Exception.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import (
    Any,
    Callable,
    Generator,
    Iterable,
    Iterator,
    Type,
    TypeVar,
    Union,
    get_origin,
    overload,
)

from .error import EffectError
from .match import Case, SupportsMatch
from .pipe import pipe

_TSource = TypeVar("_TSource")
_TResult = TypeVar("_TResult")
_TError = TypeVar("_TError")

# Used for generic methods
_TSourceM = TypeVar("_TSourceM")
_TErrorM = TypeVar("_TErrorM")

_T1 = TypeVar("_T1")
_T2 = TypeVar("_T2")
_T3 = TypeVar("_T3")
_T4 = TypeVar("_T4")


class Result(Iterable[_TSource], SupportsMatch[Union[_TSource, _TError]], ABC):
    """The result abstract base class."""

    @overload
    def pipe(
        self: Result[_T1, _TError],
        __fn1: Callable[[Result[_T1, _TError]], Result[_T2, _TError]],
    ) -> Result[_T2, _TError]:
        ...

    @overload
    def pipe(
        self,
        __fn1: Callable[[Result[_TSource, _TError]], _T1],
        __fn2: Callable[[_T1], _T2],
    ) -> _T2:
        ...

    @overload
    def pipe(
        self,
        __fn1: Callable[[Result[_TSource, _TError]], _T1],
        __fn2: Callable[[_T1], _T2],
        __fn3: Callable[[_T2], _T3],
    ) -> _T3:
        ...

    @overload
    def pipe(
        self,
        __fn1: Callable[[Result[_TSource, _TError]], _T1],
        __fn2: Callable[[_T1], _T2],
        __fn3: Callable[[_T2], _T3],
        __fn4: Callable[[_T3], _T4],
    ) -> _T4:
        ...

    def pipe(self, *args: Any) -> Any:
        """Pipe result through the given functions."""
        return pipe(self, *args)

    @abstractmethod
    def map(self, mapper: Callable[[_TSource], _TResult]) -> Result[_TResult, _TError]:
        raise NotImplementedError

    @abstractmethod
    def map_error(
        self, mapper: Callable[[_TError], _TResult]
    ) -> Result[_TSource, _TResult]:
        """Return a result of the error value after applying the mapping
        function, or Ok if the input is Ok."""
        raise NotImplementedError

    @abstractmethod
    def bind(
        self, mapper: Callable[[_TSource], Result[_TResult, _TError]]
    ) -> Result[_TResult, _TError]:
        raise NotImplementedError

    @overload
    def match(self, pattern: "Ok[_TSourceM, Any]") -> Iterable[_TSourceM]:
        ...

    @overload
    def match(self, pattern: "Error[Any, _TErrorM]") -> Iterable[_TErrorM]:
        ...

    @overload
    def match(self, pattern: "Case[Ok[_TSourceM, Any]]") -> Iterable[_TSourceM]:
        ...

    @overload
    def match(self, pattern: "Case[Error[Any, _TErrorM]]") -> Iterable[_TErrorM]:
        ...

    @overload
    def match(self, pattern: "Type[Result[_TSourceM, Any]]") -> Iterable[_TSourceM]:
        ...

    def match(self, pattern: Any) -> Any:
        """Match result with pattern."""

        case: Case[Iterable[Union[_TSource, _TError]]] = Case(self)
        return case(pattern) if pattern else case

    @abstractmethod
    def is_error(self) -> bool:
        """Returns `True` if the result is an `Error` value."""

        raise NotImplementedError

    @abstractmethod
    def is_ok(self) -> bool:
        """Returns `True` if the result is an `Ok` value."""

        raise NotImplementedError

    def __eq__(self, o: Any) -> bool:
        raise NotImplementedError

    @abstractmethod
    def __iter__(self) -> Iterator[_TSource]:
        raise NotImplementedError

    def __repr__(self) -> str:
        return str(self)


class Ok(Result[_TSource, _TError], SupportsMatch[_TSource]):
    """The Ok result case class."""

    def __init__(self, value: _TSource) -> None:
        self._value = value

    @property
    def value(self) -> _TSource:
        return self._value

    def map(self, mapper: Callable[[_TSource], _TResult]) -> Result[_TResult, _TError]:
        return Ok(mapper(self._value))

    def bind(
        self, mapper: Callable[[_TSource], Result[_TResult, _TError]]
    ) -> Result[_TResult, _TError]:
        return mapper(self._value)

    def map_error(
        self, mapper: Callable[[_TError], _TResult]
    ) -> Result[_TSource, _TResult]:
        """Return a result of the error value after applying the mapping
        function, or Ok if the input is Ok."""
        return Ok(self._value)

    def is_error(self) -> bool:
        """Returns `True` if the result is an `Ok` value."""

        return False

    def is_ok(self) -> bool:
        """Returns `True` if the result is an `Ok` value."""

        return True

    def __match__(self, pattern: Any) -> Iterable[_TSource]:
        if self is pattern or self == pattern:
            return [self.value]

        try:
            origin: Any = get_origin(pattern)
            if isinstance(self, origin or pattern):
                return [self.value]
        except TypeError:
            pass

        return []

    def __eq__(self, o: Any) -> bool:
        if isinstance(o, Ok):
            return self.value == o.value  # type: ignore
        return False

    def __iter__(self) -> Generator[_TSource, _TSource, _TSource]:
        """Return iterator for Ok case."""
        return (yield self._value)

    def __str__(self):
        return f"Ok {self._value}"


class ResultException(EffectError):
    """Makes the Error case a valid exception for effect handling. Do
    not use directly."""

    def __init__(self, message: str):
        self.message = message


class Error(ResultException, Result[_TSource, _TError]):
    """The Error result case class."""

    def __init__(self, error: _TError) -> None:
        super().__init__(str(error))
        self._error = error

    @property
    def error(self) -> _TError:
        return self._error

    def map(self, mapper: Callable[[_TSource], _TResult]) -> Result[_TResult, _TError]:
        return Error(self._error)

    def bind(
        self, mapper: Callable[[_TSource], Result[_TResult, _TError]]
    ) -> Result[_TResult, _TError]:
        return Error(self._error)

    def map_error(
        self, mapper: Callable[[_TError], _TResult]
    ) -> Result[_TSource, _TResult]:
        """Return a result of the error value after applying the mapping
        function, or Ok if the input is Ok."""
        return Error(mapper(self._error))

    def is_error(self) -> bool:
        """Returns `True` if the result is an `Ok` value."""
        return True

    def is_ok(self) -> bool:
        """Returns `True` if the result is an `Ok` value."""
        return False

    def __match__(self, pattern: Any) -> Iterable[_TError]:
        if self is pattern or self == pattern:
            return [self.error]

        try:
            origin: Any = get_origin(pattern)
            if isinstance(self, origin or pattern):
                return [self.error]
        except TypeError:
            pass

        return []

    def __eq__(self, o: Any) -> bool:
        if isinstance(o, Error):
            return self.error == o.error  # type: ignore
        return False

    def __iter__(self) -> Iterator[_TSource]:
        """Return iterator for Error case."""

        # Raise class here so sub-classes like Failure works as well.
        raise self.__class__(self._error)

        # We're a generator
        while False:
            yield

    def __str__(self):
        return f"Error {self._error}"


def map(
    mapper: Callable[[_TSource], _TResult]
) -> Callable[[Result[_TSource, _TError]], Result[_TResult, _TError]]:
    def _map(result: Result[_TSource, _TError]) -> Result[_TResult, _TError]:
        return result.map(mapper)

    return _map


def bind(
    mapper: Callable[[_TSource], Result[_TResult, Any]]
) -> Callable[[Result[_TSource, _TError]], Result[_TResult, _TError]]:
    def _bind(result: Result[_TSource, _TError]) -> Result[_TResult, _TError]:
        return result.bind(mapper)

    return _bind


__all__ = [
    "Result",
    "Ok",
    "Error",
    "map",
    "bind",
]
