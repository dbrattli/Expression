# %% [markdown]
"""
# Advanced concept: functions and composition

You do not need lambda calculus to use Expression. This short optional lesson explains
the practical parts that appear in everyday Python: functions are values, functions can
return functions, and small functions compose well.
"""

# %%
from collections.abc import Callable


def add_tax(rate: float) -> Callable[[int], int]:
    def calculate(amount: int) -> int:
        return round(amount * (1 + rate))

    return calculate


add_vat = add_tax(0.25)

assert add_vat(100) == 125

# %% [markdown]
"""
## Prefer clarity over clever shorthand

A `lambda` is useful for a short local function. Give a function a name when it carries
domain meaning, needs a type annotation, or becomes more than one expression.
"""

# %%
from expression import compose


def double(value: int) -> int:
    return value * 2


def format_currency(value: int) -> str:
    return f"${value}"


display_total = compose(double, format_currency)

assert display_total(21) == "$42"

# %% [markdown]
"""
The mathematical terms *alpha conversion*, *beta reduction*, and *eta reduction* are
useful in language theory, but they are not prerequisites for writing readable Python.
"""
