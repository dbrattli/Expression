# %% [markdown]
"""
# Tutorial: write a linear fallible workflow

Use `map` and `bind` for short workflows. When a workflow has several fallible steps and
local variables improve readability, an effect builder writes the same short-circuiting
behaviour in a direct style.
"""

# %%
from collections.abc import Generator

from expression import Error, Ok, Result, effect


def parse_price(raw_price: str) -> Result[int, str]:
    return Ok(int(raw_price)) if raw_price.isdigit() else Error("Price must be numeric.")


def apply_discount(price: int, percentage: int) -> Result[int, str]:
    if not 0 <= percentage <= 100:
        return Error("Discount must be between 0 and 100.")
    return Ok(price * (100 - percentage) // 100)


@effect.result[int, str]()
def discounted_price(raw_price: str, percentage: int) -> Generator[int, int, int]:
    price = yield from parse_price(raw_price)
    return (yield from apply_discount(price, percentage))


assert discounted_price("120", 25) == Ok(90)
assert discounted_price("free", 25) == Error("Price must be numeric.")
assert discounted_price("120", 200) == Error("Discount must be between 0 and 100.")

# %% [markdown]
"""
The `option`, `seq`, `async_option`, `async_result`, and `async_try` builders follow the
same idea for their respective return types. Use a builder only when it makes a workflow
clearer than a chain of `bind` calls.
"""
