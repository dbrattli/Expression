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
    Dict,
    Generator,
    Generic,
    Iterable,
    Iterator,
    List,
    TypeVar,
    Union,
    cast,
    get_origin,
)

from typing_extensions import TypeGuard

from .curry import curry_flip
from .error import EffectError
from .pipe import PipeMixin
from .typing import GenericValidator, ModelField, SupportsValidation

_TSource = TypeVar("_TSource")
_TOther = TypeVar("_TOther")
_TResult = TypeVar("_TResult")
_TError = TypeVar("_TError")


def _validate(result: Any, field: ModelField) -> Result[Any, Any]:
    if isinstance(result, Result):
        return cast(Result[Any, Any], result)

    if not isinstance(result, Dict):
        raise ValueError("not result type")

    try:
        value: Any = result["ok"]
        if field.sub_fields:
            sub_field = field.sub_fields[0]
            value, err = sub_field.validate(value, {}, loc="Result")
            if err:
                raise ValueError(str(err))
        return Ok(value)
    except KeyError:
        try:
            error: Any = result["error"]
            sub_field = field.sub_fields[1]
            error, err = sub_field.validate(error, {}, loc="Result")
            if err:
                raise ValueError(str(err))
            return Error(error)
        except KeyError:
            raise ValueError("not a result")


class Result(
    Iterable[_TSource],
    PipeMixin,
    SupportsValidation["Result[_TSource, _TError]"],
    Generic[_TSource, _TError],
    ABC,
):
    """The result abstract base class."""

    __validators__: List[GenericValidator[Result[_TSource, _TError]]] = [_validate]

    @abstractmethod
    def default_value(self, value: _TSource) -> _TSource:
        """Get with default value.

        Gets the value of the option if the option is Some, otherwise
        returns the specified default value.
        """
        raise NotImplementedError

    @abstractmethod
    def default_with(self, getter: Callable[[_TError], _TSource]) -> _TSource:
        """Get with default value lazily.

        Gets the value of the option if the option is Some, otherwise
        returns the value produced by the getter
        """
        raise NotImplementedError

    @abstractmethod
    def map(self, mapper: Callable[[_TSource], _TResult]) -> Result[_TResult, _TError]:
        raise NotImplementedError

    @abstractmethod
    def map2(
        self,
        other: Ok[_TOther, _TError] | Error[_TOther, _TError],
        mapper: Callable[[_TSource, _TOther], _TResult],
    ) -> Result[_TResult, _TError]:
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

    @abstractmethod
    def is_error(self) -> TypeGuard[Error[_TSource, _TError]]:
        """Returns `True` if the result is an `Error` value."""

        raise NotImplementedError

    @abstractmethod
    def is_ok(self) -> TypeGuard[Ok[_TSource, _TError]]:
        """Returns `True` if the result is an `Ok` value."""

        raise NotImplementedError

    @abstractmethod
    def dict(self) -> Dict[str, Union[_TSource, _TError]]:
        """Returns a json serializable representation of the result."""
        raise NotImplementedError

    def __eq__(self, o: Any) -> bool:
        raise NotImplementedError

    @abstractmethod
    def __iter__(self) -> Iterator[_TSource]:
        raise NotImplementedError

    def __repr__(self) -> str:
        return str(self)

    @classmethod
    def __get_validators__(
        cls,
    ) -> Iterator[GenericValidator[Result[_TSource, _TError]]]:
        yield from cls.__validators__

    @abstractmethod
    def __hash__(self) -> int:
        raise NotImplementedError


class Ok(Result[_TSource, _TError]):
    """The Ok result case class."""

    __match_args__ = ("value",)

    def default_value(self, value: _TSource) -> _TSource:
        """Get with default value.

        Gets the value of the option if the option is Some, otherwise
        returns the specified default value.
        """
        return self._value

    def default_with(self, getter: Callable[[_TError], _TSource]) -> _TSource:
        """Get with default value lazily.

        Gets the value of the option if the option is Some, otherwise
        returns the value produced by the getter
        """
        return self._value

    def __init__(self, value: _TSource) -> None:
        self._value = value

    @property
    def value(self) -> _TSource:
        return self._value

    def map(self, mapper: Callable[[_TSource], _TResult]) -> Result[_TResult, _TError]:
        return Ok(mapper(self._value))

    def map2(
        self,
        other: Ok[_TOther, _TError] | Error[_TOther, _TError],
        mapper: Callable[[_TSource, _TOther], _TResult],
    ) -> Result[_TResult, _TError]:
        return other.map(lambda value: mapper(self._value, value))

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

    def is_error(self) -> TypeGuard[Error[_TSource, _TError]]:
        """Returns `True` if the result is an `Ok` value."""

        return False

    def is_ok(self) -> TypeGuard[Ok[_TSource, _TError]]:
        """Returns `True` if the result is an `Ok` value."""

        return True

    def dict(self) -> Dict[str, _TSource | _TError]:
        """Returns a json string representation of the ok value."""
        attr = getattr(self._value, "dict", None) or getattr(self._value, "dict", None)
        if attr and callable(attr):
            value = attr()
        else:
            value = self._value

        return {"ok": value}

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

    def __hash__(self) -> int:
        return hash(self._value)


class ResultException(EffectError):
    """Makes the Error case a valid exception for effect handling. Do
    not use directly."""

    def __init__(self, message: str):
        self.message = message


class Error(
    ResultException,
    Result[_TSource, _TError],
):
    """The Error result case class."""

    __match_args__ = ("error",)

    def __init__(self, error: _TError) -> None:
        super().__init__(str(error))
        self._error = error

    def default_value(self, value: _TSource) -> _TSource:
        """Get with default value.

        Gets the value of the option if the option is Some, otherwise
        returns the specified default value.
        """
        return value

    def default_with(self, getter: Callable[[_TError], _TSource]) -> _TSource:
        """Get with default value lazily.

        Gets the value of the option if the option is Some, otherwise
        returns the value produced by the getter
        """
        return getter(self._error)

    @property
    def error(self) -> _TError:
        return self._error

    def map(self, mapper: Callable[[_TSource], _TResult]) -> Result[_TResult, _TError]:
        return Error(self._error)

    def map2(
        self,
        other: Result[_TOther, _TError],
        mapper: Callable[[_TSource, _TOther], _TResult],
    ) -> Result[_TResult, _TError]:
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

    def is_error(self) -> TypeGuard[Error[_TSource, _TError]]:
        """Returns `True` if the result is an `Ok` value."""
        return True

    def is_ok(self) -> TypeGuard[Ok[_TSource, _TError]]:
        """Returns `True` if the result is an `Ok` value."""
        return False

    def dict(self) -> Dict[str, Any]:
        """Returns a json serializable representation of the error value."""
        attr = getattr(self._error, "dict") or getattr(self._error, "dict")
        if callable(attr):
            error = attr()
        else:
            error = self._error

        return {"error": error}

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

    def __hash__(self) -> int:
        return hash(self._error)


def default_value(value: _TSource) -> Callable[[Result[_TSource, Any]], _TSource]:
    """Gets the value of the option if the option is Some, otherwise
    returns the specified default value.
    """

    def _default_value(result: Result[_TSource, Any]) -> _TSource:
        return result.default_value(value)

    return _default_value


def default_with(
    getter: Callable[[_TError], _TSource]
) -> Callable[[Result[_TSource, _TError]], _TSource]:
    """Get with default value lazily.

    Gets the value of the option if the option is Some, otherwise
    returns the value produced by the getter
    """

    def _default_with(result: Result[_TSource, _TError]) -> _TSource:
        return result.default_with(getter)

    return _default_with


@curry_flip(1)
def map(
    result: Result[_TSource, _TError], mapper: Callable[[_TSource], _TResult]
) -> Result[_TResult, _TError]:
    return result.map(mapper)


@curry_flip(2)
def map2(
    x: Ok[_TSource, _TError] | Error[_TSource, _TError],
    y: Ok[_TOther, _TError] | Error[_TOther, _TError],
    mapper: Callable[[_TSource, _TOther], _TResult],
) -> Result[_TResult, _TError]:
    return x.map2(y, mapper)


@curry_flip(1)
def bind(
    result: Result[_TSource, _TError],
    mapper: Callable[[_TSource], Result[_TResult, Any]],
) -> Result[_TResult, _TError]:
    return result.bind(mapper)


def dict(source: Result[_TSource, _TError]) -> Dict[str, Union[_TSource, _TError]]:
    return source.dict()


__all__ = [
    "Result",
    "Ok",
    "Error",
    "default_value",
    "default_with",
    "map",
    "bind",
    "dict",
]
