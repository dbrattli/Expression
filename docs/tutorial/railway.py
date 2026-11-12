# %% [markdown]
"""
# Tutorial: compose expected failures

`Result[T, E]` models a successful value as `Ok(value)` or an expected failure as
`Error(error)`. Each `bind` step runs only after success, so error propagation does not
need nested `if` statements or broad exception handling.
"""

# %%
from expression import Error, Ok, Result


def parse_quantity(raw_value: str) -> Result[int, str]:
    if not raw_value.isdigit():
        return Error("Quantity must be a whole number.")
    return Ok(int(raw_value))


def require_available(quantity: int) -> Result[int, str]:
    if quantity > 10:
        return Error("Only 10 items are available.")
    return Ok(quantity)


assert parse_quantity("3").bind(require_available) == Ok(3)
assert parse_quantity("many").bind(require_available) == Error("Quantity must be a whole number.")
assert parse_quantity("12").bind(require_available) == Error("Only 10 items are available.")

# %% [markdown]
"""
## Recover at the boundary

Keep a `Result` through the workflow. Turn it into a display message, HTTP response, or
other ordinary value only at the boundary that can make a sensible decision.
"""

# %%
message = parse_quantity("many").bind(require_available).default_with(lambda error: f"Cannot order: {error}")

assert message == "Cannot order: Quantity must be a whole number."

# %% [markdown]
"""
The term “railway-oriented programming” is sometimes used for this pattern. The useful
idea is simpler: successful values continue, and expected errors keep their reason.
"""
