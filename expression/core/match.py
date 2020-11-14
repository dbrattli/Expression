from abc import abstractmethod
from typing import (Any, Generic, Iterable, Protocol, TypeVar, Union, cast,
                    overload)

TSource = TypeVar("TSource")

TG = Generic


class Matchable(Protocol[TSource]):
    """Pattern matching protocol."""

    @abstractmethod
    def __match__(self, pattern: Any) -> Iterable[TSource]:
        """Return a singleton iterable item (e.g `[ value ]`) if pattern
        matches, else an empty iterable (e.g. `[]`)."""

        raise NotImplementedError

    @overload
    def match(self) -> "Match[TSource]":
        ...

    @overload
    def match(self, pattern: Any) -> Iterable[TSource]:
        ...

    def match(self, pattern: Any) -> Any:
        m: Match[TSource] = Match(self)
        return m.case(pattern) if pattern else m


class Match(Generic[TSource]):
    """Pattern matching.

    Matches a value with type, instance or uses matching protocol
    if supported by value.
    """

    def __init__(self, value: Union[Any, Matchable[TSource]]):
        self.is_matched = False
        self.value = value

    def case(self, pattern: Any) -> Iterable[TSource]:
        value = self.value

        if self.is_matched:
            return []

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
        return [self.value]

    def __bool__(self):
        return self.is_matched


def match(value: TSource) -> Match[TSource]:
    """Convenience create method to get typing right"""
    return Match(value)


__all__ = ["match", "Match", "Matchable"]
