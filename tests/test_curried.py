import pytest

from expression import curried


def test_curried_simple():
    @curried(1)
    def add(a: int, b: int) -> int:
        """Add a + b"""
        return a + b

    assert add(3)(4) == 7


def test_curried_named():
    @curried(1)
    def add(a: int, b: int) -> int:
        """Add a + b"""
        return a + b

    assert add(3)(b=4) == 7


def test_curried_none():
    @curried(0)
    def magic() -> int:
        return 42

    assert magic() == 42
    with pytest.raises(TypeError):
        magic(42)  # type:ignore


def test_curried_three():
    @curried(2)
    def add(a: int, b: int, c: int) -> int:
        """Add a + b + c"""
        return a + b + c

    assert add(3)(4)(2) == 9


def test_curry1of3_with_optional():
    @curried(1)
    def add(a: int, b: int, c: int = 10) -> int:
        """Add a + b + c"""
        return a + b + c

    assert add(3)(4) == 17


def test_curry2of3_with_optional():
    @curried(2)
    def add(a: int, b: int, c: int = 10) -> int:
        """Add a + b + c"""
        return a + b + c

    assert add(3)(4)() == 17


def test_curry1of3_with_optional2():
    @curried(1)
    def add(a: int, b: int, c: int = 10) -> int:
        """Add a + b + c"""
        return a + b + c

    assert add(3)(4, c=9) == 16
