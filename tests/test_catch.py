from collections.abc import Generator
from typing import Any, assert_type

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
        case Error(ex):
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
        case Error(ex):
            assert isinstance(ex, ValueError)
            assert str(ex) == "error"
        case _:
            assert False

    result = fn(KeyError("error"))
    match result:
        case Error(ex):
            assert isinstance(ex, KeyError)
            assert str(ex) == "'error'"
        case _:
            assert False


def test_catch_with_effect_ok():
    @catch(exception=TypeError)
    @effect.try_[int]()
    def fn(a: int) -> Generator[int, int, int]:
        b = yield from Ok(42)
        return a + b

    result = fn(1)
    assert result == Ok(43)


def test_catch_with_effect_error():
    @catch(exception=TypeError)
    @effect.try_[int]()
    def fn(a: int) -> Generator[int, int, int]:
        b = yield from Error(ValueError("failure"))
        return a + b

    result = fn(1)
    match result:
        case Error(ex):
            assert isinstance(ex, ValueError)
            assert str(ex) == "failure"
        case _:
            assert False


def test_catch_with_effect_exception():
    @catch(exception=TypeError)
    @effect.result[str, Exception]()
    def fn(a: int) -> Generator[str, str, str]:
        b = yield from Ok("hello")
        return a + b  # type: ignore (by design)

    result = fn(1)
    match result:
        case Error(ex):
            assert isinstance(ex, TypeError)
        case _:
            assert False


def test_catch_preserves_signature_and_plain_return_type():
    def add(a: int, *, b: int = 1) -> int:
        return a + b

    wrapped = catch(add, exception=ValueError)
    decorated = catch(exception=ValueError)(add)
    assert_type(wrapped(3, b=4), Result[int, ValueError])
    assert_type(decorated(3, b=4), Result[int, ValueError])
    assert wrapped(3, b=4) == decorated(3, b=4) == Ok(7)
    assert wrapped.__name__ == "add"


def test_catch_preserves_existing_result_and_error_type():
    original: Result[int, str] = Error("failure")

    def fn(value: int) -> Result[int, str]:
        return Ok(value) if value else original

    wrapped = catch(fn, exception=ValueError)
    decorated = catch(exception=ValueError)(fn)
    assert_type(wrapped(1), Result[int, str | ValueError])
    assert_type(decorated(1), Result[int, str | ValueError])
    assert wrapped(1) == decorated(1) == Ok(1)
    assert wrapped(0) is original
    assert decorated(0) is original


def test_catch_chained_preserves_types():
    @catch(exception=KeyError)
    @catch(exception=ValueError)
    def fn(value: int) -> int:
        return value

    assert_type(fn(1), Result[int, ValueError | KeyError])
    assert fn(1) == Ok(1)


def test_catch_direct_call_catches_exception():
    error = ValueError("failure")

    def fn() -> int:
        raise error

    wrapped = catch(fn, exception=ValueError)
    assert wrapped() == Error(error)


def test_catch_decorator_can_wrap_different_signatures():
    decorator = catch(exception=ValueError)

    @decorator
    def number(value: int) -> int:
        return value

    @decorator
    def text(*, value: str) -> str:
        return value

    assert_type(number(1), Result[int, ValueError])
    assert_type(text(value="hello"), Result[str, ValueError])
    assert number(1) == Ok(1)
    assert text(value="hello") == Ok("hello")
