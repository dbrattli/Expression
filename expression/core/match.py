from abc import abstractmethod
from types import TracebackType
from typing import Any, Generic, Iterable, Optional, Protocol, Type, TypeVar, cast, get_origin, overload

from .error import MatchFailureError

TSource = TypeVar("TSource")
TPattern = TypeVar("TPattern")


class SupportsMatch(Protocol[TSource]):
    """Pattern matching protocol."""

    @abstractmethod
    def __match__(self, pattern: Any) -> Iterable[TSource]:
        """Match pattern with value.

        Return a singleton iterable item (e.g `[ value ]`) if pattern
        matches value , else an empty iterable (e.g. `[]`)."""

        raise NotImplementedError


class MatchMixin(SupportsMatch[TSource]):
    def match(self, pattern: Any) -> Iterable[TSource]:
        """Match with pattern.

        NOTE: This is just the basic default implementation for fluent
        matching. You most often need to add this methods plus the
        appropriate overloads to your own matchable class to get typing
        correctly.

        Example:
        >>> for x in xs.match(Some):
        ...     print(x)
        """

        case: Case[TSource] = Case(self)
        return case(pattern)


# class ActivePattern(SupportsMatch[TSource]):
#     def match(self, pattern: Any) -> Iterable[TSource]:
#         """Match with pattern.

#         NOTE: This is just the basic default implementation for fluent
#         matching. You most often need to add this methods plus the
#         appropriate overloads to your own matchable class to get typing
#         correctly.

#         Example:
#         >>> for x in xs.match(Some):
#         ...     print(x)
#         """

#         return pattern(self)


class Case(Generic[TSource]):
    """Case matcher for patterns.

    Matches its value with the given pattern. The pattern can be any of
    - Instance for is and equals matching
    - Type for isinstance matching
    - Matchable protocol if supported by value
    - Pattern protocol if supported by the pattern
    """

    def __init__(self, value: Any):
        self.is_matched = False
        self.value = value

    @overload
    def __call__(self, pattern: SupportsMatch[TPattern]) -> Iterable[TPattern]:
        """Intance pattern.

        Handle the case where pattern is instance of a type e.g:
        - 42
        - "test"
        - 23.4
        """
        ...

    @overload
    def __call__(self, pattern: Type[SupportsMatch[TPattern]]) -> Iterable[TPattern]:
        """Active type pattern.

        Handle the case where pattern is an active pattern type e.g:
        - ParseInteger
        """
        ...

    @overload
    def __call__(self, pattern: Type[TSource]) -> Iterable[TSource]:
        """Type pattern.

        Handle the case where pattern is a type e.g:
        - int
        - str
        - float
        """

    @overload
    def __call__(self, pattern: TPattern) -> Iterable[TPattern]:
        """Intance pattern.

        Handle the case where pattern is instance of a type e.g:
        - 42
        - "test"
        - 23.4
        """
        ...

    def __call__(self, pattern: Any) -> Iterable[Any]:
        if self.is_matched:
            return []

        value = self.value

        # Value is matching pattern
        if hasattr(value, "__match__"):
            value_ = cast(SupportsMatch[Any], value)
            matched = value_.__match__(pattern)
            if matched:
                self.is_matched = True
                return matched

        # The pattern is matching value (aka active pattern matching)
        elif hasattr(pattern, "__match__"):
            matched = pattern.__match__(value)
            if matched:
                self.is_matched = True
                return matched

        # Value is pattern or equals pattern
        if value is pattern or value == pattern:
            self.is_matched = True
            return [value]

        # Value is an instance of pattern
        try:
            origin: Any = get_origin(pattern)
            if isinstance(value, origin or pattern):
                self.is_matched = True
                return [value]
        except TypeError:
            pass

        # No match
        return []

    def default(self) -> Iterable[Any]:
        print("default()")
        if self.is_matched:
            return []

        self.is_matched = True
        return [self.value]

    def __enter__(self) -> "Case[TSource]":
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


def match(value: TSource) -> Case[TSource]:
    """Convenience case matcher create method to get typing right

    Same as `Case(value)`
    """
    return Case(value)


# def matcher(value: TSource) -> Callable[[Callable[..., Any]], Callable[[TSource], Generator[TSource, None, None]]]:
#     def wrap(fn: Callable[..., Any]) -> Callable[..., Generator[TSource, None, None]]:
#         def inner(*args: Any, **kw: Any) -> Generator[TSource, None, None]:
#             m = Matcher.of(value)
#             return fn(m, *args, **kw)

#         return inner

#     return wrap


__all__ = ["match", "Case", "MatchMixin", "SupportsMatch"]
