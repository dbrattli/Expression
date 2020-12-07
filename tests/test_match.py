from typing import Any, Iterable

from expression.core import Nothing, Option, Some, SupportsMatch, match


def test_default_matches():
    with match(42) as case:

        for value in case.default():
            assert value == 42


def test_match_type():
    with match(42) as case:
        for value in case(int):
            assert value == 42
            break
        else:
            assert False


def test_not_match_type():
    with match(42) as case:
        while case(float):  # NOTE: Should show type error
            assert False

        while case.default():
            assert True


def test_match_instance():
    with match(42) as case:
        for value in case(42):
            assert value == 42
            break
        else:
            assert False


def test_not_match_instance():
    x = 42
    with match(x) as case:
        while case(43):  # NOTE: should show type error
            assert False

        while case.default():
            assert True


def test_match_equals():
    with match(Some(42)) as case:
        while case(Some(42)):
            assert True

        while case.default():
            assert False


def test_match_not_equals():
    with match(Some(42)) as case:
        while case(Some(4)):  # NOTE: should show type error
            assert False

        while case.default():
            assert True


class A:
    pass


class B(A):
    pass


def test_match_isinstance():
    with match(B()) as case:
        for _ in case(A):
            assert True
            break
        else:
            assert False


def test_not_match_isinstance():
    with match(A()) as case:
        while case(B):
            assert False

        while case.default():
            assert True


def test_match_multiple_cases():
    with match("expression") as case:
        while case("rxpy"):  # NOTE: should show type error
            assert False

        for value in case(str):
            assert value == "expression"

        for value in case(float):  # NOTE: should show type error
            assert False

        while case.default():
            assert False


def test_match_multiple_cases_return_value():
    def matcher(value: str) -> Option[str]:
        with match(value) as case:
            while case("rxpy"):
                assert False

            for value in case(str):
                assert value == "expression"
                return Some(value)

            for value in case("aioreactive"):
                assert False

            while case.default():
                assert False

        return Nothing

    result = matcher("expression")
    assert result.value == "expression"


def test_match_multiple_only_matches_first():
    with match("expression") as case:
        for value in case(str):
            assert value == "expression"

        for value in case(str):
            assert False

        while case.default():
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


def test_active_pattern_matches():
    text = "42"
    with match(text) as case:
        for value in case(ParseInteger):
            assert value == int(text)

        while case.default():
            assert False


def test_active_pattern_not_matches():
    text = "abc"
    with match(text) as case:
        for _ in case(ParseInteger):
            assert False

        while case.default():
            assert True
