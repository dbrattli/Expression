from expression.core import match


def test_default_matches():
    m = match(42)
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

    for _ in m.case(B):
        assert False
    else:
        assert True


def test_match_multiple_cases():
    m = match("expression")

    for _ in m.case("rxpy"):
        assert False

    for value in m.case("expression"):
        assert value == "expression"

    for value in m.case("aioreactive"):
        assert False

    for _ in m.default():
        assert False


def test_match_multiple_only_matches_first():
    m = match("expression")

    for value in m.case("expression"):
        assert value == "expression"

    for value in m.case("expression"):
        assert False

    for _ in m.default():
        assert False
