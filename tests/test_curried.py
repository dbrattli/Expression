from typing import Callable, overload

import pytest

from expression import curried


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
