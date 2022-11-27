import pytest

from expression import Failure, Success, Try

from .utils import CustomException


def test_can_create_success():
    Success(10)


def test_can_create_failure():
    Failure(ValueError())


def test_try_success():
    xs: Try[int] = Success(10)

    for x in xs:
        assert x == 10


def test_try_failure():
    error = CustomException("err")
    xs: Try[int] = Failure(error)

    with pytest.raises(Failure):  # type: ignore
        for _ in xs:
            assert False


def test_try_match_failure():
    error = Exception("err")
    xs: Try[int] = Failure(error)

    match xs:
        case Failure(err):
            assert err == error
        case _:
            assert False
