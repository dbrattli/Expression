from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Generic, Literal, TypeVar

import pytest

from expression import case, tag, tagged_union

_T = TypeVar("_T")


@dataclass(unsafe_hash=True)
class Circle:
    radius: float


@tagged_union(frozen=True)
class Shape:
    tag: Literal["circle", "rectangle", "triangle"] = tag()

    circle: Circle = case()
    rectangle: tuple[float, float] = case()
    triangle: tuple[float, float] = case()


def test_union_create_shape_works():
    shape = Shape(circle=Circle(10.0))
    assert shape.circle.radius == 10.0


def test_union_shape_tag_is_set():
    shape = Shape(circle=Circle(10.0))
    assert shape.tag == "circle"


def test_union_shape_circle_pattern_matching_works():
    shape = Shape(circle=Circle(10.0))

    match shape:
        case Shape(tag="rectangle", rectangle=(_, _)):
            raise AssertionError("Should not match")
        case Shape(tag="circle", circle=Circle(radius=r)):
            assert r == 10.0
        case _:
            assert False


def test_shape_rectangle_pattern_matching_works():
    shape = Shape(rectangle=(10.0, 20.0))

    match shape:
        case Shape(tag="circle", circle=Circle(radius=_)):
            raise AssertionError("Should not match")
        case Shape(tag="rectangle", rectangle=(w, h)):
            assert w == 10.0
            assert h == 20.0
        case _:
            assert False


def test_union_shape_hash_works():
    shape = Shape(circle=Circle(10.0))
    assert hash(shape) == hash(("Shape", "circle", Circle(10.0)))


def test_union_shape_repr_works():
    shape = Shape(circle=Circle(10.0))
    assert repr(shape) == "Shape(circle=Circle(radius=10.0))"


def test_union_can_add_custom_attributes_to_shape():
    shape = Shape(circle=Circle(10.0))
    setattr(shape, "custom", "rectangle")
    assert getattr(shape, "custom") == "rectangle"


def test_union_cannot_change_case_value():
    shape = Shape(circle=Circle(10.0))
    with pytest.raises(TypeError):
        shape.circle = Circle(20.0) # type: ignore


def test_union_compare_shapes():
    shape1 = Shape(circle=Circle(10.0))
    shape2 = Shape(circle=Circle(10.0))
    assert shape1 == shape2

    shape3 = Shape(rectangle=(10.0, 20.0))
    assert shape1 != shape3


def test_union_compare_shapes_with_different_tags():
    shape1 = Shape(circle=Circle(10.0))
    shape2 = Shape(rectangle=(10.0, 20.0))
    assert shape1 != shape2


@tagged_union
class Maybe(Generic[_T]):
    tag: Literal["just", "nothing"] = tag()

    just: _T = case()
    nothing: None = case()


def test_maybe_works():
    xs = Maybe(just=1)
    match xs:
        case Maybe(tag="just", just=x):
            assert x == 1
        case _:
            assert False


def test_maybe_just_works():
    xs = Maybe(just=1)
    match xs:
        case Maybe(tag="just", just=x):
            assert x == 1
        case Maybe(tag="nothing", nothing=None):
            assert False
        case _:
            assert False

def test_maybe_nothing_works():
    xs = Maybe[int](nothing=None)
    match xs:
        case Maybe(tag="nothing", nothing=None):
            assert True
        case _:
            assert False


def test_nested_unions_works():
    xs = Maybe(just=Shape(circle=Circle(10.0)))
    match xs:
        case Maybe(tag="just", just=Shape(tag="circle", circle=Circle(radius=r))):
            assert r == 10.0
        case _:
            assert False


def test_union_maybe_asdict_works():
    xs = Maybe(just=1)
    assert asdict(xs) == {"tag": "just", "just": 1}


def test_unions_can_be_composed():
    @tagged_union
    class Weather:
        tag: Literal["sunny", "rainy"] = tag()

        sunny: bool = case()
        rainy: bool = case()

    @tagged_union
    class Day:
        tag: Literal["weekday", "weekend"] = tag()

        weekday: Weather = case()
        weekend: Weather = case()

    today = Day(weekday=Weather(sunny=True))
    match today:
        case Day(tag="weekday", weekday=Weather(tag="sunny", sunny=s)):
            assert s is True
        case _:
            assert False


@tagged_union
class Email:
    email: str = case()


def test_single_case_union_works():
    email = Email(email="test@test.com")
    match email:
        case Email(email=e):
            assert e == "test@test.com"
        case _: # pyright: ignore
            assert False


@tagged_union
class Suit:
    tag: Literal["spades", "hearts", "clubs", "diamonds"] = tag()

    spades: None = case()
    hearts: None = case()
    clubs: None = case()
    diamonds: None = case()

    @staticmethod
    def Spades() -> Suit:
        return Suit(spades=None)

    @staticmethod
    def Hearts() -> Suit:
        return Suit(hearts=None)

    @staticmethod
    def Clubs() -> Suit:
        return Suit(clubs=None)

    @staticmethod
    def Diamonds() -> Suit:
        return Suit(diamonds=None)


@tagged_union
class Face:
    tag: Literal["jack", "queen", "king", "ace"] = tag()

    jack: None = case()
    queen: None = case()
    king: None = case()
    ace: None = case()

    @staticmethod
    def Jack() -> Face:
        return Face(jack=None)

    @staticmethod
    def Queen() -> Face:
        return Face(queen=None)

    @staticmethod
    def King() -> Face:
        return Face(king=None)

    @staticmethod
    def Ace() -> Face:
        return Face(ace=None)


@tagged_union
class Card:
    tag: Literal["value_card", "face_card", "joker"] = tag()

    face_card: tuple[Suit, Face] = case()
    value_card: tuple[Suit, int] = case()
    joker: None = case()

    @staticmethod
    def Face(suit: Suit, face: Face) -> Card:
        return Card(face_card=(suit, face))

    @staticmethod
    def Value(suit: Suit, value: int) -> Card:
        return Card(value_card=(suit, value))

    @staticmethod
    def Joker() -> Card:
        return Card(joker=None)


def test_rummy_score():
    def score(card: Card) -> int:
        match card:
            case Card(tag="face_card", face_card=(Suit(spades=None), Face(queen=None))):
                return 40
            case Card(tag="face_card", face_card=(_suit, Face(ace=None))):
                return 15
            case Card(tag="face_card", face_card=(_suit, _face)):
                return 10
            case Card(tag="value_card", value_card=(_suit, value)):
                return value
            case Card(tag="joker", joker=None):
                return 0
            case _:
                raise AssertionError("Should not match")

    assert score(Card.Face(Suit.Spades(), Face.Jack())) == 10
    assert score(Card.Value(Suit.Spades(), 5)) == 5
    assert score(Card.Joker()) == 0
    assert score(Card.Face(Suit.Spades(), Face.Queen())) == 40
    assert score(Card.Face(Suit.Spades(), Face.King())) == 10
    assert score(Card.Face(Suit.Spades(), Face.Ace())) == 15
    assert score(Card.Face(Suit.Spades(), Face.Ace())) == 15
