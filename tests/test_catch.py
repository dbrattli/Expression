from typing import Any, Generator

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
    for ex in result.match(Error[Any, Exception]):
        assert isinstance(ex, ValueError)
        assert str(ex) == "error"
        break
    else:
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
    for ex in result.match(Error[Any, Exception]):
        assert isinstance(ex, ValueError)
        assert str(ex) == "error"
        break
    else:
        assert False

    result = fn(KeyError("error"))
    for ex in result.match(Error[Any, Exception]):
        assert isinstance(ex, KeyError)
        assert str(ex) == "'error'"
        break
    else:
        assert False


def test_catch_with_effect_ok():
    @catch(exception=TypeError)
    @effect.result
    def fn(a: int) -> Generator[int, int, int]:
        b = yield from Ok(42)
        return a + b

    result = fn(1)
    assert result == Ok(43)


def test_catch_with_effect_error():
    @catch(exception=TypeError)
    @effect.result
    def fn(a: int) -> Generator[int, Any, int]:
        b: int
        b = yield from Error(ValueError("failure"))
        return a + b

    result = fn(1)
    for ex in result.match(Error[Any, ValueError]):
        assert isinstance(ex, ValueError)
        assert str(ex) == "failure"
        break
    else:
        assert False


def test_catch_with_effect_exception():
    @catch(exception=TypeError)
    @effect.result
    def fn(a: int) -> Generator[str, str, int]:
        b = yield from Ok("hello")
        return a + b  # type: ignore

    result = fn(1)
    for ex in result.match(Error[Any, TypeError]):
        assert isinstance(ex, TypeError)
        break
    else:
        assert False
