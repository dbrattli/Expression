from __future__ import annotations

from types import TracebackType
from typing import Any, Generic, Iterable, Optional, Type, TypeVar, cast, get_origin, overload

from expression.core.builder import TResult

from .error import MatchFailureError
from .typing import SupportsMatch

TSource = TypeVar("TSource")
A = TypeVar("A")
B = TypeVar("B")


class MatchMixin(SupportsMatch[TSource]):
    def match(self, pattern: Any) -> Iterable[Any]:
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
    def __call__(self, pattern: Type[SupportsMatch[A]]) -> Iterable[A]:
        """Match with active type pattern.

        Handle the case where pattern is an active pattern type e.g
        `ParseInteger`
        """
        ...

    @overload
    def __call__(self, pattern: SupportsMatch[A]) -> Iterable[A]:
        """Match with intance of `SupportsMatch` pattern.

        Handle the case where pattern is instance of a type that
        sub-classes `SupportsMatch`, e.g an active pattern.
        """
        ...

    # @overload
    # def __call__(self, pattern: Choice1of2[A, B]) -> Iterable[A]:
    #     """Intance pattern.

    #     Handle the case where pattern is instance of a `Choice1of2` type
    #     """
    #     ...

    # @overload
    # def __call__(self, pattern: Choice2of2[A, B]) -> Iterable[B]:
    #     """Intance pattern.

    #     Handle the case where pattern is instance of a `Choice2of2` type
    #     """
    #     ...

    @overload
    def __call__(self, pattern: Type[A]) -> Iterable[A]:
        """Match with type pattern.

        Handle the case where pattern is a type e.g `int`, `str`,
        `float`.
        """

    @overload
    def __call__(self, pattern: A) -> Iterable[A]:
        """Match with intance pattern.

        Handle the case where pattern is instance of a type e.g `42`,
        `"test"`, `23.4`.
        """
        ...

    def __call__(self, pattern: Any) -> Iterable[Any]:
        """Match with pattern."""
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

    @property
    def _(self):
        """Handle default case. Always matches."""
        return self.default()

    @overload
    def default(self) -> Iterable[TSource]:
        ...

    @overload
    def default(self, ret: Optional[TResult]) -> TResult:
        ...

    def default(self, ret: Optional[Any] = None) -> Any:
        """Handle default case. Always matches."""

        if self.is_matched:
            return []

        self.is_matched = True
        return [ret or self.value]

    def __enter__(self) -> Case[TSource]:
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
