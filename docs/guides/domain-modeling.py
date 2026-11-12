# %% [markdown]
"""
# Model domain alternatives with tagged unions

Use a tagged union when a value is exactly one of several well-defined cases. It makes
the cases explicit and works naturally with Python structural pattern matching.
"""

# %%
from typing import Literal, TypeAlias, assert_never, final

from expression import TaggedUnion, case, tag


@final
@case
class Card:
    last_four: str
    tag: Literal["card"] = tag()


@final
@case
class Cash:
    tag: Literal["cash"] = tag()


Payment: TypeAlias = TaggedUnion[Card | Cash]


def describe(payment: Payment) -> str:
    match payment:
        case Card(last_four):
            return f"Card ending in {last_four}"
        case Cash():
            return "Cash"
        case _:
            assert_never(payment)


assert describe(Card("1234")) == "Card ending in 1234"
assert describe(Cash()) == "Cash"

# %% [markdown]
"""
Each case is a frozen dataclass with its own fields and constructor. `@case` rejects
subclasses at runtime; `@final` also makes a type checker reject them. The literal tag
is fixed by the declaration, so callers cannot override it. `Cash` has no payload and
needs no placeholder field.

`Payment` is a type alias used in annotations. Construct and match `Card` or `Cash`
directly. The `assert_never` branch makes a missing case a type-checking error when the
alias grows. Use a standard enum when every alternative is just a named constant.
See [Tagged unions](reference_union) for serialization and the full API.
"""


# %% [markdown]
"""
## Single-case domain types

A case can also wrap a primitive value in a distinct domain type, similar to an F#
single-case discriminated union. The class itself serves as the type and constructor;
a separate union alias is unnecessary for ordinary domain use.
"""

# %%
@final
@case
class CustomerId:
    value: int
    tag: Literal["customer_id"] = tag()


def customer_number(customer_id: CustomerId) -> int:
    match customer_id:
        case CustomerId(value):
            return value


assert customer_number(CustomerId(42)) == 42

# %% [markdown]
"""
The annotation keeps `CustomerId` distinct from an ordinary `int` during static
checking. `tag()` derives its fixed value from `Literal` when the class is declared,
normally during module import. Constructing instances does not repeat that inference.
For tagged Pydantic decoding, use `TypeAdapter(TaggedUnion[CustomerId])` at the
serialization boundary.
"""
