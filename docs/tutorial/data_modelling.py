# %% [markdown]
"""
# Tutorial: model domain alternatives

Use a dataclass for one record shape. Use a tagged union when a value is exactly one of
several alternatives with different data or behaviour.
"""

# %%
from dataclasses import dataclass
from typing import Literal, TypeAlias, assert_never, final

from expression import TaggedUnion, case, tag


@dataclass(frozen=True)
class Address:
    city: str


@final
@case
class Pickup:
    store: str
    tag: Literal["pickup"] = tag("pickup")


@final
@case
class Shipping:
    address: Address
    tag: Literal["shipping"] = tag("shipping")


Delivery: TypeAlias = TaggedUnion[Pickup | Shipping]


# %% [markdown]
"""
## Match each case where behaviour differs

Python structural pattern matching makes handling the alternatives direct and explicit.
"""


# %%
def delivery_label(delivery: Delivery) -> str:
    match delivery:
        case Pickup(store):
            return f"Collect from {store}"
        case Shipping(Address(city)):
            return f"Ship to {city}"
        case _:
            assert_never(delivery)


assert delivery_label(Pickup("Central")) == "Collect from Central"
assert delivery_label(Shipping(Address("Oslo"))) == "Ship to Oslo"

# %% [markdown]
"""
The case classes are frozen dataclasses. Each constructor accepts only that case's
payload, and the type alias describes all valid alternatives. `@final` makes static
checking reject subclasses; `@case` enforces the same restriction at runtime.

The literal tag supports tagged serialization and cannot be passed to the constructor.
Use ordinary field defaults or `dataclasses.field` for payload defaults. See the
[tagged-union reference](../reference/union) for serialization and the full API.
"""
