"""Option module.

Contains a collection of static methods (functions) for operating on
options. All functions takes the source as the last curried argument,
i.e all functions returns a function that takes the source sequence as
the only argument.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Generator,
    Iterable,
    Iterator,
    List,
    Optional,
    TypeVar,
    cast,
)

from typing_extensions import TypeGuard

from .curry import curry_flip
from .error import EffectError
from .pipe import PipeMixin
from .typing import GenericValidator, ModelField, SupportsValidation

if TYPE_CHECKING:
    from ..collections.seq import Seq

_TSource = TypeVar("_TSource")
_TResult = TypeVar("_TResult")

_T1 = TypeVar("_T1")
_T2 = TypeVar("_T2")


def _validate(value: Any, field: ModelField) -> Option[Any]:
    if isinstance(value, Option):
        return cast(Option[Any], value)

    if isinstance(value, Dict) and not value:
        return Nothing

    if field.sub_fields:
        sub_field = field.sub_fields[0]
        value, error = sub_field.validate(value, {}, loc="Option")
        if error:
            raise ValueError(str(error))

    return Some(cast(Any, value))


class Option(
    Iterable[_TSource],
    PipeMixin,
    SupportsValidation["Option[_TSource]"],
    ABC,
):
    """Option abstract base class."""

    __validators__: List[GenericValidator[Option[_TSource]]] = [_validate]

    @abstractmethod
    def default_value(self, value: _TSource) -> _TSource:
        """Get with default value.

        Gets the value of the option if the option is Some, otherwise
        returns the specified default value.
        """
        raise NotImplementedError

    @abstractmethod
    def default_with(self, getter: Callable[[], _TSource]) -> _TSource:
        """Get with default value lazily.

        Gets the value of the option if the option is Some, otherwise
        returns the value produced by the getter
        """
        raise NotImplementedError

    @abstractmethod
    def map(self, mapper: Callable[[_TSource], _TResult]) -> Option[_TResult]:
        raise NotImplementedError

    @abstractmethod
    def map2(
        self, mapper: Callable[[_TSource, _T2], _TResult], other: Option[_T2]
    ) -> Option[_TResult]:
        raise NotImplementedError

    @abstractmethod
    def bind(self, mapper: Callable[[_TSource], Option[_TResult]]) -> Option[_TResult]:
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
    def or_else(self, if_none: Option[_TSource]) -> Option[_TSource]:
        """Returns option if it is Some, otherwise returns `if_one`."""
        raise NotImplementedError

    @abstractmethod
    def or_else_with(self, if_none: Callable[[], Option[_TSource]]) -> Option[_TSource]:
        """Returns option if it is Some,
        otherwise evaluates the given function and returns the result."""
        raise NotImplementedError

    @abstractmethod
    def filter(self, predicate: Callable[[_TSource], bool]) -> Option[_TSource]:
        """Returns the input if the predicate evaluates to true,
        otherwise returns `Nothing`"""
        raise NotImplementedError

    @abstractmethod
    def to_list(self) -> List[_TSource]:
        raise NotImplementedError

    @abstractmethod
    def to_seq(self) -> Seq[_TSource]:
        raise NotImplementedError

    @abstractmethod
    def is_some(self) -> TypeGuard[Some[_TSource]]:
        """Returns true if the option is not Nothing."""
        raise NotImplementedError

    @abstractmethod
    def is_none(self) -> TypeGuard[Nothing_[_TSource]]:
        """Returns true if the option is Nothing."""
        raise NotImplementedError

    @classmethod
    def of_obj(cls, value: _TSource) -> Option[_TSource]:
        """Convert object to an option."""
        return of_optional(value)

    @classmethod
    def of_optional(cls, value: Optional[_TSource]) -> Option[_TSource]:
        """Convert optional value to an option."""
        return of_optional(value)

    @abstractmethod
    def dict(self) -> Optional[_TSource]:
        """Returns a json string representation of the option."""
        raise NotImplementedError

    @property
    @abstractmethod
    def value(self) -> _TSource:
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

    @classmethod
    def __get_validators__(cls) -> Iterator[GenericValidator[Option[_TSource]]]:
        yield from cls.__validators__

    @abstractmethod
    def __hash__(self) -> int:
        raise NotImplementedError


class Some(Option[_TSource]):
    """The Some option case class."""

    __match_args__ = ("value",)

    def __init__(self, value: _TSource) -> None:
        self._value = value

    def default_value(self, value: _TSource) -> _TSource:
        """Gets the value of the option if the option is Some, otherwise
        returns the specified default value.
        """
        return self._value

    def default_with(self, getter: Callable[[], _TSource]) -> _TSource:
        """Get with default value.

        Gets the value of the option if the option is Some, otherwise
        returns the value produced by the getter
        """
        return self._value

    def is_some(self) -> TypeGuard[Some[_TSource]]:
        """Returns `True`."""
        return True

    def is_none(self) -> TypeGuard[Nothing_[_TSource]]:
        """Returns `False`."""
        return False

    def map(self, mapper: Callable[[_TSource], _TResult]) -> Option[_TResult]:
        return Some(mapper(self._value))

    def map2(
        self, mapper: Callable[[_TSource, _T2], _TResult], other: Option[_T2]
    ) -> Option[_TResult]:
        if isinstance(other, Some):
            return Some(mapper(self._value, other.value))
        return Nothing

    def bind(self, mapper: Callable[[_TSource], Option[_TResult]]) -> Option[_TResult]:
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

    def or_else(self, if_none: Option[_TSource]) -> Option[_TSource]:
        """Returns `self`."""
        return self

    def or_else_with(self, if_none: Callable[[], Option[_TSource]]) -> Option[_TSource]:
        """Returns `self`."""
        return self

    def filter(self, predicate: Callable[[_TSource], bool]) -> Option[_TSource]:
        """Returns the input if the predicate evaluates to true,
        otherwise returns `Nothing`"""
        return self if predicate(self._value) else Nothing

    def to_list(self) -> List[_TSource]:
        return [self._value]

    def to_seq(self) -> Seq[_TSource]:
        # deferred import to avoid circular dependencies
        from expression.collections.seq import Seq

        return Seq.of(self._value)

    def dict(self) -> Optional[_TSource]:
        attr = getattr(self._value, "dict", None) or getattr(self._value, "dict", None)
        if attr and callable(attr):
            value = attr()
        else:
            value = self._value

        return value

    @property
    def value(self) -> _TSource:
        """Returns the value wrapped by the option.

        A `ValueError` is raised if the option is `Nothing`.
        """
        return self._value

    def __lt__(self, other: Any) -> bool:
        if isinstance(other, Some):
            return self._value < other._value  # type: ignore
        return False

    def __eq__(self, o: Any) -> bool:
        if isinstance(o, Some):
            return self._value == o._value  # type: ignore
        return False

    def __iter__(self) -> Generator[_TSource, _TSource, _TSource]:
        return (yield self._value)

    def __str__(self) -> str:
        return f"Some {self._value}"

    def __hash__(self) -> int:
        return hash(self._value)


class Nothing_(Option[_TSource], EffectError):
    """The None option case class.

    Do not use. Use the singleton `Nothing` instead. Since Nothing is a
    singleton it can be tested e.g using `is`:
        >>> if xs is Nothing:
        ...     return True
    """

    def default_value(self, value: _TSource) -> _TSource:
        """Gets the value of the option if the option is Some, otherwise
        returns the specified default value.
        """
        return value

    def default_with(self, getter: Callable[[], _TSource]) -> _TSource:
        """Get with default value.

        Gets the value of the option if the option is Some, otherwise
        returns the value produced by the getter
        """
        return getter()

    def is_some(self) -> TypeGuard[Some[_TSource]]:
        """Returns `False`."""
        return False

    def is_none(self) -> TypeGuard[Nothing_[_TSource]]:
        """Returns `True`."""
        return True

    def map(self, mapper: Callable[[_TSource], _TResult]) -> Option[_TResult]:
        return Nothing

    def map2(
        self, mapper: Callable[[_TSource, _T2], _TResult], other: Option[_T2]
    ) -> Option[_TResult]:
        return Nothing

    def bind(self, mapper: Callable[[_TSource], Option[_TResult]]) -> Option[_TResult]:
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

    def or_else(self, if_none: Option[_TSource]) -> Option[_TSource]:
        """Returns `if_none`."""
        return if_none

    def or_else_with(self, if_none: Callable[[], Option[_TSource]]) -> Option[_TSource]:
        """Evaluates `if_none` and returns the result."""
        return if_none()

    def filter(self, predicate: Callable[[_TSource], bool]) -> Option[_TSource]:
        return Nothing

    def to_list(self) -> List[_TSource]:
        return []

    def to_seq(self) -> Seq[_TSource]:
        # deferred import to avoid circular dependencies
        from expression.collections.seq import Seq

        return Seq()

    def dict(self) -> _TSource | Dict[Any, Any]:
        return {}  # Pydantic cannot handle None or other types than Optional

    @property
    def value(self) -> _TSource:
        """Returns the value wrapped by the option.

        A `ValueError` is raised if the option is `Nothing`.
        """

        raise ValueError("There is no value.")

    def __iter__(self) -> Generator[_TSource, _TSource, _TSource]:
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

    def __hash__(self) -> int:
        return 0


# The singleton None class. We use the name 'Nothing' here instead of `None` to
# avoid conflicts with the builtin `None` value in Python.
# Note to self: Must be of type `Nothing_` or pattern matching will not work.
Nothing: Nothing_[Any] = Nothing_()
"""Singleton `Nothing` object.

Since Nothing is a singleton it can be tested e.g using `is`:
    >>> if xs is Nothing:
    ...     return True
"""


@curry_flip(1)
def bind(
    option: Option[_TSource], mapper: Callable[[_TSource], Option[_TResult]]
) -> Option[_TResult]:
    """Bind option.

    Applies and returns the result of the mapper if the value is
    `Some`. If the value is `Nothing` then `Nothing` is returned.

    Args:
        mapper: A function that takes the value of type _TSource from
            an option and transforms it into an option containing a
            value of type TResult.

    Returns:
        A partially applied function that takes an option and returns an
        option of the output type of the mapper.
    """

    return option.bind(mapper)


@curry_flip(1)
def default_value(option: Option[_TSource], value: _TSource) -> _TSource:
    """Gets the value of the option if the option is Some, otherwise
    returns the specified default value.
    """

    return option.default_value(value)


def default_with(
    getter: Callable[[], _TSource]
) -> Callable[[Option[_TSource]], _TSource]:
    """Get with default value lazily.

    Gets the value of the option if the option is Some, otherwise
    returns the value produced by the getter
    """

    def _default_with(option: Option[_TSource]) -> _TSource:
        return option.default_with(getter)

    return _default_with


def is_none(option: Option[_TSource]) -> TypeGuard[Nothing_[_TSource]]:
    return option.is_none()


def is_some(option: Option[_TSource]) -> TypeGuard[Some[_TSource]]:
    return option.is_some()


@curry_flip(1)
def map(
    option: Option[_TSource], mapper: Callable[[_TSource], _TResult]
) -> Option[_TResult]:
    return option.map(mapper)


@curry_flip(2)
def map2(
    opt1: Option[_T1], opt2: Option[_T2], mapper: Callable[[_T1, _T2], _TResult]
) -> Option[_TResult]:
    return opt1.map2(mapper, opt2)


def or_else(
    option: Option[_TSource],
    if_none: Option[_TSource],
) -> Option[_TSource]:
    """Returns option if it is Some, otherwise returns `if_none`."""
    return option.or_else(if_none)


def to_list(option: Option[_TSource]) -> List[_TSource]:
    return option.to_list()


def to_seq(option: Option[_TSource]) -> Seq[_TSource]:
    return option.to_seq()


def of_optional(value: Optional[_TSource]) -> Option[_TSource]:
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


def dict(value: Option[_TSource]) -> _TSource | Dict[Any, Any] | None:
    return value.dict()


def default_arg(value: Option[_TSource], default_value: _TSource) -> _TSource:
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
    "default_with",
    "map",
    "map2",
    "is_none",
    "is_some",
    "or_else",
    "to_list",
    "dict",
    "to_seq",
    "of_optional",
    "of_obj",
]
