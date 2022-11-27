from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Tuple, TypeVar, final

from pydantic import parse_obj_as

from expression import SingleCaseUnion, Tag, TaggedUnion, tag

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

    match shape.tag:
        case Shape.CIRCLE:
            assert False
        case Shape.RECTANGLE:
            assert True
        case _:
            assert False


def test_union_match_type():
    shape = Shape.rectangle(2.3, 3.3)

    match shape:
        case Shape(value=Rectangle(length=length)):
            assert length == 3.3
        case _:
            assert False


def test_union_match_value():
    shape = Shape.rectangle(2.3, 3.3)

    match shape:
        case Shape(value=Rectangle(width=2.3)):
            assert shape.value.width == 2.3
        case _:
            assert False


def test_union_no_match_value():
    shape = Shape.rectangle(2.3, 3.3)

    match shape:
        case Shape(Rectangle(width=12.3)):
            assert False
        case _:
            assert True


@final
class Weather(TaggedUnion):
    SUNNY = tag()
    RAINY = tag()

    @staticmethod
    def sunny() -> Weather:
        return Weather(Weather.SUNNY)

    @staticmethod
    def rainy() -> Weather:
        return Weather(Weather.RAINY)


def test_union_wether_match():
    rainy = Weather.sunny()

    match rainy:
        case Weather(Weather.RAINY):
            assert False
        case Weather(Weather.SUNNY):
            assert True
        case _:
            assert False


class Maybe(TaggedUnion, Generic[_T]):
    NOTHING = tag()
    JUST = Tag[_T]()

    @staticmethod
    def just(value: _T) -> Maybe[_T]:
        return Maybe[_T](Maybe.JUST, value)

    @staticmethod
    def nothing() -> Maybe[None]:
        return Maybe[None](Maybe.NOTHING)


def test_union_maybe_match():
    maybe = Maybe.just(10)
    value: int

    match maybe:
        case Maybe(Maybe.NOTHING):
            assert False
        case Maybe(value=value):
            assert value == 10

        case _:
            assert False


@final
class Suit(TaggedUnion):
    HEARTS = tag(1)
    SPADES = tag(2)
    CLUBS = tag(3)
    DIAMONDS = tag(4)

    @staticmethod
    def hearts() -> Suit:
        return Suit(Suit.HEARTS)

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
    JACK = tag()
    QUEEN = tag()
    KIND = tag()
    ACE = tag()

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
    JOKER = tag()

    @staticmethod
    def face_card(suit: Suit, face: Face) -> Card:
        return Card(Card.FACE_CARD, (suit, face))

    @staticmethod
    def value_card(suit: Suit, value: int) -> Card:
        return Card(Card.VALUE_CARD, (suit, value))

    @staticmethod
    def Joker() -> Card:
        return Card(Card.JOKER)


jack_of_hearts = Card.face_card(Suit.hearts(), Face.jack())
three_of_clubs = Card.value_card(Suit.clubs(), 3)
joker = Card.Joker()


def calculate_value(card: Card) -> int:
    match card:
        case Card(Card.JOKER):
            return 0
        case Card(value=Face(suit=Suit.SPADES, face=Face.QUEEN)):
            return 40
        case Card(value=Face(face=Face.ACE)):
            return 15
        case Card(Card.FACE_CARD):
            return 10
        case Card(tag=Card.FACE_CARD, value=(_, 10)):
            return 10
        case _:
            return 5


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

    match email:
        case EmailAddress():
            assert True
        case _:
            assert False


def test_single_case_union_match_value():
    addr = "foo@bar.com"
    email = EmailAddress(addr)

    match email:
        case EmailAddress(value=value):
            assert value == addr
        case _:
            assert False


def test_single_case_union_not_match_value():
    addr = "foo@bar.com"
    email = EmailAddress(addr)

    match email:
        case EmailAddress(value="test@test.com"):
            assert False
        case _:
            assert True


def test_union_to_dict_works():
    maybe = Maybe.just(10)
    obj = maybe.dict()
    assert obj == dict(tag="JUST", value=10)


def test_union_from_dict_works():
    obj = dict(tag="JUST", value=10)
    maybe = parse_obj_as(Maybe[int], obj)

    assert maybe
    assert maybe.value == 10


def test_nested_union_to_dict_works():
    maybe = Maybe.just(Maybe.just(10))
    obj = maybe.dict()
    assert obj == dict(tag="JUST", value=dict(tag="JUST", value=10))


def test_nested_union_from_dict_works():
    obj = dict(tag="JUST", value=dict(tag="JUST", value=10))

    maybe = parse_obj_as(Maybe[Maybe[int]], obj)
    assert maybe
    assert maybe.value
    assert maybe.value.value == 10
