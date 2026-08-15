# %% [markdown]
"""
# Tutorial: model domain alternatives

Use a dataclass for one record shape. Use a tagged union when a value is exactly one of
several alternatives with different data or behaviour.
"""

# %%
from dataclasses import dataclass
from typing import Literal

from expression import case, tag, tagged_union


@dataclass(frozen=True)
class Address:
    city: str


@tagged_union
class Delivery:
    tag: Literal["pickup", "shipping"] = tag()
    pickup: str = case()
    shipping: Address = case()

    @staticmethod
    def Pickup(store: str) -> "Delivery":
        return Delivery(pickup=store)

    @staticmethod
    def Shipping(address: Address) -> "Delivery":
        return Delivery(shipping=address)


# %% [markdown]
"""
## Match each case where behaviour differs

Python structural pattern matching makes handling the alternatives direct and explicit.
"""

# %%
def delivery_label(delivery: Delivery) -> str:
    match delivery:
        case Delivery(tag="pickup", pickup=store):
            return f"Collect from {store}"
        case Delivery(tag="shipping", shipping=Address(city=city)):
            return f"Ship to {city}"


assert delivery_label(Delivery.Pickup("Central")) == "Collect from Central"
assert delivery_label(Delivery.Shipping(Address("Oslo"))) == "Ship to Oslo"

# %% [markdown]
"""
Keep constructors descriptive and keep cases small. See the [tagged-union reference](../reference/union)
for serialization and the full decorator API.
"""
