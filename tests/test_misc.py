from typing import Any, List

from expression.core.misc import downcast, try_upcast, upcast
from hypothesis import given
from hypothesis import strategies as st


class Base:
    pass


class Derived(Base):
    pass


class Other(Base):
    pass


def test_downcast():
    # Arrange
    d = Derived()

    # Act
    b = downcast(Base, d)

    # Assert
    assert isinstance(b, Base)
    assert isinstance(b, Derived)


def test_downcast_negative():
    # Arrange
    d = Derived()

    # Act / Assert
    try:
        downcast(Other, d)
    except AssertionError:
        pass


def test_upcast():
    # Arrange
    d = Derived()
    c = downcast(Base, d)

    # Act
    d = upcast(Derived, c)

    # Assert
    assert isinstance(d, Base)
    assert isinstance(d, Derived)


def test_upcast_negative():
    # Arrange
    d = Derived()
    c = downcast(Base, d)

    # Act / Assert
    try:
        d = upcast(Other, c)
    except AssertionError:
        pass


def test_try_cast():
    # Arrange
    d = Derived()
    b = downcast(Base, d)

    # Act
    c = try_upcast(Derived, b)

    # Assert
    assert isinstance(c, Derived)


def test_try_cast_negative():
    # Arrange
    d = Derived()
    b = downcast(Base, d)

    # Act
    c = try_upcast(Other, b)

    # Assert
    assert not c


def test_try_cast_generic():
    # Arrange
    d: List[Derived] = [Derived()]

    # Act
    b = try_upcast(List[Any], d)

    # Assert
    assert isinstance(b, List)


def test_try_cast_generic_negative():
    # Arrange
    d: List[Derived] = [Derived()]

    # Act
    b = try_upcast(str, d)

    # Assert
    assert b is None
