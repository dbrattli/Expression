"""Option module.

Contains a collection of static methods (functions) for operating on
options. All functions takes the source as the last curried
argument, i.e all functions returns a function that takes the source
sequence as the only argument.
"""
from abc import abstractmethod
from typing import Optional, TypeVar, Callable, List, Iterable, Iterator, Any

TSource = TypeVar("TSource")
TResult = TypeVar("TResult")
T1 = TypeVar("T1")
T2 = TypeVar("T2")


class Option(Iterable[TSource]):
    """Option abstract base class."""

    @abstractmethod
    def map(self, mapper: Callable[[TSource], TResult]) -> "Option[TResult]":
        raise NotImplementedError

    def match(self, *args, **kw):
        from pampy import match
        return match(self, *args, **kw)

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
    def to_list(cls) -> List[TSource]:
        raise NotImplementedError

    @abstractmethod
    def to_seq(cls) -> Iterable[TSource]:
        raise NotImplementedError

    @abstractmethod
    def is_some(cls) -> bool:
        """Returns true if the option is not Nothing."""
        raise NotImplementedError

    @abstractmethod
    def is_none(cls) -> bool:
        """Returns true if the option is Nothing."""
        raise NotImplementedError

    @abstractmethod
    def __eq__(self, other):
        raise NotImplementedError

    def __repr__(self):
        return self.__str__()


class Some(Option[TSource]):
    """The Some option case class."""

    def __init__(self, value: TSource) -> None:
        self._value = value

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
            return Some(mapper(self._value, other.value))
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
    def value(self):
        """Returns the value wrapped by the option.

        This is safe since the property is only defined on `Some` and not on either `Option` or `None`.
        """
        return self._value

    def __eq__(self, other):
        if isinstance(other, Some):
            return self._value == other._value
        return False

    def __iter__(self) -> Iterator[TSource]:
        return (yield self._value)

    def __str__(self):
        return f"Some {self._value}"


class _None(Option[TSource]):
    """The None option case class.

    Do not use. Use the singleton `Nothing` instead. Since Nothing is a
    singleton it can be tested e.g using `is`:
        >>> if xs is Nothing:
        ...     return True
    """

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

    def __iter__(self) -> Iterator[TSource]:
        """Return iterator for the `Nothing` case.

        We basically want to return nothing, but we have to return
        something to signal fail

        Raises:
            GeneratorExit
        """
        raise GeneratorExit
        yield  # Just to make it a generator

    def __eq__(self, other):
        if other is Nothing:
            return True
        return False

    def __str__(self):
        return "Nothing"


# The singleton None class. We use the name 'Nothing' here instead of `None` to
# avoid conflicts with the builtin `None` value.
Nothing: _None = _None()
"""Singleton `Nothing` object.

Since Nothing is a singleton it can be tested e.g using `is`:
    >>> if xs is Nothing:
    ...     return True
"""


def map(mapper: Callable[[TSource], TResult]) -> Callable[[Option[TSource]], Option[TResult]]:
    def _map(option: Option[TSource]) -> Option[TResult]:
        return option.map(mapper)

    return _map


def map2(mapper: Callable[[T1, T2], TResult]) -> Callable[[Option[T1], Option[T2]], Option[TResult]]:
    def _map2(opt1: Option[T1], opt2: Option[T2]) -> Option[TResult]:
        return opt1.map2(mapper, opt2)

    return _map2


def bind(mapper: Callable[[TSource], Option[TResult]]) -> Callable[[Option[TSource]], Option[TResult]]:
    def _bind(option: Option[TSource]) -> Option[TResult]:
        return option.bind(mapper)

    return _bind


def is_none(option: Option[TSource]) -> bool:
    return option.is_none()


def is_some(option: Option[TSource]) -> bool:
    return option.is_some()


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
    else:
        return Some(value)


__all__ = [
    "Option",
    "Some",
    "Nothing",
    "_None",
    "map",
    "map2",
    "bind",
    "is_none",
    "is_some",
    "or_else",
    "to_list",
    "to_seq",
    "of_optional",
    "of_obj",
]
