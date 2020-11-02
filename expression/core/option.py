"""Option module.

Contains a collection of static methods (functions) for operating on
options. All functions takes the source as the last curried
argument, i.e all functions returns a function that takes the source
sequence as the only argument.
"""
from abc import ABC, abstractmethod, abstractproperty
from typing import Any, Callable, Generator, Iterable, Iterator, List, Optional, TypeVar, cast, overload

from .error import EffectError
from .pipe import pipe

TSource = TypeVar("TSource")
TResult = TypeVar("TResult")
T1 = TypeVar("T1")
T2 = TypeVar("T2")
T3 = TypeVar("T3")
T4 = TypeVar("T4")


class Option(Iterable[TSource], ABC):
    """Option abstract base class."""

    @overload
    def pipe(self, __fn1: Callable[["Option[TSource]"], TResult]) -> TResult:
        ...

    @overload
    def pipe(self, __fn1: Callable[["Option[TSource]"], T1], __fn2: Callable[[T1], T2]) -> T2:
        ...

    @overload
    def pipe(
        self, __fn1: Callable[["Option[TSource]"], T1], __fn2: Callable[[T1], T2], __fn3: Callable[[T2], T3]
    ) -> T3:
        ...

    @overload
    def pipe(
        self,
        __fn1: Callable[["Option[TSource]"], T1],
        __fn2: Callable[[T1], T2],
        __fn3: Callable[[T2], T3],
        __fn4: Callable[[T3], T4],
    ) -> T4:
        ...

    def pipe(self, *args: Any) -> Any:
        """Pipe option through the given functions."""
        return pipe(self, *args)

    def match(self, *args: Any, **kw: Any) -> Any:
        from pampy import match  # type: ignore

        return match(self, *args, **kw)  # type: ignore

    def default_value(self, value: TSource) -> TSource:
        """Gets the value of the option if the option is Some, otherwise
        returns the specified default value.
        """
        raise NotImplementedError

    @abstractmethod
    def map(self, mapper: Callable[[TSource], TResult]) -> "Option[TResult]":
        raise NotImplementedError

    @abstractmethod
    def map2(self, mapper: Callable[[TSource, T2], TResult], other: "Option[T2]") -> "Option[TResult]":
        raise NotImplementedError

    @abstractmethod
    def bind(self, mapper: Callable[[TSource], "Option[TResult]"]) -> "Option[TResult]":
        raise NotImplementedError

    @abstractmethod
    def or_else(self, if_none: "Option[TSource]") -> "Option[TSource]":
        """Returns option if it is Some, otherwise returns `if_one`. """
        raise NotImplementedError

    @abstractmethod
    def to_list(self) -> List[TSource]:
        raise NotImplementedError

    @abstractmethod
    def to_seq(self) -> Iterable[TSource]:
        raise NotImplementedError

    @abstractmethod
    def is_some(self) -> bool:
        """Returns true if the option is not Nothing."""
        raise NotImplementedError

    @abstractmethod
    def is_none(self) -> bool:
        """Returns true if the option is Nothing."""
        raise NotImplementedError

    @abstractmethod
    def __eq__(self, other: Any) -> bool:
        raise NotImplementedError

    def __repr__(self) -> str:
        return self.__str__()

    @abstractproperty
    def value(self) -> TSource:
        """Returns the value wrapped by the option.

        A `ValueError` is raised if the option is `Nothing`.
        """
        raise NotImplementedError


class Some(Option[TSource]):
    """The Some option case class."""

    def __init__(self, value: TSource) -> None:
        self._value = value

    def default_value(self, value: TSource) -> TSource:
        """Gets the value of the option if the option is Some, otherwise
        returns the specified default value.
        """
        return self._value

    def is_some(self) -> bool:
        """Returns `True`."""
        return True

    def is_none(self) -> bool:
        """Returns `False`."""
        return False

    def map(self, mapper: Callable[[TSource], TResult]):
        return Some(mapper(self._value))

    def map2(self, mapper: Callable[[TSource, T2], TResult], other: Option[T2]) -> Option[TResult]:
        if isinstance(other, Some):
            return Some(mapper(self._value, cast(Some[T2], other).value))
        return Nothing

    def bind(self, mapper: Callable[[TSource], Option[TResult]]) -> Option[TResult]:
        return mapper(self._value)

    def or_else(self, if_none: Option[TSource]) -> Option[TSource]:
        """Returns `self`."""
        return self

    def to_list(self) -> List[TSource]:
        return [self._value]

    def to_seq(self) -> Iterable[TSource]:
        return [self._value]

    @property
    def value(self) -> TSource:
        """Returns the value wrapped by the option.

        A `ValueError` is raised if the option is `Nothing`.
        """
        return self._value

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Some):
            return self._value == other._value  # type: ignore
        return False

    def __iter__(self) -> Generator[TSource, TSource, TSource]:
        return (yield self._value)

    def __str__(self) -> str:
        return f"Some {self._value}"


class Nothing_(Option[TSource], EffectError):
    """The None option case class.

    Do not use. Use the singleton `Nothing` instead. Since Nothing is a
    singleton it can be tested e.g using `is`:
        >>> if xs is Nothing:
        ...     return True
    """

    def default_value(self, value: TSource) -> TSource:
        """Gets the value of the option if the option is Some, otherwise
        returns the specified default value.
        """
        return value

    def is_some(self) -> bool:
        """Returns `False`."""
        return False

    def is_none(self) -> bool:
        """Returns `True`."""
        return True

    def map(self, mapper: Callable[[TSource], TResult]):
        return self

    def map2(self, mapper: Callable[[TSource, T2], TResult], other: Option[T2]) -> Option[TResult]:
        return Nothing

    def bind(self, mapper: Callable[[TSource], Option[TResult]]) -> Option[TResult]:
        return Nothing

    def or_else(self, if_none: Option[TSource]) -> Option[TSource]:
        """Returns `if_none`."""
        return if_none

    def to_list(self) -> List[TSource]:
        return []

    def to_seq(self) -> Iterable[TSource]:
        return []

    @property
    def value(self) -> TSource:
        """Returns the value wrapped by the option.

        A `ValueError` is raised if the option is `Nothing`.
        """

        raise ValueError("There is no value.")

    def __iter__(self) -> Iterator[TSource]:
        """Return iterator for the `Nothing` case.

        We basically want to return nothing, but we have to return
        something to signal fail.
        """
        raise Nothing
        yield

    def __eq__(self, other: Any) -> bool:
        if other is Nothing:
            return True
        return False

    def __str__(self):
        return "Nothing"


# The singleton None class. We use the name 'Nothing' here instead of `None` to
# avoid conflicts with the builtin `None` value.
Nothing: Nothing_[Any] = Nothing_()
"""Singleton `Nothing` object.

Since Nothing is a singleton it can be tested e.g using `is`:
    >>> if xs is Nothing:
    ...     return True
"""


def bind(mapper: Callable[[TSource], Option[TResult]]) -> Callable[[Option[TSource]], Option[TResult]]:
    def _bind(option: Option[TSource]) -> Option[TResult]:
        return option.bind(mapper)

    return _bind


def default_value(value: TSource) -> Callable[[Option[TSource]], TSource]:
    """Gets the value of the option if the option is Some, otherwise
    returns the specified default value.
    """

    def _default_value(option: Option[TSource]) -> TSource:
        return option.default_value(value)

    return _default_value


def is_none(option: Option[TSource]) -> bool:
    return option.is_none()


def is_some(option: Option[TSource]) -> bool:
    return option.is_some()


def map(mapper: Callable[[TSource], TResult]) -> Callable[[Option[TSource]], Option[TResult]]:
    def _map(option: Option[TSource]) -> Option[TResult]:
        return option.map(mapper)

    return _map


def map2(mapper: Callable[[T1, T2], TResult]) -> Callable[[Option[T1], Option[T2]], Option[TResult]]:
    def _map2(opt1: Option[T1], opt2: Option[T2]) -> Option[TResult]:
        return opt1.map2(mapper, opt2)

    return _map2


def or_else(if_none: Option[TSource]) -> Callable[[Option[TSource]], Option[TSource]]:
    """Returns option if it is Some, otherwise returns ifNone."""

    def _or_else(option: Option[TSource]) -> Option[TSource]:
        return option.or_else(if_none)

    return _or_else


def to_list(option: Option[TSource]) -> List[TSource]:
    return option.to_list()


def to_seq(option: Option[TSource]) -> Iterable[TSource]:
    return option.to_list()


def of_optional(value: Optional[TSource]) -> Option[TSource]:
    """Convert an optional value to an option.

    Convert a value that could be `None` into an `Option` value. Same as
    `of_obj` but with typed values.

    Args:
        value: The input optional value.

    Return:
        The result option.
    """
    if value is None:
        return Nothing
    else:
        return Some(value)


def of_obj(value: Any) -> Option[TSource]:
    """Convert object to an option.

    Convert a value that could be `None` into an `Option` value.

    Args:
        value: The input object.

    Return:
        The result option.
    """
    if value is None:
        return Nothing

    return Some(value)


__all__ = [
    "Option",
    "Some",
    "Nothing",
    "Nothing_",
    "bind",
    "default_value",
    "map",
    "map2",
    "is_none",
    "is_some",
    "or_else",
    "to_list",
    "to_seq",
    "of_optional",
    "of_obj",
]
