from typing import Callable, overload

from fslash.core import curried


def test_curried_simple():
    @curried
    def add(a: int, b: int) -> int:
        """Add a + b"""
        return a + b

    assert add(3)(4) == 7


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
