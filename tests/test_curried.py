from typing import Callable, overload

import pytest

from expression import (
    curried,
    curry1of2,
    curry1of3,
    curry1of4,
    curry2of2,
    curry2of3,
    curry2of4,
    curry3of3,
    curry3of4,
    curry4of4,
)


def test_curried_simple():
    @curried
    def add(a: int, b: int) -> int:
        """Add a + b"""
        return a + b

    assert add(3, 4) == 7
    assert add()(3, 4) == 7
    assert add(3)(4) == 7
    assert add()(3)(4) == 7
    assert add()(3)()(4) == 7
    assert add()()(3)()()(4) == 7


def test_curried_named():
    @curried
    def add(a: int, b: int) -> int:
        """Add a + b"""
        return a + b

    assert add(3, b=4) == 7
    assert add(a=3, b=4) == 7
    assert add(3)(b=4) == 7
    assert add(a=3)(b=4) == 7
    assert add(3)(b=4) == 7
    assert add()(3)(b=4) == 7
    assert add()(3)()(b=4) == 7


def test_curried_starred_args():
    @curried
    def add(a: int, b: int) -> int:
        """Add a + b"""
        return a + b

    assert add(*[3, 4]) == 7
    assert add(**dict(a=3, b=4)) == 7


def test_curried_none():
    @curried
    def magic() -> int:
        return 42

    assert magic() == 42
    with pytest.raises(TypeError):  # type:ignore
        magic(42)


def test_curried_three():
    @curried
    def add(a: int, b: int, c: int) -> int:
        """Add a + b + c"""
        return a + b + c

    assert add(3, 4, 2) == 9
    assert add(3)(4, 2) == 9
    assert add(3, 4)(2) == 9
    assert add(3)(4)(2) == 9
    assert add()(3)()(4)()(2) == 9

    with pytest.raises(TypeError):  # type:ignore
        add(3, 4, 5, 6)

    with pytest.raises(TypeError):  # type:ignore
        add(3, 4, 5)(6, 7)


def test_curried_typed():
    @overload
    def add(a: int, b: int) -> int:
        ...

    @overload
    def add(a: int) -> Callable[[int], int]:
        ...

    @curried
    def add(a: int, b: int) -> int:
        """Add a + b"""
        return a + b

    assert add(3, 4) == 7
    assert add(3)(4) == 7


def test_curry1of2():
    @curry1of2
    def add(a: int, b: int) -> int:
        """Add a + b"""
        return a + b

    assert add(3)(4) == 7


def test_curry2of2():
    @curry2of2
    def add(a: int, b: int) -> int:
        """Add a + b"""
        return a + b

    assert add()(3)(4) == 7


def test_curry1of3():
    @curry1of3
    def add(a: int, b: int, c: int) -> int:
        """Add a + b + c"""
        return a + b + c

    assert add(3, 4)(2) == 9


def test_curry2of3():
    @curry2of3
    def add(a: int, b: int, c: int) -> int:
        """Add a + b + c"""
        return a + b + c

    assert add(3)(4)(2) == 9


def test_curry3of3():
    @curry3of3
    def add(a: int, b: int, c: int) -> int:
        """Add a + b + c"""
        return a + b + c

    print("%d" % add()(3)(4)(2))
    assert add()(3)(4)(2) == 9


def test_curry1of4():
    @curry1of4
    def add(a: int, b: int, c: int, d: int) -> int:
        """Add a + b + c + d"""
        return a + b + c + d

    assert add(3, 4, 5)(2) == 14


def test_curry2of4():
    @curry2of4
    def add(a: int, b: int, c: int, d: int) -> int:
        """Add a + b + c + d"""
        return a + b + c + d

    assert add(3, 4)(5)(2) == 14


def test_curry3of4():
    @curry3of4
    def add(a: int, b: int, c: int, d: int) -> int:
        """Add a + b + c + d"""
        return a + b + c + d

    assert add(3)(4)(5)(2) == 14


def test_curry4of4():
    @curry4of4
    def add(a: int, b: int, c: int, d: int) -> int:
        """Add a + b + c + d"""
        return a + b + c + d

    assert add()(3)(4)(5)(2) == 14
