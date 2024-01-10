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
        shape.circle = Circle(20.0)  # type: ignore


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

@tagged_union(order=True, frozen=True)
class Maybe(Generic[_T]):
    tag: Literal["just", "nothing"] = tag()

    nothing: None = case()
    just: _T = case()

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

def test_union_order_just_just_works():
    xs = Maybe(just=1)
    ys = Maybe(just=2)
    assert xs < ys
    assert ys > xs

def test_union_order_just_nothing_works():
    xs = Maybe(just=1)
    ys = Maybe[int](nothing=None)
    assert xs > ys
    assert ys < xs

def test_union_order_nothing_just_works():
    xs = Maybe[int](nothing=None)
    ys = Maybe(just=1)
    assert xs < ys
    assert ys > xs

def test_union_order_nothing_nothing_works():
    xs = Maybe[int](nothing=None)
    ys = Maybe[int](nothing=None)
    assert not xs < ys
    assert not ys < xs

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

    # Test attribute access
    assert email.email == "test@test.com"
    assert email.tag == "email"  # type: ignore

    # Test pattern matching
    match email:
        case Email(email=e):
            assert e == "test@test.com"
        case _:  # pyright: ignore
            assert False


@tagged_union(frozen=True, repr=False)
class SecurePassword:
    password: str = case()

    # Override __str__ and __repr__ to make sure we don't leak the password in logs
    def __str__(self) -> str:
        return "********"

    def __repr__(self) -> str:
        return "SecurePassword(password='********')"


def test_single_case_union_secure_password_works():
    password = SecurePassword(password="secret")

    # Test attribute access
    assert password.password == "secret"
    assert password.tag == "password"  # type: ignore

    # Test pattern matching
    match password:
        case SecurePassword(password=p):
            assert p == "secret"

    # Test __str__
    assert str(password) == "********"

    # Test __repr__
    assert repr(password) == "SecurePassword(password='********')"


@tagged_union
class Suit:
    tag: Literal["spades", "hearts", "clubs", "diamonds"] = tag()

    spades: bool = case()
    hearts: bool = case()
    clubs: bool = case()
    diamonds: bool = case()

    @staticmethod
    def Spades() -> Suit:
        return Suit(spades=True)

    @staticmethod
    def Hearts() -> Suit:
        return Suit(hearts=True)

    @staticmethod
    def Clubs() -> Suit:
        return Suit(clubs=True)

    @staticmethod
    def Diamonds() -> Suit:
        return Suit(diamonds=True)


@tagged_union
class Face:
    tag: Literal["jack", "queen", "king", "ace"] = tag()

    jack: bool = case()
    queen: bool = case()
    king: bool = case()
    ace: bool = case()

    @staticmethod
    def Jack() -> Face:
        return Face(jack=True)

    @staticmethod
    def Queen() -> Face:
        return Face(queen=True)

    @staticmethod
    def King() -> Face:
        return Face(king=True)

    @staticmethod
    def Ace() -> Face:
        return Face(ace=True)


@tagged_union
class Card:
    tag: Literal["value_card", "face_card", "joker"] = tag()

    face_card: tuple[Suit, Face] = case()
    value_card: tuple[Suit, int] = case()
    joker: bool = case()

    @staticmethod
    def Face(suit: Suit, face: Face) -> Card:
        return Card(face_card=(suit, face))

    @staticmethod
    def Value(suit: Suit, value: int) -> Card:
        if value < 1 or value > 10:
            raise ValueError("Value must be between 1 and 10")
        return Card(value_card=(suit, value))

    @staticmethod
    def Joker() -> Card:
        return Card(joker=True)


def test_rummy_score():
    def score(card: Card) -> int:
        match card:
            case Card(tag="face_card", face_card=(Suit(spades=True), Face(queen=True))):
                return 40
            case Card(tag="face_card", face_card=(_suit, Face(ace=True))):
                return 15
            case Card(tag="face_card", face_card=(_suit, _face)):
                return 10
            case Card(tag="value_card", value_card=(_suit, value)):
                return value
            case Card(tag="joker", joker=True):
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
    assert score(Card.Face(Suit.Hearts(), Face.Ace())) == 15
    assert score(Card.Face(Suit.Hearts(), Face.King())) == 10
    assert score(Card.Face(Suit.Clubs(), Face.Ace())) == 15
    assert score(Card.Face(Suit.Clubs(), Face.King())) == 10
    assert score(Card.Face(Suit.Clubs(), Face.Queen())) == 10
    assert score(Card.Face(Suit.Clubs(), Face.Jack())) == 10
    assert score(Card.Face(Suit.Diamonds(), Face.Ace())) == 15
    assert score(Card.Face(Suit.Diamonds(), Face.King())) == 10
    assert score(Card.Face(Suit.Diamonds(), Face.Queen())) == 10
    assert score(Card.Face(Suit.Diamonds(), Face.Jack())) == 10
    assert score(Card.Value(Suit.Hearts(), 1)) == 1
    assert score(Card.Value(Suit.Hearts(), 2)) == 2
    assert score(Card.Value(Suit.Hearts(), 3)) == 3
    assert score(Card.Value(Suit.Hearts(), 4)) == 4
    assert score(Card.Value(Suit.Hearts(), 5)) == 5
    assert score(Card.Value(Suit.Hearts(), 6)) == 6
    assert score(Card.Value(Suit.Hearts(), 7)) == 7
    assert score(Card.Value(Suit.Hearts(), 8)) == 8
    assert score(Card.Value(Suit.Hearts(), 9)) == 9
    assert score(Card.Value(Suit.Hearts(), 10)) == 10
