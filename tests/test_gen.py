"""
This file is just to explore how generators works
"""
from typing import Generator, Optional

import pytest

# from hypothesis import given, strategies as st


def test_generator_with_single_empty_yield():
    def fn():
        yield

    gen = fn()
    value = next(gen)
    assert value is None


def test_generator_with_single_empty_yield_double_next():
    def fn():
        yield

    gen = fn()
    value = next(gen)
    assert value is None
    with pytest.raises(StopIteration) as ex:  # type: ignore
        next(gen)
    assert ex.value.value is None


def test_generator_with_single_yield_value():
    def fn():
        yield 42

    gen = fn()
    value = next(gen)
    assert value == 42


def test_generator_with_multiple_yield_value():
    def fn():
        yield 2
        yield 4

    gen = fn()
    value = next(gen)
    assert value == 2
    value = next(gen)
    assert value == 4


def test_generator_with_single_return_value():
    def fn():
        return 42
        yield

    gen = fn()

    # Return in a generator is just syntactic sugar for raise StopIteration
    with pytest.raises(StopIteration) as ex:  # type: ignore
        next(gen)  # type: ignore
    assert ex.value.value == 42


def test_generator_with_multiple_return_value():
    def fn():
        return 2
        return 4
        yield

    gen = fn()

    # Return in a generator is just syntactic sugar for raise StopIteration
    with pytest.raises(StopIteration) as ex:  # type: ignore
        next(gen)  # type: ignore
    assert ex.value.value == 2

    with pytest.raises(StopIteration) as ex:  # type: ignore
        next(gen)  # type: ignore

    # Cannot get value from second return
    assert ex.value.value is None


def test_generator_with_yield_assignment_and_yield():
    def fn() -> Generator[int, int, Optional[int]]:
        x = yield 42
        yield x

    gen = fn()
    value = next(gen)
    assert value == 42
    value = gen.send(10)  # type: ignore
    assert value == 10


def test_generator_with_yield_assignment_and_return():
    def fn() -> Generator[int, int, int]:
        x = yield 42
        return x

    gen = fn()
    value = next(gen)
    assert value == 42
    with pytest.raises(StopIteration) as ex:  # type: ignore
        gen.send(10)  # type: ignore
    assert ex.value.value == 10


def test_generator_with_yield_from():
    def fn():
        yield from [42]

    gen = fn()
    value = next(gen)
    assert value == 42


def test_generator_with_yield_from_gen():
    def gn():
        yield 42

    def fn():
        yield from gn()

    gen = fn()
    value = next(gen)
    assert value == 42


def test_generator_with_yield_from_gen_empty():
    def gn():
        yield from []

    def fn():
        yield from gn()
        yield 42

    gen = fn()
    value = next(gen)
    assert value == 42
