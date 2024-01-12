"""This file is just to explore how generators works
"""
from collections.abc import Generator

import pytest


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
    with pytest.raises(StopIteration) as ex:
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
    with pytest.raises(StopIteration) as ex:
        next(gen)  # type: ignore
    assert ex.value.value == 42


def test_generator_with_multiple_return_value():
    def fn():
        return 2
        return 4
        yield

    gen = fn()

    # Return in a generator is just syntactic sugar for raise StopIteration
    with pytest.raises(StopIteration) as ex:
        next(gen)  # type: ignore
    assert ex.value.value == 2

    with pytest.raises(StopIteration) as ex:
        next(gen)  # type: ignore

    # Cannot get value from second return
    assert ex.value.value is None


def test_generator_with_yield_assignment_and_yield():
    def fn() -> Generator[int, int, None]:
        x = yield 42
        yield x

    gen = fn()
    value = next(gen)
    assert value == 42
    value = gen.send(10)
    assert value == 10


def test_generator_with_yield_assignment_and_return():
    def fn() -> Generator[int, int, int]:
        x = yield 42
        return x

    gen = fn()
    value = next(gen)
    assert value == 42
    with pytest.raises(StopIteration) as ex:
        gen.send(10)  # type: ignore
    assert ex.value.value == 10


def test_generator_with_yield_from():
    def fn() -> Generator[int, None, None]:
        yield from [42]

    gen = fn()
    value = next(gen)
    assert value == 42


def test_generator_with_yield_from_subgen():
    def gn():
        yield 42

    def fn() -> Generator[int, None, None]:
        yield from gn()

    gen = fn()
    value = next(gen)
    assert value == 42


def test_generator_with_yield_from_gen_empty():
    def gn() -> Generator[int, None, None]:
        yield from []

    def fn() -> Generator[int, None, None]:
        yield from gn()
        yield 42

    gen = fn()
    value = next(gen)
    assert value == 42

def test_generator_with_yield_from_send_to_subgen():
    def gn() -> Generator[int, int|None, int]:
        ret = yield 42
        print("subgenerator: ret", ret)
        assert ret is not None
        return ret + 1

    def fn() -> Generator[int, int|None, int]:
        ret = yield from gn()
        print("generator: ret", ret)
        return ret +1

    gen = fn()
    value = gen.send(None)
    assert value == 42
    try:
        value = gen.send(10)
    except StopIteration as ex:
        print("StopIteration", ex.value)
        assert ex.value == 12
