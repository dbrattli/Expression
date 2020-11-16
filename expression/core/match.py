from abc import abstractmethod
from types import TracebackType
from typing import Any, Generic, Iterable, Optional, Protocol, Type, TypeVar, Union, cast, overload

from .error import MatchFailureError

TSource = TypeVar("TSource")


class Matchable(Protocol[TSource]):
    """Pattern matching protocol."""

    @abstractmethod
    def __match__(self, pattern: Any) -> Iterable[TSource]:
        """Return a singleton iterable item (e.g `[ value ]`) if pattern
        matches, else an empty iterable (e.g. `[]`)."""

        raise NotImplementedError

    @overload
    def match(self) -> "Matcher[TSource]":
        ...

    @overload
    def match(self, pattern: Any) -> Iterable[TSource]:
        ...

    def match(self, pattern: Optional[Any] = None) -> "Union[Matcher[TSource], Iterable[TSource]]":
        """Match with pattern.

        NOTE: You most often need to add this methods plus the
        appropriate overloads to your own matchable class to get typing
        correctly."""

        m: Matcher[TSource] = Matcher(self)
        return m.case(pattern) if pattern else m


class Matcher(Generic[TSource]):
    """Pattern matcher.

    Matches a value with type, instance or uses matching protocol
    if supported by value.
    """

    def __init__(self, value: Union[Any, Matchable[TSource]]):
        self.is_matched = False
        self.value = value

    def case(self, pattern: Any) -> Iterable[Any]:
        if self.is_matched:
            return []

        value = self.value

        if hasattr(value, "__match__"):
            value_ = cast(Matchable[TSource], value)
            matched = value_.__match__(pattern)
            if matched:
                self.is_matched = True
            return matched

        try:
            if value is pattern or isinstance(value, pattern):
                self.is_matched = True
                return [value]
        except TypeError:
            pass

        return []

    def default(self) -> Iterable[Union[Any, Matchable[TSource]]]:
        if self.is_matched:
            return []
        self.is_matched = True
        return [self.value]

    @staticmethod
    def of(value: TSource) -> "Matcher[TSource]":
        """Convenience create method to get typing right"""
        return Matcher(value)

    def __enter__(self) -> "Matcher[TSource]":
        """Enter context management."""
        return self

    def __exit__(
        self, exctype: Optional[Type[BaseException]], excinst: Optional[BaseException], exctb: Optional[TracebackType]
    ) -> None:
        """Exit context management."""

        if not self.is_matched:
            raise MatchFailureError(self.value)

    def __bool__(self):
        return self.is_matched


def match(value: TSource) -> Matcher[TSource]:
    """Convenience create method to get typing right

    Same as `Matcher.of(value)`
    """
    return Matcher(value)


# def matcher(value: TSource) -> Callable[[Callable[..., Any]], Callable[[TSource], Generator[TSource, None, None]]]:
#     def wrap(fn: Callable[..., Any]) -> Callable[..., Generator[TSource, None, None]]:
#         def inner(*args: Any, **kw: Any) -> Generator[TSource, None, None]:
#             m = Matcher.of(value)
#             return fn(m, *args, **kw)

#         return inner

#     return wrap


__all__ = ["match", "Matcher", "Matchable"]
