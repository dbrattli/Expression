"""Option module.

Contains a collection of static methods (functions) for operating on
options. All functions takes the source as the last curried
argument, i.e all functions returns a function that takes the source
sequence as the only argument.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Generator,
    Iterable,
    Iterator,
    List,
    Optional,
    TypeVar,
    Union,
    cast,
    get_origin,
    overload,
)

from .error import EffectError
from .match import MatchMixin, SupportsMatch
from .pipe import pipe

if TYPE_CHECKING:
    from ..collections.seq import Seq

TSource = TypeVar("TSource")
TSourceIn = TypeVar("TSourceIn", contravariant=True)
TResult = TypeVar("TResult")
TResultOut = TypeVar("TResultOut", covariant=True)
T1 = TypeVar("T1")
T2 = TypeVar("T2")
T3 = TypeVar("T3")
T4 = TypeVar("T4")


class Option(Iterable[TSource], MatchMixin[TSource], SupportsMatch[Union[TSource, bool]], ABC):
    """Option abstract base class."""

    @overload
    def pipe(self, __fn1: Callable[[Option[TSource]], TResult]) -> TResult:
        ...

    @overload
    def pipe(self, __fn1: Callable[[Option[TSource]], T1], __fn2: Callable[[T1], T2]) -> T2:
        ...

    @overload
    def pipe(self, __fn1: Callable[[Option[TSource]], T1], __fn2: Callable[[T1], T2], __fn3: Callable[[T2], T3]) -> T3:
        ...

    @overload
    def pipe(
        self,
        __fn1: Callable[[Option[TSource]], T1],
        __fn2: Callable[[T1], T2],
        __fn3: Callable[[T2], T3],
        __fn4: Callable[[T3], T4],
    ) -> T4:
        ...

    def pipe(self, *args: Any) -> Any:
        """Pipe option through the given functions."""
        return pipe(self, *args)

    def default_value(self, value: TSource) -> TSource:
        """Get with default value.

        Gets the value of the option if the option is Some, otherwise
        returns the specified default value.
        """
        raise NotImplementedError

    @abstractmethod
    def map(self, mapper: Callable[[TSource], TResult]) -> Option[TResult]:
        raise NotImplementedError

    @abstractmethod
    def map2(self, mapper: Callable[[TSource, T2], TResult], other: Option[T2]) -> Option[TResult]:
        raise NotImplementedError

    @abstractmethod
    def bind(self, mapper: Callable[[TSource], Option[TResult]]) -> Option[TResult]:
        """Bind option.

        Applies and returns the result of the mapper if the value is
        `Some`. If the value is `Nothing` then `Nothing` is returned.

        Args:
            mapper: A function that takes the value of type TSource from
                an option and transforms it into an option containing a
                value of type TResult.

        Returns:
            An option of the output type of the mapper.
        """
        raise NotImplementedError

    @abstractmethod
    def or_else(self, if_none: Option[TSource]) -> Option[TSource]:
        """Returns option if it is Some, otherwise returns `if_one`."""
        raise NotImplementedError

    @abstractmethod
    def or_else_with(self, if_none: Callable[[], Option[TSource]]) -> Option[TSource]:
        """Returns option if it is Some,
        otherwise evaluates the given function and returns the result."""
        raise NotImplementedError

    @abstractmethod
    def filter(self, predicate: Callable[[TSource], bool]) -> Option[TSource]:
        """Returns the input if the predicate evaluates to true,
        otherwise returns `Nothing`"""
        raise NotImplementedError

    @abstractmethod
    def to_list(self) -> List[TSource]:
        raise NotImplementedError

    @abstractmethod
    def to_seq(self) -> Seq[TSource]:
        raise NotImplementedError

    @abstractmethod
    def is_some(self) -> bool:
        """Returns true if the option is not Nothing."""
        raise NotImplementedError

    @abstractmethod
    def is_none(self) -> bool:
        """Returns true if the option is Nothing."""
        raise NotImplementedError

    @classmethod
    def of_obj(cls, value: TSource) -> Option[TSource]:
        """Convert object to an option."""
        return of_optional(value)

    @classmethod
    def of_optional(cls, value: Optional[TSource]) -> Option[TSource]:
        """Convert optional value to an option."""
        return of_optional(value)

    @property
    @abstractmethod
    def value(self) -> TSource:
        """Returns the value wrapped by the option.

        A `ValueError` is raised if the option is `Nothing`.
        """
        raise NotImplementedError

    @abstractmethod
    def __eq__(self, o: Any) -> bool:
        raise NotImplementedError

    @abstractmethod
    def __lt__(self, other: Any) -> bool:
        raise NotImplementedError

    def __repr__(self) -> str:
        return self.__str__()


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

    def map(self, mapper: Callable[[TSource], TResult]) -> Option[TResult]:
        return Some(mapper(self._value))

    def map2(self, mapper: Callable[[TSource, T2], TResult], other: Option[T2]) -> Option[TResult]:
        if isinstance(other, Some):
            return Some(mapper(self._value, cast(Some[T2], other).value))
        return Nothing

    def bind(self, mapper: Callable[[TSource], Option[TResult]]) -> Option[TResult]:
        """Bind option.

        Applies and returns the result of the mapper if the value is
        `Some`. If the value is `Nothing` then `Nothing` is returned.

        Args:
            mapper: A function that takes the value of type TSource from
                an option and transforms it into an option containing a
                value of type TResult.

        Returns:
            An option of the output type of the mapper.
        """
        return mapper(self._value)

    def or_else(self, if_none: Option[TSource]) -> Option[TSource]:
        """Returns `self`."""
        return self

    def or_else_with(self, if_none: Callable[[], Option[TSource]]) -> Option[TSource]:
        """Returns `self`."""
        return self

    def filter(self, predicate: Callable[[TSource], bool]) -> Option[TSource]:
        """Returns the input if the predicate evaluates to true,
        otherwise returns `Nothing`"""
        return self if predicate(self._value) else Nothing

    def to_list(self) -> List[TSource]:
        return [self._value]

    def to_seq(self) -> Seq[TSource]:
        from expression.collections.seq import Seq  # deferred import to avoid circular dependencies

        return Seq.of(self._value)

    @property
    def value(self) -> TSource:
        """Returns the value wrapped by the option.

        A `ValueError` is raised if the option is `Nothing`.
        """
        return self._value

    def __match__(self, pattern: Any) -> Iterable[TSource]:
        if self is pattern or self == pattern:
            return [self.value]

        try:
            origin: Any = get_origin(pattern)
            if isinstance(self, origin or pattern):
                return [self.value]
        except TypeError:
            pass

        return []

    def __lt__(self, other: Any) -> bool:
        if isinstance(other, Some):
            return self._value < other._value  # type: ignore
        return False

    def __eq__(self, o: Any) -> bool:
        if isinstance(o, Some):
            return self._value == o._value  # type: ignore
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

    def map(self, mapper: Callable[[TSource], TResult]) -> Option[TResult]:
        return Nothing

    def map2(self, mapper: Callable[[TSource, T2], TResult], other: Option[T2]) -> Option[TResult]:
        return Nothing

    def bind(self, mapper: Callable[[TSource], Option[TResult]]) -> Option[TResult]:
        """Bind option.

        Applies and returns the result of the mapper if the value is
        `Some`. If the value is `Nothing` then `Nothing` is returned.

        Args:
            mapper: A function that takes the value of type TSource from
                an option and transforms it into an option containing a
                value of type TResult.

        Returns:
            An option of the output type of the mapper.
        """
        return Nothing

    def or_else(self, if_none: Option[TSource]) -> Option[TSource]:
        """Returns `if_none`."""
        return if_none

    def or_else_with(self, if_none: Callable[[], Option[TSource]]) -> Option[TSource]:
        """Evaluates `if_none` and returns the result."""
        return if_none()

    def filter(self, predicate: Callable[[TSource], bool]) -> Option[TSource]:
        return Nothing

    def to_list(self) -> List[TSource]:
        return []

    def to_seq(self) -> Seq[TSource]:
        from expression.collections.seq import Seq  # deferred import to avoid circular dependencies

        return Seq()

    @property
    def value(self) -> TSource:
        """Returns the value wrapped by the option.

        A `ValueError` is raised if the option is `Nothing`.
        """

        raise ValueError("There is no value.")

    def __match__(self, pattern: Any) -> Iterable[bool]:
        if self is pattern:
            return [True]

        return []

    def __iter__(self) -> Iterator[TSource]:
        """Return iterator for the `Nothing` case.

        We basically want to return nothing, but we have to return
        something to signal fail.
        """

        raise Nothing
        while False:
            yield

    def __lt__(self, other: Any) -> bool:
        return True

    def __eq__(self, o: Any) -> bool:
        if o is Nothing:
            return True
        return False

    def __str__(self):
        return "Nothing"


# The singleton None class. We use the name 'Nothing' here instead of `None` to
# avoid conflicts with the builtin `None` value in Python.
# Note to self: Must be of type `Nothing_` or pattern matching will not work.
Nothing: Nothing_[Any] = Nothing_()
"""Singleton `Nothing` object.

Since Nothing is a singleton it can be tested e.g using `is`:
    >>> if xs is Nothing:
    ...     return True
"""


def bind(mapper: Callable[[TSource], Option[TResult]]) -> Callable[[Option[TSource]], Option[TResult]]:
    """Bind option.

    Applies and returns the result of the mapper if the value is
    `Some`. If the value is `Nothing` then `Nothing` is returned.

    Args:
        mapper: A function that takes the value of type TSource from
            an option and transforms it into an option containing a
            value of type TResult.

    Returns:
        A partially applied function that takes an option and returns an
        option of the output type of the mapper.
    """

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


def is_none(option: Option[Any]) -> bool:
    return option.is_none()


def is_some(option: Option[Any]) -> bool:
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


def to_seq(option: Option[TSource]) -> Seq[TSource]:
    return option.to_seq()


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

    return Some(value)


def of_obj(value: Any) -> Option[Any]:
    """Convert object to an option.

    Convert a value that could be `None` into an `Option` value.

    Args:
        value: The input object.

    Return:
        The result option.
    """
    return of_optional(value)


def default_arg(value: Option[TSource], default_value: TSource) -> TSource:
    """Specify default argument.

    Used to specify a default value for an optional argument in the
    implementation of a function. Same as `default_value`, but
    "uncurried" and with the arguments swapped.
    """
    return value.default_value(default_value)


__all__ = [
    "Option",
    "Some",
    "Nothing",
    "Nothing_",
    "bind",
    "default_arg",
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
