from expression.core import Matcher, Nothing, Option, Some, match


def test_default_matches():
    m = Matcher.of(42)

    for value in m.default():
        assert value == 42


def test_match_type():
    with match(42) as m:
        for value in m.case(int):
            assert value == 42
            break
        else:
            assert False


def test_not_match_type():
    with match(42) as m:
        while m.case(float):
            assert False

        while m.default():
            assert True


def test_match_instance():
    with match(42) as m:
        for value in m.case(42):
            assert value == 42
            break
        else:
            assert False


def test_not_match_instance():
    with match(42) as m:
        while m.case(43):
            assert False

        while m.default():
            assert True


class A:
    pass


class B(A):
    pass


def test_match_isinstance():
    with match(B()) as m:
        for _ in m.case(A):
            assert True
            break
        else:
            assert False


def test_not_match_isinstance():
    with match(A()) as m:
        while m.case(B):
            assert False

        while m.default():
            assert True


def test_match_multiple_cases():
    with match("expression") as m:
        while m.case("rxpy"):
            assert False

        for value in m.case(str):
            assert value == "expression"

        for value in m.case(float):
            assert False

        while m.default():
            assert False


def test_match_multiple_cases_return_value():
    def matcher(value: str) -> Option[str]:
        with match(value) as m:
            while m.case("rxpy"):
                assert False

            for value in m.case(str):
                assert value == "expression"
                return Some(value)

            for value in m.case("aioreactive"):
                assert False

            while m.default():
                assert False

        return Nothing

    result = matcher("expression")
    assert result.value == "expression"


def test_match_multiple_only_matches_first():
    with match("expression") as m:
        for value in m.case(str):
            assert value == "expression"

        for value in m.case(str):
            assert False

        while m.default():
            assert False
