# Data Modelling

With Expression and Python you can model your types using data-classes and tagged-unions.

```{code-cell} python
from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Tuple, TypeVar, final

from expression import Tag, TaggedUnion, match

_T = TypeVar("_T")
```

You define your record types using Python data-classes e.g:

```{code-cell} python
@dataclass
class Rectangle:
    width: float
    length: float


@dataclass
class Circle:
    radius: float
```

You can use tagged unions to create sum-types. Tagged unions are similar to untagged
unions (or just unions) but are safer and allows to be nested in ways that normal
cannot. With tagged unions each of the union cases produces the same type which is why
we use a static create method for to create each of the union cases.

```{code-cell} python
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
```

A more complex type modelling example:

```{code-cell} python
from __future__ import annotations
from typing import Tuple, final

from expression import DiscriminatedUnion, match
from expression.core.union import Tag


@final
class Suit(DiscriminatedUnion):
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
class Face(DiscriminatedUnion):
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
class Card(DiscriminatedUnion):
    FACE_CARD = Tag[Tuple[Suit, Face]]()
    VALUE_CARD = Tag[Tuple[Suit, int]]()
    JOKER = Tag[None]()

    @staticmethod
    def face_card(suit: Suit, face: Face) -> Card:
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
```

We can now use our types with pattern matching to create our domain logic:

```{code-cell} python
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


rummy_score = calculate_value(jack_of_hearts)
print("Score: ", rummy_score)

rummy_score = calculate_value(three_of_clubs)
print("Score: ", rummy_score)

rummy_score = calculate_value(joker)
print("Score: ", rummy_score)
```