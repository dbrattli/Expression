"""Choice type.

A union type similar to the `Result` type. But also allows for higher
number of choices. Usually you would most likekly want to use the
`Result` type instead, but choice can be preferered in non-error cases.
"""
from abc import ABC
from typing import Any, Generic, Iterable, TypeVar, get_origin, overload

from .match import Case
from .typing import SupportsMatch

_TSource = TypeVar("_TSource")
_A = TypeVar("_A")
_A_ = TypeVar("_A_")
_B = TypeVar("_B")
_B_ = TypeVar("_B_")
_C = TypeVar("_C")


class Choice(ABC, SupportsMatch[_TSource]):
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


class Choice2(Generic[_A, _B]):
    def __repr__(self) -> str:
        return str(self)


class Choice1of2(Choice2[_A, _B], Choice[_A]):
    def __init__(self, value: _A) -> None:
        super().__init__(value)

    @overload
    @classmethod
    def match(cls, case: Case[Choice2[_A_, Any]]) -> Iterable[_A_]:
        """Helper to cast the match result to correct type."""
        ...

    @overload
    @classmethod
    def match(cls, case: "Case[Choice1of2[_A_, Any]]") -> Iterable[_A_]:
        """Helper to cast the match result to correct type."""
        ...

    @overload
    @classmethod
    def match(cls, case: Case[_A_]) -> Iterable[_A_]:
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


class Choice2of2(Choice2[_A, _B], Choice[_B]):
    def __init__(self, value: _B) -> None:
        super().__init__(value)

    @overload
    @classmethod
    def match(cls, case: Case[Choice2[Any, _B_]]) -> Iterable[_B_]:
        """Helper to cast the match result to correct type."""
        ...

    @overload
    @classmethod
    def match(cls, case: "Case[Choice1of2[Any, _B_]]") -> Iterable[_B_]:
        """Helper to cast the match result to correct type."""
        ...

    @overload
    @classmethod
    def match(cls, case: Case[_B_]) -> Iterable[_B_]:
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


class Choice3(Generic[_A, _B, _C]):
    ...


class Choice1of3(Choice3[_A, _B, _C], Choice[_A]):
    def __init__(self, value: _A) -> None:
        super().__init__(value)

    @classmethod
    def match(cls, case: Case[_A]) -> Iterable[_A]:
        """Helper to cast the match result to correct type."""
        return case(cls)


class Choice2of3(Choice3[_A, _B, _C], Choice[_B]):
    def __init__(self, value: _B) -> None:
        super().__init__(value)

    @classmethod
    def case(cls, case: Case[_B]) -> Iterable[_B]:
        """Helper to cast the match result to correct type."""
        return case(cls)


class Choice3of3(Choice3[_A, _B, _C], Choice[_C]):
    def __init__(self, value: _C) -> None:
        super().__init__(value)

    @classmethod
    def case(cls, case: Case[_C]) -> Iterable[_C]:
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
