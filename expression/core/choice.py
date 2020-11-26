from abc import ABC, abstractclassmethod
from typing import Any, Generic, Iterable, Optional, TypeVar, Union

from .match import Matcher

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")


class Choice(ABC):
    def __init__(self, value: Any) -> None:
        self.value = value

    @abstractclassmethod
    def case(cls, m: Matcher) -> Iterable[Any]:
        """Helper to cast the match result to correct type."""
        raise NotImplementedError

    def __match__(self, pattern: Any) -> Iterable[Any]:
        if self.value is pattern or self.value == pattern:
            self.is_matched = True
            return [self.value]

        try:
            if isinstance(self.value, pattern):
                self.is_matched = True
                return [self.value]
        except TypeError:
            pass

        return []


class Choice2(Generic[A, B], Choice):
    def match(self, pattern: Optional[Any] = None) -> Union[Iterable[Union[A, B]]]:
        m = Matcher(self)
        return m.case(pattern) if pattern else self.case(m)


class Choice1of2(Choice2[A, B]):
    def __init__(self, value: A) -> None:
        super().__init__(value)

    @classmethod
    def case(cls, m: Matcher) -> Iterable[A]:
        """Helper to cast the match result to correct type."""
        return m.case(cls)

    def __match__(self, pattern: Any) -> Iterable[A]:
        return super().__match__(pattern)


class Choice2of2(Choice2[A, B]):
    def __init__(self, value: B) -> None:
        super().__init__(value)

    @classmethod
    def case(cls, m: Matcher) -> Iterable[B]:
        """Helper to cast the match result to correct type."""
        return m.case(cls)

    def __match__(self, pattern: Any) -> Iterable[B]:
        return super().__match__(pattern)


class Choice3(Generic[A, B, C], Choice):
    def match(self, pattern: Optional[Any] = None) -> Union[Iterable[Union[A, B, C]]]:
        m = Matcher(self)
        return m.case(pattern) if pattern else self.case(m)


class Choice1of3(Choice3[A, B, C]):
    def __init__(self, value: A) -> None:
        super().__init__(value)

    @classmethod
    def case(cls, m: Matcher) -> Iterable[A]:
        """Helper to cast the match result to correct type."""
        return m.case(cls)

    def __match__(self, pattern: Any) -> Iterable[A]:
        return super().__match__(pattern)


class Choice2of3(Choice3[A, B, C]):
    def __init__(self, value: B) -> None:
        super().__init__(value)

    @classmethod
    def case(cls, m: Matcher) -> Iterable[B]:
        """Helper to cast the match result to correct type."""
        return m.case(cls)

    def __match__(self, pattern: Any) -> Iterable[B]:
        return super().__match__(pattern)


class Choice3of3(Choice3[A, B, C]):
    def __init__(self, value: C) -> None:
        super().__init__(value)

    @classmethod
    def case(cls, m: Matcher) -> Iterable[C]:
        """Helper to cast the match result to correct type."""
        return m.case(cls)

    def __match__(self, pattern: Any) -> Iterable[C]:
        return super().__match__(pattern)
