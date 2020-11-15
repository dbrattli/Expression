from typing import Callable, Generator, List, Optional

import pytest
from expression import effect
from expression.core import Error, Ok, Result, result
from expression.extra.result import sequence
from hypothesis import given
from hypothesis import strategies as st

from .utils import CustomException


def test_result_ok():
    xs: Result[int, str] = Ok(42)

    assert isinstance(xs, Result)
    assert xs.is_ok()
    assert not xs.is_error()
    assert str(xs) == "Ok 42"

    for x in xs.match(Ok):
        assert x == 42
        break
    else:
        assert False


def test_result_ok_iterate():
    for x in Ok(42):
        assert x == 42


def test_result_error():
    error = CustomException("d'oh!")
    xs: Result[str, Exception] = Error(error)

    assert isinstance(xs, Result)
    assert not xs.is_ok()
    assert xs.is_error()
    assert str(xs) == f"Error {error}"

    for _ in xs.match(Ok):
        assert False

    for ex in xs.match(Error):
        assert ex == error


def test_result_error_iterate():
    with pytest.raises(Error) as excinfo:  # type: ignore
        error: Error[int, str] = Error("err")
        for _ in error:
            assert False

    assert excinfo.value.error == "err"  # type: ignore


@given(st.integers(), st.integers())
def test_result_ok_equals_ok(x: int, y: int):
    xs: Result[int, Exception] = Ok(x)
    ys: Result[int, Exception] = Ok(y)

    assert xs == ys if x == y else xs != ys


@given(st.integers())
def test_result_ok_not_equals_error(x: int):
    assert not Ok(x) == Error(x)
    assert not Error(x) == Ok(x)


@given(st.text(), st.text())
def test_result_error_equals_error(x: int, y: int):
    xs: Result[int, int] = Error(x)
    ys: Result[int, int] = Error(y)

    assert xs == ys if x == y else xs != ys


@given(st.integers(), st.integers())
def test_result_map_piped(x: int, y: int):
    xs: Result[int, Exception] = Ok(x)
    mapper: Callable[[int], int] = lambda x: x + y

    ys = xs.pipe(result.map(mapper))
    for value in ys.match(Ok):
        assert value == mapper(x)
        break
    else:
        assert False


@given(st.integers(), st.integers())
def test_result_map_ok_fluent(x: int, y: int):
    xs: Result[int, Exception] = Ok(x)
    mapper: Callable[[int], int] = lambda x: x + y

    ys = xs.map(mapper)
    for value in ys.match(Ok):
        assert value == mapper(x)
        break
    else:
        assert False


@given(st.integers(), st.integers())
def test_result_ok_chained_map(x: int, y: int):
    xs: Result[int, Exception] = Ok(x)
    mapper1: Callable[[int], int] = lambda x: x + y
    mapper2: Callable[[int], int] = lambda x: x * 10

    ys = xs.map(mapper1).map(mapper2)

    for value in ys.match(Ok):
        assert value == mapper2(mapper1(x))
        break
    else:
        assert False


@given(st.text(), st.integers())
def test_result_map_error_piped(msg: str, y: int):
    xs: Result[int, str] = Error(msg)
    mapper: Callable[[int], int] = lambda x: x + y

    ys = xs.pipe(result.map(mapper))

    for err in ys.match(Error):
        assert err == msg
        break
    else:
        assert False


@given(st.text(), st.integers())
def test_result_map_error_fluent(msg: str, y: int):
    xs: Result[int, str] = Error(msg)
    mapper: Callable[[int], int] = lambda x: x + y

    ys = xs.map(mapper)
    for err in ys.match(Error):
        assert err == msg
        break
    else:
        assert False


@given(st.text(), st.integers())
def test_result_error_chained_map(msg: str, y: int):
    xs: Result[int, str] = Error(msg)
    mapper1: Callable[[int], int] = lambda x: x + y
    mapper2: Callable[[int], int] = lambda x: x * 10

    ys = xs.map(mapper1).map(mapper2)
    for err in ys.match(Error):
        assert err == msg
        break
    else:
        assert False


@given(st.integers(), st.integers())
def test_result_bind_piped(x: int, y: int):
    xs: Result[int, str] = Ok(x)
    mapper: Callable[[int], Result[int, str]] = lambda x: Ok(x + y)

    ys = xs.pipe(result.bind(mapper))
    for value in ys.match(Ok):
        assert Ok(value) == mapper(x)
        break
    else:
        assert False


@given(st.lists(st.integers()))
def test_result_traverse_ok(xs: List[int]):
    ys: List[Result[int, str]] = [Ok(x) for x in xs]
    zs = sequence(ys)
    for value in zs.match(Ok):
        assert sum(value) == sum(xs)
        break
    else:
        assert False


@given(st.lists(st.integers(), min_size=5))
def test_result_traverse_error(xs: List[int]):
    error = "Do'h"
    ys: List[Result[int, str]] = [Ok(x) if i == 3 else Error(error) for x, i in enumerate(xs)]

    zs = sequence(ys)
    for err in zs.match(Error):
        assert err == error


def test_result_builder_zero():
    @effect.result
    def fn():
        while False:
            yield

    with pytest.raises(NotImplementedError):
        fn()


def test_result_builder_yield_ok():
    @effect.result
    def fn() -> Generator[int, int, Optional[int]]:
        yield 42

    xs = fn()
    for x in xs:
        assert x == 42


def test_result_builder_return_ok():
    @effect.result
    def fn() -> Generator[int, int, int]:
        x = yield 42
        return x

    xs = fn()
    for x in xs.match(Ok):
        assert x == 42
        break
    else:
        assert False


def test_result_builder_yield_from_ok():
    @effect.result
    def fn() -> Generator[int, int, int]:
        x = yield from Ok(42)
        return x + 1

    xs = fn()
    for x in xs.match(Ok):
        assert x == 43
        break
    else:
        assert False


def test_result_builder_yield_from_error():
    error = "Do'h"

    @effect.result
    def fn() -> Generator[int, int, int]:
        x = yield from Error(error)
        return x

    xs = fn()
    for err in xs.match(Error):
        assert err == error
        break
    else:
        assert False, "Should not happen"


def test_result_builder_multiple_ok():
    @effect.result
    def fn() -> Generator[int, int, int]:
        x = yield 42
        y = yield from Ok(43)

        return x + y

    xs = fn()
    for value in xs.match(Ok):
        assert value == 85
        break
    else:
        assert False
