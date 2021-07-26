"""Choice type.

A union type similar to the `Result` type. But also allows for higher
number of choices. Usually you would most likekly want to use the
`Result` type instead, but choice can be preferered in non-error cases.
"""
from abc import ABC
from typing import Any, Generic, Iterable, TypeVar, get_origin, overload

from .match import Case
from .typing import SupportsMatch

TSource = TypeVar("TSource")
A = TypeVar("A")
A_ = TypeVar("A_")
B = TypeVar("B")
B_ = TypeVar("B_")
C = TypeVar("C")


class Choice(ABC, SupportsMatch[TSource]):
    def __init__(self, value: Any) -> None:
        self.value = value

    def __match__(self, pattern: Any) -> Iterable[Any]:
        if self.value is pattern or self.value == pattern:
            return [self.value]

        try:
            origin: Any = get_origin(pattern)
            if isinstance(self, origin or pattern):
                return [self.value]
        except TypeError:
            pass

        return []

    def __repr__(self) -> str:
        return str(self)


class Choice2(Generic[A, B]):
    def __repr__(self) -> str:
        return str(self)


class Choice1of2(Choice2[A, B], Choice[A]):
    def __init__(self, value: A) -> None:
        super().__init__(value)

    @overload
    @classmethod
    def match(cls, case: Case[Choice2[A_, Any]]) -> Iterable[A_]:
        """Helper to cast the match result to correct type."""
        ...

    @overload
    @classmethod
    def match(cls, case: "Case[Choice1of2[A_, Any]]") -> Iterable[A_]:
        """Helper to cast the match result to correct type."""
        ...

    @overload
    @classmethod
    def match(cls, case: Case[A_]) -> Iterable[A_]:
        ...

    @classmethod
    def match(cls, case: Any) -> Iterable[Any]:
        return case(cls)

    def __eq__(self, o: Any) -> bool:
        if isinstance(o, Choice1of2):
            return self.value == o.value
        return False

    def __str__(self) -> str:
        return f"Choice1of2 {self.value}"


class Choice2of2(Choice2[A, B], Choice[B]):
    def __init__(self, value: B) -> None:
        super().__init__(value)

    @overload
    @classmethod
    def match(cls, case: Case[Choice2[Any, B_]]) -> Iterable[B_]:
        """Helper to cast the match result to correct type."""
        ...

    @overload
    @classmethod
    def match(cls, case: "Case[Choice1of2[Any, B_]]") -> Iterable[B_]:
        """Helper to cast the match result to correct type."""
        ...

    @overload
    @classmethod
    def match(cls, case: Case[B_]) -> Iterable[B_]:
        ...

    @classmethod
    def match(cls, case: Any) -> Iterable[Any]:
        return case(cls)

    def __eq__(self, o: Any) -> bool:
        if isinstance(o, Choice2of2):
            return self.value == o.value
        return False

    def __str__(self) -> str:
        return f"Choice2of2 {self.value}"


class Choice3(Generic[A, B, C]):
    ...


class Choice1of3(Choice3[A, B, C], Choice[A]):
    def __init__(self, value: A) -> None:
        super().__init__(value)

    @classmethod
    def match(cls, case: Case[A]) -> Iterable[A]:
        """Helper to cast the match result to correct type."""
        return case(cls)


class Choice2of3(Choice3[A, B, C], Choice[B]):
    def __init__(self, value: B) -> None:
        super().__init__(value)

    @classmethod
    def case(cls, case: Case[B]) -> Iterable[B]:
        """Helper to cast the match result to correct type."""
        return case(cls)


class Choice3of3(Choice3[A, B, C], Choice[C]):
    def __init__(self, value: C) -> None:
        super().__init__(value)

    @classmethod
    def case(cls, case: Case[C]) -> Iterable[C]:
        """Helper to cast the match result to correct type."""
        return case(cls)


__all__ = [
    "Choice",
    "Choice2",
    "Choice3",
    "Choice1of2",
    "Choice2of2",
    "Choice1of3",
    "Choice2of3",
    "Choice3of3",
]
