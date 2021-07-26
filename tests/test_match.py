from typing import Any, Iterable, List

from expression import Nothing, Option, Some, match
from expression.collections import FrozenList
from expression.core import SupportsMatch


def test_default_matches() -> None:
    with match(42) as case:
        for value in case._:
            assert value == 42


def test_default_falsy_matches() -> None:
    with match(None) as case:
        if case._:
            assert True
        else:
            assert False


def test_match_type() -> None:
    with match(42) as case:
        for value in case(int):
            assert value == 42
            break
        else:
            assert False


def test_not_match_type() -> None:
    with match(42) as case:
        if case(float):
            assert False

        if case._:
            assert True


def test_match_instance() -> None:
    with match(42) as case:
        for value in case(42):
            assert value == 42
            break
        else:
            assert False


def test_not_match_instance() -> None:
    x = 42
    with match(x) as case:
        if case(43):
            assert False

        if case._:
            assert True


def test_match_equals() -> None:
    with match(Some(42)) as case:
        if case(Some(42)):
            assert True

        if case._:
            assert False


def test_match_not_equals() -> None:
    with match(Some(42)) as case:
        if case(Some(4)):
            assert False

        if case._:
            assert True


def test_match_destructure() -> None:
    xs: FrozenList[int] = FrozenList.empty().cons(42)
    with match(xs) as case:
        for (head, *_) in case(FrozenList[int]):
            assert head == 42


class A:
    pass


class B(A):
    pass


def test_match_isinstance() -> None:
    with match(B()) as case:
        for _ in case(A):
            assert True
            break
        else:
            assert False


def test_not_match_isinstance() -> None:
    with match(A()) as case:
        if case(B):
            assert False

        if case._:
            assert True


def test_match_multiple_cases() -> None:
    with match("expression") as case:
        while case("rxpy"):
            assert False

        for value in case(str):
            assert value == "expression"

        for value in case(float):
            assert False

        if case._:
            assert False


def test_match_multiple_cases_return_value() -> None:
    def matcher(value: str) -> Option[str]:
        with match(value) as case:
            while case("rxpy"):
                assert False

            for value in case(str):
                assert value == "expression"
                return Some(value)

            for value in case("aioreactive"):
                assert False

            if case._:
                assert False

        return Nothing

    result = matcher("expression")
    assert result.value == "expression"


def test_match_multiple_only_matches_first() -> None:
    with match("expression") as case:
        for value in case(str):
            assert value == "expression"

        for value in case(str):
            assert False

        if case._:
            assert False


class ParseInteger_(SupportsMatch[int]):
    """Active pattern for parsing integers."""

    def __match__(self, pattern: Any) -> Iterable[int]:
        """Match value with pattern."""

        try:
            number = int(pattern)
        except ValueError:
            return []
        else:
            return [number]


ParseInteger = ParseInteger_()


def test_active_pattern_matches() -> None:
    text = "42"
    with match(text) as case:
        for value in case(ParseInteger):
            assert value == int(text)

        if case._:
            assert False


def test_active_pattern_not_matches() -> None:
    text = "abc"
    with match(text) as case:
        for _ in case(ParseInteger):
            assert False

        if case._:
            assert True


def test_match_generic_matches() -> None:
    xs = [1, 2, 3]

    with match(xs) as case:
        for x in case(List[int]):
            assert x == xs
