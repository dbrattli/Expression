from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Tuple, TypeVar, final

from expression import SingleCaseUnion, Tag, TaggedUnion, match

_T = TypeVar("_T")


@dataclass
class Rectangle:
    width: float
    length: float


@dataclass
class Circle:
    radius: float


@final
class Shape(TaggedUnion):
    RECTANGLE = Tag[Rectangle]()
    CIRCLE = Tag[Circle]()

    @staticmethod
    def rectangle(width: float, length: float) -> Shape:
        return Shape(Shape.RECTANGLE, Rectangle(width, length))

    @staticmethod
    def circle(radius: float) -> Shape:
        return Shape(Shape.CIRCLE, Circle(radius))


def test_union_create():
    shape = Shape.circle(2.3)
    assert shape.tag == Shape.CIRCLE
    assert shape.value == Circle(2.3)


def test_union_match_tag():
    shape = Shape.rectangle(2.3, 3.3)

    with match(shape.tag) as case:
        if case(Shape.CIRCLE):
            assert False
        if case(Shape.RECTANGLE):
            assert True
        if case.default():
            assert False


def test_union_match_type():
    shape = Shape.rectangle(2.3, 3.3)

    with match(shape) as case:
        for rect in case(Rectangle):
            assert rect.length == 3.3
        if case.default():
            assert False


def test_union_match_value():
    shape = Shape.rectangle(2.3, 3.3)

    with match(shape) as case:
        for rect in case(Shape.RECTANGLE(width=2.3)):
            assert rect.length == 3.3
        if case.default():
            assert False


def test_union_no_match_value():
    shape = Shape.rectangle(2.3, 3.3)

    with match(shape) as case:
        if case(Shape.RECTANGLE(width=12.3)):
            assert False
        if case.default():
            assert True


@final
class Weather(TaggedUnion):
    Sunny = Tag[None]()
    Rainy = Tag[None]()

    @staticmethod
    def sunny() -> Weather:
        return Weather(Weather.Sunny)

    @staticmethod
    def rainy() -> Weather:
        return Weather(Weather.Rainy)


def test_union_wether_match():
    rainy = Weather.sunny()

    with match(rainy) as case:
        if case(Weather.Rainy):
            assert False
        if case(Weather.Sunny):
            assert True
        if case.default():
            assert False


class Maybe(TaggedUnion, Generic[_T]):
    NOTHING = Tag[None]()
    JUST = Tag[_T]()

    @staticmethod
    def just(value: _T) -> Maybe[_T]:
        return Maybe[_T](Maybe.JUST, value)

    @staticmethod
    def nothing() -> Maybe[None]:
        return Maybe[None](Maybe.NOTHING)


def test_union_maybe_match():
    maybe = Maybe.just(10)

    with match(maybe) as case:
        if case(Maybe.NOTHING):
            assert False
        for value in case(
            maybe.JUST
        ):  # Note the lower-case maybe to get the type right
            assert value == 10

        if case.default():
            assert False


@final
class Suit(TaggedUnion):
    HEARTS = Tag[None]
    SPADES = Tag[None]()
    CLUBS = Tag[None]()
    DIAMONDS = Tag[None]()

    @staticmethod
    def hearts() -> Suit:
        return Suit(Suit.HEARTS())

    @staticmethod
    def spades() -> Suit:
        return Suit(Suit.SPADES)

    @staticmethod
    def clubs() -> Suit:
        return Suit(Suit.CLUBS)

    @staticmethod
    def diamonds() -> Suit:
        return Suit(Suit.DIAMONDS)


@final
class Face(TaggedUnion):
    JACK = Tag[None]()
    QUEEN = Tag[None]()
    KIND = Tag[None]()
    ACE = Tag[None]()

    @staticmethod
    def jack() -> Face:
        return Face(Face.JACK)

    @staticmethod
    def queen() -> Face:
        return Face(Face.QUEEN)

    @staticmethod
    def king() -> Face:
        return Face(Face.KIND)

    @staticmethod
    def ace() -> Face:
        return Face(Face.ACE)


@final
class Card(TaggedUnion):
    FACE_CARD = Tag[Tuple[Suit, Face]]()
    VALUE_CARD = Tag[Tuple[Suit, int]]()
    JOKER = Tag[None]()

    @classmethod
    def face_card(cls, suit: Suit, face: Face) -> Card:
        return Card(Card.FACE_CARD, suit=suit, face=face)

    @staticmethod
    def value_card(suit: Suit, value: int) -> Card:
        return Card(Card.VALUE_CARD, suit=suit, value=value)

    @staticmethod
    def Joker() -> Card:
        return Card(Card.JOKER)


jack_of_hearts = Card.face_card(Suit.hearts(), Face.jack())
three_of_clubs = Card.value_card(Suit.clubs(), 3)
joker = Card.Joker()


def calculate_value(card: Card) -> int:
    with match(card) as case:
        if case(Card.JOKER):
            return 0
        if case(Card.FACE_CARD(suit=Suit.SPADES, face=Face.QUEEN)):
            return 40
        if case(Card.FACE_CARD(face=Face.ACE)):
            return 15
        if case(Card.FACE_CARD()):
            return 10
        if case(Card.VALUE_CARD(value=10)):
            return 10
        if case._:
            return 5

    assert False


def test_union_cards():
    rummy_score = calculate_value(jack_of_hearts)
    assert rummy_score == 10

    rummy_score = calculate_value(three_of_clubs)
    assert rummy_score == 5

    rummy_score = calculate_value(joker)
    assert rummy_score == 0


class EmailAddress(SingleCaseUnion[str]):
    ...


def test_single_case_union_create():
    addr = "foo@bar.com"
    email = EmailAddress(addr)

    assert email.VALUE.tag == 1000
    assert email.value == addr


def test_single_case_union_match():
    addr = "foo@bar.com"
    email = EmailAddress(addr)

    with match(email) as case:
        for email in case(str):
            assert email == addr

        if case._:
            assert False


def test_single_case_union_match_value():
    addr = "foo@bar.com"
    email = EmailAddress(addr)

    with match(email) as case:
        for email in case(EmailAddress.VALUE(addr)):
            assert email == addr

        if case._:
            assert False


def test_single_case_union_not_match_value():
    addr = "foo@bar.com"
    email = EmailAddress(addr)

    with match(email) as case:
        for email in case(EmailAddress.VALUE("test@test.com")):
            assert email == addr

        if case._:
            assert False
