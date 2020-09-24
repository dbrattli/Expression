from abc import abstractmethod
from typing import Generic, Generator, Optional, TypeVar, Callable, List, Iterable, Iterator, Coroutine, cast, Union

from pampy import match, _

TSource = TypeVar("TSource")
TResult = TypeVar("TResult")


class OptionModule(Generic[TSource]):
    """Option module.

    Contains a collection of static methods (functions) for operating on
    options. All functions takes the source as the last curried
    argument, i.e all functions returns a function that takes the source
    sequence as the only argument.
    """

    @staticmethod
    def map(mapper: Callable[[TSource], TResult]) -> "Callable[[Option[TSource]], Option[TResult]]":
        def _map(option: Option[TSource]) -> "Option[TResult]":
            return option.map(mapper)
        return _map

    @staticmethod
    def bind(mapper: Callable[[TSource], 'Option[TResult]']) -> 'Callable[[Option[TSource]], Option[TResult]]':
        def _bind(option: "Option[TSource]") -> "Option[TResult]":
            return option.bind(mapper)
        return _bind

    @staticmethod
    def or_else(if_none: 'Option[TSource]') -> 'Callable[[Option[TSource]], Option[TSource]]':
        """Returns option if it is Some, otherwise returns ifNone."""
        def _or_else(option: 'Option[TSource]') -> 'Option[TSource]':
            return option.or_else(if_none)
        return _or_else

    @classmethod
    def to_list(cls) -> 'Callable[[Option[TSource]], List[TSource]]':
        def _to_list(option: Option[TSource]) -> List[TSource]:
            return option.to_list()
        return _to_list

    @classmethod
    def to_seq(cls, option: "Option[TSource]") -> Iterable[TSource]:
        return match(option, Some, lambda some: option, _, [])  # type: ignore

    @classmethod
    def is_some(cls, option: "Option[TSource]") -> bool:
        return match(option, Some, True, _, False)  # type: ignore

    @classmethod
    def is_none(cls, option: "Option[TSource]") -> bool:
        return not cls.is_some(option)


class Option(Iterable[TSource]):

    @abstractmethod
    def map(self, mapper: Callable[[TSource], TResult]) -> 'Option[TResult]':  # noqa: T484
        raise NotImplementedError

    @abstractmethod
    def bind(self, mapper: Callable[[TSource], 'Option[TResult]']) -> 'Option[TResult]':  # noqa: T484
        raise NotImplementedError

    @abstractmethod
    def or_else(self, if_none: 'Option[TSource]') -> 'Option[TSource]':  # noqa: T484
        raise NotImplementedError

    @abstractmethod
    def to_list(cls) -> List[TSource]:
        raise NotImplementedError

    @abstractmethod
    def to_seq(cls) -> Iterable[TSource]:
        raise NotImplementedError

    @abstractmethod
    def is_some(cls) -> bool:
        raise NotImplementedError

    @abstractmethod
    def is_none(cls) -> bool:
        raise NotImplementedError

    @abstractmethod
    def __eq__(self, other):
        raise NotImplementedError

    def __repr__(self):
        return self.__str__()


class Some(Option[TSource]):
    def __init__(self, value: TSource) -> None:
        self._value = value

    def is_some(self) -> bool:
        return True

    def is_none(self) -> bool:
        return False

    def map(self, mapper: Callable[[TSource], TResult]):
        return Some(mapper(self._value))

    def bind(self, mapper: Callable[[TSource], Option[TResult]]) -> Option[TResult]:
        return mapper(self._value)

    def or_else(self, if_none: Option[TSource]) -> Option[TSource]:
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
    """Do not use.

    Use the singleton None_ instead."""

    def is_some(self) -> bool:
        return False

    def is_none(self) -> bool:
        return True

    def map(self, mapper: Callable[[TSource], TResult]):
        return self

    def bind(self, mapper: Callable[[TSource], Option[TResult]]) -> Option[TResult]:
        return Nothing

    def or_else(self, if_none: Option[TSource]) -> Option[TSource]:
        return if_none

    def to_list(self) -> List[TSource]:
        return []

    def to_seq(self) -> Iterable[TSource]:
        return []

    def __iter__(self) -> Iterator[TSource]:
        """Return iterator for None_().

        We basically want to return nothing, but we have to return something to signal fail
        """
        print("None:iter")
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


def send(gen, done: List[bool], value: Optional[TSource] = None) -> Option[TSource]:
    try:
        yielded = gen.send(value)
        return Some(yielded) if yielded else Nothing
    except GeneratorExit:
        done.append(True)
        return Nothing
    except StopIteration as ex:
        done.append(True)
        if ex.value is not None:
            return Some(ex.value)
        elif value is not None:
            return Some(value)
        return Nothing
    except Exception:
        done.append(True)
        return Nothing


def option(
    fn: Callable[  # Function
        ...,       # ... that takes anything
        Union[     # ... and returns
            # Coroutine that yields or returns an option
            Coroutine[TSource, Optional[TSource], Optional[Option[TSource]]],
            # Generator that yields or returns an option
            Generator[TSource, Optional[TSource], Optional[Option[TSource]]],
            # or simply just an Option
            Option[TSource]
        ],
    ]
) -> Callable[..., Option[TSource]]:
    """Option builder.

    Enables the use of options as computational expressions using
    coroutines. Thus inside the coroutine the keywords `yield` and
    `yield from` reasembles `yield` and `yield!` from F#.

    Args:
        fn: A function that contains a computational expression and
        returns either a coroutine, generator or an option.

    Returns:
        An Option object.
    """

    # This is a mess, but we basically just want to convert plain functions with a return statement into coroutines.
    gen = iter(cast(Iterable[TSource], fn()))

    def wrapper(*args, **kw) -> Option[TSource]:
        done: List[bool] = []
        result: Option[TSource] = send(gen, done)

        while result != Nothing and not done:
            result = result.bind(lambda value: send(gen, done, value))

        return result
    return wrapper


__all__ = ["OptionModule", "Option", "Some", "Nothing", "option"]
