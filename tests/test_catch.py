from typing import Any

import pytest

from expression import Error, Ok, Result, effect
from expression.extra.result import catch


def test_catch_wraps_ok():
    @catch(exception=ValueError)
    def add(a: int, b: int) -> Any:
        return a + b

    assert add(3, 4) == Ok(7)


def test_catch_wraps_error():
    @catch(exception=ValueError)
    def fn() -> Any:
        raise ValueError("error")

    result = fn()
    match result:
        case Error(error=ex):
            assert isinstance(ex, ValueError)
            assert str(ex) == "error"

        case _:
            assert False


def test_catch_ignores_other_exceptions():
    @catch(exception=KeyError)
    def fn(ex: Exception) -> Result[int, Exception]:
        raise ex

    with pytest.raises(ValueError):
        fn(ValueError("error"))

    with pytest.raises(RuntimeError):
        fn(RuntimeError("error"))


def test_catch_chained():
    @catch(exception=KeyError)
    @catch(exception=ValueError)
    def fn(ex: Exception) -> Any:
        raise ex

    result = fn(ValueError("error"))
    match result:
        case Error(error=ex):
            assert isinstance(ex, ValueError)
            assert str(ex) == "error"
        case _:
            assert False

    result = fn(KeyError("error"))
    match result:
        case Error(error=ex):
            assert isinstance(ex, KeyError)
            assert str(ex) == "'error'"
        case _:
            assert False


def test_catch_with_effect_ok():
    @catch(exception=TypeError)
    @effect.try_
    def fn(scope: effect.ResultScope[Exception], a: int) -> int:
        b = scope.bind(Ok(42))
        return a + b

    result = fn(1)
    assert result == Ok(43)


def test_catch_with_effect_error():
    @catch(exception=TypeError)
    @effect.try_
    def fn(scope: effect.ResultScope[Exception], a: int) -> int:
        b = scope.bind(Error(ValueError("failure")))
        return a + b

    result = fn(1)
    match result:
        case Error(error=ex):
            assert isinstance(ex, ValueError)
            assert str(ex) == "failure"
        case _:
            assert False


def test_catch_with_effect_exception():
    @catch(exception=TypeError)
    @effect.result
    def fn(scope: effect.ResultScope[Exception], a: int) -> str:
        b = scope.bind(Ok("hello"))
        return a + b  # type: ignore (by design)

    result = fn(1)
    match result:
        case Error(error=ex):
            assert isinstance(ex, TypeError)
        case _:
            assert False
