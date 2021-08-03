from typing import Any, List, cast

import pytest

from expression import downcast, try_downcast, upcast


class Base:
    pass


class Derived(Base):
    pass


class Other:
    pass


def test_upcast():
    # Arrange
    d = Derived()

    # Act
    b = upcast(Base, d)

    # Assert
    assert isinstance(b, Base)
    assert isinstance(b, Derived)


def test_upcast_negative():
    # Arrange
    d = Derived()

    # Act / Assert
    x = upcast(Other, d)

    with pytest.raises(AssertionError):
        assert isinstance(x, Other)


def test_downcast():
    # Arrange
    b = cast(Base, Derived())

    # Act
    d = downcast(Derived, b)

    # Assert
    assert isinstance(d, Base)
    assert isinstance(d, Derived)


def test_downcast_negative():
    # Arrange
    b = cast(Base, Derived())

    # Act / Assert
    try:
        downcast(Other, b)
    except AssertionError:
        pass


def test_try_downcast():
    # Arrange
    b = cast(Base, Derived())

    # Act
    c = try_downcast(Derived, b)

    # Assert
    assert isinstance(c, Derived)


def test_try_downcast_negative():
    # Arrange
    b = cast(Base, Derived())

    # Act
    c = try_downcast(Other, b)

    # Assert
    assert c is None


def test_try_cast_generic():
    # Arrange
    d: List[Derived] = [Derived()]

    # Act
    b = try_downcast(List[Any], d)

    # Assert
    assert isinstance(b, List)


def test_try_cast_generic_negative():
    # Arrange
    d: List[Derived] = [Derived()]

    # Act
    b = try_downcast(str, d)

    # Assert
    assert b is None
