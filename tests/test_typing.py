import subprocess
import sys
from typing import Any, assert_type, cast

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
    assert b is d
    assert_type(b, Base)


def test_upcast_negative():
    # Arrange
    d = Derived()

    # Act / Assert
    with pytest.raises(TypeError, match="incompatible runtime type"):
        upcast(Other, d)


def test_downcast():
    # Arrange
    b = cast(Base, Derived())

    # Act
    d = downcast(Derived, b)

    # Assert
    assert d is b
    assert_type(d, Derived)


def test_downcast_negative():
    # Arrange
    b = cast(Base, Derived())

    # Act / Assert
    with pytest.raises(TypeError, match="incompatible runtime type"):
        downcast(Other, b)


def test_try_downcast():
    # Arrange
    b = cast(Base, Derived())

    # Act
    c = try_downcast(Derived, b)

    # Assert
    assert c is b
    assert_type(c, Derived | None)


def test_try_downcast_negative():
    # Arrange
    b = cast(Base, Derived())

    # Act
    c = try_downcast(Other, b)

    # Assert
    assert c is None


def test_try_cast_parameterized_generic_is_unsupported():
    # Arrange
    d: list[Derived] = [Derived()]

    # Act
    with pytest.raises(TypeError):
        try_downcast(list[Any], d)


def test_try_cast_generic_negative():
    # Arrange
    d: list[Derived] = [Derived()]

    # Act
    b = try_downcast(str, d)

    # Assert
    assert b is None


def test_parameterized_downcasts_reject_unchecked_element_types():
    values: object = ["wrong"]
    with pytest.raises(TypeError):
        downcast(list[int], values)
    with pytest.raises(TypeError):
        try_downcast(list[int], values)


def test_cast_checks_survive_optimization():
    script = """
from expression import downcast, upcast
for cast_value in (downcast, upcast):
    try:
        cast_value(int, "wrong")
    except TypeError:
        pass
    else:
        raise RuntimeError("Invalid cast succeeded under optimization")
"""
    subprocess.run([sys.executable, "-O", "-c", script], check=True, capture_output=True, text=True)


def test_downcast_accepts_subclasses_and_preserves_identity():
    value = Derived()
    assert downcast(Base, value) is value
    assert try_downcast(Base, value) is value


def test_upcast_rejects_invalid_narrowing():
    with pytest.raises(TypeError):
        upcast(Derived, Base())


def test_upcast_rejects_parameterized_target():
    with pytest.raises(TypeError):
        upcast(list[int], [1])
