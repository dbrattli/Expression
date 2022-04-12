from __future__ import annotations

from dataclasses import dataclass

from expression import DiscriminatedUnion, match


@dataclass
class Rectangle:
    width: float
    length: float


@dataclass
class Circle:
    radius: float


class Shape(DiscriminatedUnion[Circle, Rectangle]):
    @staticmethod
    def Rectangle(width: float, length: float) -> Shape:
        return Shape(Rectangle(width, length), tag=1)

    @staticmethod
    def Circle(radius: float) -> Shape:
        return Shape(Circle(radius), tag=2)


def test_union_create():
    shape = Shape.Circle(2.3)
    assert shape.tag == 2
    assert shape.value == Circle(2.3)


def test_union_match_tag():
    shape = Shape.Rectangle(2.3, 3.3)

    with match(shape.tag) as case:
        for _ in case(2):
            assert False
        for _ in case(1):
            assert True

        if case.default():
            assert False


def test_union_match():
    shape = Shape.Rectangle(2.3, 3.3)

    with match(shape) as case:
        for _ in case(Circle):
            assert False
        for rect in case(Rectangle):
            assert rect.length == 3.3

        if case.default():
            assert False
