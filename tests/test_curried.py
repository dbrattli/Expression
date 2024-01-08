from collections.abc import Callable

import pytest

from expression import curry, curry_flip, pipe


def test_curry_identity():
    @curry(0)
    def add(a: int, b: int) -> int:
        """Add a + b"""
        return a + b

    assert add(3, 4) == 7


def test_curry_simple():
    @curry(1)
    def add(a: int, b: int) -> int:
        """Add a + b"""
        return a + b

    assert add(3)(4) == 7


def test_curry_simple_curry_2_of_2():
    @curry(2)
    def add(a: int, b: int) -> int:
        """Add a + b"""
        return a + b

    assert add(3)(4)() == 7


def test_curry_named():
    @curry(1)
    def add(a: int, b: int) -> int:
        """Add a + b"""
        return a + b

    assert add(3)(b=4) == 7


def test_curry_none():
    @curry(0)
    def magic() -> int:
        return 42

    assert magic() == 42
    with pytest.raises(TypeError):
        magic(42)  # type:ignore


def test_curry_three():
    @curry(2)
    def add(a: int, b: int, c: int) -> int:
        """Add a + b + c"""
        return a + b + c

    assert add(3)(4)(2) == 9


def test_curry1of3_with_optional():
    @curry(1)
    def add(a: int, b: int, c: int = 10) -> int:
        """Add a + b + c"""
        return a + b + c

    assert add(3)(4) == 17


def test_curry2of3_with_optional():
    @curry(2)
    def add(a: int, b: int, c: int = 10) -> int:
        """Add a + b + c"""
        return a + b + c

    assert add(3)(4)() == 17


def test_curry1of3_with_optional2():
    @curry(1)
    def add(a: int, b: int, c: int = 10) -> int:
        """Add a + b + c"""
        return a + b + c

    assert add(3)(4, c=9) == 16


def test_curry_flip_identity():
    @curry_flip(0)
    def add(a: int, b: int) -> int:
        """Add a + b"""
        return a + b

    assert add(3, 4) == 7


def test_curry_flip_1():
    xs = [1, 2, 3]

    @curry_flip(1)
    def map(source: list[int], mapper: Callable[[int], int]):
        return [mapper(x) for x in source]

    ys = pipe(
        xs,
        map(mapper=lambda x: x * 10),
    )

    assert ys == [10, 20, 30]


def test_curry_flip_2():
    xs = [1, 2, 3]

    @curry_flip(2)
    def map(a: int, source: list[int], mapper: Callable[[int], int]):
        return [mapper(x) + a for x in source]

    ys = pipe(xs, map(lambda x: x * 10)(10))

    assert ys == [20, 30, 40]
