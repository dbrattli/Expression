"""Choice type.

A union type similar to the `Result` type. But also allows for higher
number of choices. Usually you would most likely want to use the
`Result` type instead, but choice can be preferred in non-error cases.
"""
from abc import ABC
from typing import Any, Generic, TypeVar

_TSource = TypeVar("_TSource")
_A = TypeVar("_A")
_B = TypeVar("_B")
_C = TypeVar("_C")


class Choice(ABC, Generic[_TSource]):
    def __init__(self, value: Any) -> None:
        self.value = value

    def __repr__(self) -> str:
        return str(self)

    def __hash__(self) -> int:
        return hash(self.value)


class Choice2(Generic[_A, _B]):
    def __repr__(self) -> str:
        return str(self)


class Choice1of2(Choice2[_A, _B], Choice[_A]):
    __match_args__ = ("value",)

    def __init__(self, value: _A) -> None:
        super().__init__(value)

    def __eq__(self, o: Any) -> bool:
        if isinstance(o, Choice1of2):
            return self.value == o.value
        return False

    def __str__(self) -> str:
        return f"Choice1of2 {self.value}"


class Choice2of2(Choice2[_A, _B], Choice[_B]):
    __match_args__ = ("value",)

    def __init__(self, value: _B) -> None:
        super().__init__(value)

    def __eq__(self, o: Any) -> bool:
        if isinstance(o, Choice2of2):
            return self.value == o.value
        return False

    def __str__(self) -> str:
        return f"Choice2of2 {self.value}"


class Choice3(Generic[_A, _B, _C]):
    ...


class Choice1of3(Choice3[_A, _B, _C], Choice[_A]):
    __match_args__ = ("value",)

    def __init__(self, value: _A) -> None:
        super().__init__(value)


class Choice2of3(Choice3[_A, _B, _C], Choice[_B]):
    __match_args__ = ("value",)

    def __init__(self, value: _B) -> None:
        super().__init__(value)


class Choice3of3(Choice3[_A, _B, _C], Choice[_C]):
    __match_args__ = ("value",)

    def __init__(self, value: _C) -> None:
        super().__init__(value)


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
