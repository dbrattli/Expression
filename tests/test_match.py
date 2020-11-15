from expression.core import Matcher, match


def test_default_matches():
    m = Matcher.of(42)

    for value in m.default():
        assert value == 42


def test_match_type():
    m = match(42)

    for value in m.case(int):
        assert value == 42
        break
    else:
        assert False


def test_not_match_type():
    m = match(42)

    for _ in m.case(float):
        assert False
    else:
        assert True


def test_match_instance():
    m = match(42)

    for value in m.case(42):
        assert value == 42
        break
    else:
        assert False


def test_not_match_instance():
    m = match(42)

    for _ in m.case(43):
        assert False
    else:
        assert True


class A:
    pass


class B(A):
    pass


def test_match_isinstance():
    m = match(B())

    for _ in m.case(A):
        assert True
        break
    else:
        assert False


def test_not_match_isinstance():
    m = match(A())

    while m.case(B):
        assert False
    else:
        assert True


def test_match_multiple_cases():
    m = match("expression")

    while m.case("rxpy"):
        assert False

    for value in m.case(str):
        assert value == "expression"

    for value in m.case("aioreactive"):
        assert False

    while m.default():
        assert False


def test_match_multiple_cases_return_value():
    def matcher(value: str) -> str:
        m = match(value)

        while m.case("rxpy"):
            assert False

        for value in m.case(str):
            assert value == "expression"
            return value

        for value in m.case("aioreactive"):
            assert False

        while m.default():
            assert False

    result = matcher("expression")
    assert result == "expression"


def test_match_multiple_only_matches_first():
    m = match("expression")

    for value in m.case(str):
        assert value == "expression"

    for value in m.case(str):
        assert False

    while m.default():
        assert False
