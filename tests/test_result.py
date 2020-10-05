import pytest
from hypothesis import given, strategies as st
from pampy import match, _

from fslash import Result, Ok, Error, result, TResult, pipe
from .utils import CustomException, throw


def test_result_ok():
    xs = Ok(42)

    assert(isinstance(xs, TResult))
    res = match(xs,
                Ok, lambda ok: ok.value,
                Error, lambda error: throw(error.error))
    assert(res == 42)


def test_result_error():
    xs = Error(CustomException("d'oh!"))

    assert(isinstance(xs, TResult))
    with pytest.raises(CustomException):
        match(xs,
              Ok, lambda ok: ok.value,
              Error, lambda error: throw(error.error))


@given(st.integers(), st.integers())
def test_result_map_piped(x, y):
    xs = Ok(x)
    mapper = lambda x: x + y

    ys = pipe(xs, Result.map(mapper))
    res = match(ys,
                Ok, lambda ok: ok.value,
                Error, lambda error: throw(error.error))
    assert(res == mapper(x))


@given(st.integers(), st.integers())
def test_result_map_fluent(x, y):
    xs = Ok(x)
    mapper = lambda x: x + y

    ys = xs.map(mapper)
    res = match(ys,
                Ok, lambda ok: ok.value,
                Error, lambda error: throw(error.error))
    assert(res == mapper(x))


@given(st.integers(), st.integers())
def test_result_chained_map(x, y):
    xs = Ok(x)
    mapper1 = lambda x: x + y
    mapper2 = lambda x: x * 10

    ys = xs.map(mapper1).map(mapper2)
    res = match(ys,
                Ok, lambda ok: ok.value,
                Error, lambda error: throw(error.error))
    assert(res == mapper2(mapper1(x)))


@given(st.integers(), st.integers())
def test_result_bind_piped(x, y):
    xs = Ok(x)
    mapper = lambda x: Ok(x + y)

    ys = pipe(xs, Result.bind(mapper))
    res = match(ys,
                Ok, lambda ok: ok.value,
                Error, lambda error: throw(error.error))
    assert(Ok(res) == mapper(x))


def test_result_builder_zero():
    @result
    def fn():
        yield

    xs = fn()
    assert match(
        xs,
        Error, lambda error: True,
        _, True
    )


def test_result_builder_yield_ok():
    @result
    def fn():
        yield 42

    xs = fn()
    assert 42 == match(
        xs,
        Ok, lambda ok: ok.value,
        _, None
    )


def test_result_builder_return_ok():
    @result
    def fn():
        x = yield 42
        return x

    xs = fn()
    assert 42 == match(
        xs,
        Ok, lambda ok: ok.value,
        _, None
    )


def test_result_builder_yield_from_ok():
    @result
    def fn():
        x = yield from Ok(42)
        return x + 1

    xs = fn()
    assert 43 == match(
        xs,
        Ok, lambda some: some.value,
        _, None
    )


def test_result_builder_yield_from_error():
    error = "Do'h"

    @result
    def fn():
        x = yield from Error(error)
        return x

    xs = fn()
    assert match(
        xs,
        Ok, lambda some: some.value,
        Error, lambda error: error.error
    ) == error


def test_result_builder_multiple_ok():
    @result
    def fn():
        x = yield 42
        y = yield from Ok(43)

        return x + y

    xs = fn()
    assert 85 == match(
        xs,
        Ok, lambda ok: ok.value,
        _, None
    )
