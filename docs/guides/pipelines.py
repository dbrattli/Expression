# %% [markdown]
"""
# Compose data transformations

Use a pipeline when a value passes through several independent transformations. Each
step receives the previous result, so the order reads from top to bottom.
"""
# %%
from collections.abc import Mapping

from expression import pipe
from expression.collections import seq

def is_active(user: Mapping[str, str | bool]) -> bool:
    return user["active"] is True

def name(user: Mapping[str, str | bool]) -> str:
    return str(user["name"])

users = [
    {"name": "Ada", "active": True},
    {"name": "Grace", "active": False},
    {"name": "Linus", "active": True},
]

names = pipe(
    users,
    seq.filter(is_active),
    seq.map(name),
    list,
)

assert names == ["Ada", "Linus"]

# %% [markdown]
"""
`pipe(value, step_one, step_two)` is equivalent to `step_two(step_one(value))`. Most
functional collection helpers accept their source last, which makes them directly
usable as pipeline steps.

## Reuse a workflow

Use `compose` to build a new function from reusable transformations:
"""
# %%
from expression import compose
from expression.collections import seq

active_names = compose(
    seq.filter(is_active),
    seq.map(name),
    list,
)

assert active_names([{"name": "Ada", "active": True}]) == ["Ada"]

# %% [markdown]
"""
Use a normal `def` instead when a workflow needs branching, local names, or domain
specific validation. A pipeline should clarify the work, not conceal it.

See the [Pipe API](reference_pipe) and [Seq API](reference_seq) for available helpers.
"""
