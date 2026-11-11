from expression import Error, Failure, Ok, Success, Try


def test_can_create_success():
    Success(10)


def test_can_create_failure():
    Failure(ValueError())


def test_try_success():
    xs: Try[int] = Success(10)

    match xs:
        case Ok(x):
            assert x == 10
        case _:
            assert False


def test_try_match_failure():
    error = Exception("err")
    xs: Try[int] = Failure(error)

    match xs:
        case Error(err):
            assert err == error
        case _:
            assert False


def test_try_to_string_success():
    xs: Try[int] = Success(10)
    assert str(xs) == "Ok 10"


def test_try_to_string_failure():
    error = Exception("err")
    xs: Try[int] = Failure(error)
    assert str(xs) == "Error err"
