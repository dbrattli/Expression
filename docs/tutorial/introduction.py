# %% [markdown]
"""
# Tutorial: build a small data workflow

This tutorial applies Expression to a familiar task: turn a list of raw records into a
small report. It assumes you have read [Getting started](../guides/getting-started).

The important habit is to keep each transformation small, named, and independently
testable. `pipe` then makes the order of those transformations obvious.
"""

# %%
from expression import pipe
from expression.collections import seq

orders = [
    {"customer": "Ada", "amount": 12, "paid": True},
    {"customer": "Grace", "amount": 8, "paid": False},
    {"customer": "Ada", "amount": 5, "paid": True},
]


def is_paid(order: dict[str, object]) -> bool:
    return order["paid"] is True


def amount(order: dict[str, object]) -> int:
    return int(order["amount"])


revenue = pipe(
    orders,
    seq.filter(is_paid),
    seq.map(amount),
    seq.sum,
)

assert revenue == 17

# %% [markdown]
"""
## Keep domain decisions in normal functions

Expression does not replace ordinary Python. A function is often the clearest place for
branching and a domain rule; a pipeline connects those functions.
"""

# %%
from expression import compose


paid_amounts = compose(
    seq.filter(is_paid),
    seq.map(amount),
    list,
)

assert paid_amounts(orders) == [12, 5]

# %% [markdown]
"""
Next, learn how [collections](containers) keep transformations lazy or immutable, and
how [Option](optional_values) and [Result](railway) make incomplete workflows explicit.
"""
