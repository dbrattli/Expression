from typing import Annotated, Any, cast

import pytest

from expression import Option, Result, downcast, try_downcast, upcast
from expression.core.typing import fetch_type


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
    d: list[Derived] = [Derived()]

    # Act
    b = try_downcast(list[Any], d)

    # Assert
    assert isinstance(b, list)


def test_try_cast_generic_negative():
    # Arrange
    d: list[Derived] = [Derived()]

    # Act
    b = try_downcast(str, d)

    # Assert
    assert b is None


@pytest.mark.parametrize(
    ("type_", "expect"),
    (
        (None, None),
        (int, int),
        ("int", int),
        (Annotated[int, 1], int),
        (Annotated[Annotated[str, 1], 2], str),
        ("Annotated[Annotated[str, 1], 2]", str),
        ("Annotated[Annotated[str, 1], 2]", str),
    ),
)
def test_fetch_nested_type(type_: Any, expect: Any):
    value = fetch_type(type_)
    assert value is expect


@pytest.mark.parametrize(
    "type_", (Option[int], Option[Annotated[int, int]], Result[int, Any], Result[Annotated[int, 1], Any])
)
def test_expression_to_expression(type_: Any):
    value = fetch_type(type_)
    assert value is type_
