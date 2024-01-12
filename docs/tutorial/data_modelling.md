---
jupytext:
  cell_metadata_filter: -all
  formats: md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.11.5
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---
(tutorial_data_modelling)=

# Data Modelling

With Expression and Python you can model your types using data-classes and
tagged-unions. Let's start by importing some types we need before we begin.

```{code-cell} python
from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Tuple, TypeVar, final

from expression import case, tag, tagged_union

_T = TypeVar("_T")
```

You define your record types using normal Python data-classes e.g:

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
@tagged_union
class Shape:
    tag: Literal["rectangle", "circle"] = tag()

    rectangle: Rectangle = case()
    circle: Circle = case()

    @staticmethod
    def Rectangle(width: float, length: float) -> Shape:
        return Shape(rectangle=Rectangle(width, length))

    @staticmethod
    def Circle(radius: float) -> Shape:
        return Shape(circle=Circle(radius))
```

A more complex type modelling example:

```{code-cell} python
from __future__ import annotations
from typing import Tuple, final

from expression import TaggedUnion, match
from expression.core.union import Tag


@tagged_union
class Suit:
    tag: Literal["spades", "hearts", "clubs", "diamonds"] = tag()

    spades: Literal[True] = case()
    hearts: Literal[True] = case()
    clubs: Literal[True] = case()
    diamonds: Literal[True] = case()

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

    jack: Literal[True] = case()
    queen: Literal[True] = case()
    king: Literal[True] = case()
    ace: Literal[True] = case()

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
    tag: Literal["value", "face", "joker"] = tag()

    face: tuple[Suit, Face] = case()
    value: tuple[Suit, int] = case()
    joker: Literal[True] = case()

    @staticmethod
    def Face(suit: Suit, face: Face) -> Card:
        return Card(face=(suit, face))

    @staticmethod
    def Value(suit: Suit, value: int) -> Card:
        if value < 1 or value > 10:
            raise ValueError("Value must be between 1 and 10")
        return Card(value=(suit, value))

    @staticmethod
    def Joker() -> Card:
        return Card(joker=True)


jack_of_hearts = Card.Face(suit=Suit.Hearts(), face=Face.Jack())
three_of_clubs = Card.Value(suit=Suit.Clubs(), value=3)
joker = Card.Joker()
```

We can now use our types with pattern matching to create our domain logic:

```{code-cell} python
def calculate_value(card: Card) -> int:
    match card:
        case Card(tag="face", face=(Suit(spades=True), Face(queen=True))):
            return 40
        case Card(tag="face", face=(_suit, Face(ace=True))):
            return 15
        case Card(tag="face", face=(_suit, _face)):
            return 10
        case Card(tag="value", value=(_suit, value)):
            return value
        case Card(tag="joker", joker=True):
            return 0
        case _:
            raise AssertionError("Should not match")


rummy_score = calculate_value(jack_of_hearts)
print("Score: ", rummy_score)

rummy_score = calculate_value(three_of_clubs)
print("Score: ", rummy_score)

rummy_score = calculate_value(joker)
print("Score: ", rummy_score)
```

## Single case tagged unions

You can also use tagged unions to create single case tagged unions. This is useful
when you want to create a type that is different from the underlying type. For example
you may want to create a type that is a string but is a different type to a normal
string:

```{code-cell} python
@tagged_union(frozen=True, repr=False)
class SecurePassword:
    password: str = case()

    # Override __str__ and __repr__ to make sure we don't leak the password in logs
    def __str__(self) -> str:
        return "********"

    def __repr__(self) -> str:
        return "SecurePassword(password='********')"

password = SecurePassword(password="secret")
match password:
    case SecurePassword(password=p):
        assert p == "secret"

```

This will make sure that the password is not leaked in logs or when printed to the
console, and that we don't assign a password to a normal string anywhere in our code.

