# %% [markdown]
"""
# Tutorial: make absence explicit

This tutorial builds a configuration lookup that can legitimately be missing. Use
`Option[T]` when absence is enough information; use `Result[T, E]` when a caller needs an
error explanation.
"""

# %%
from expression import Nothing, Option, Some


def read_timeout(settings: dict[str, str]) -> Option[int]:
    raw_timeout = settings.get("TIMEOUT_SECONDS")
    if raw_timeout is None or not raw_timeout.isdigit():
        return Nothing
    return Some(int(raw_timeout))


assert read_timeout({"TIMEOUT_SECONDS": "30"}) == Some(30)
assert read_timeout({"TIMEOUT_SECONDS": "fast"}) is Nothing

# %% [markdown]
"""
## Transform and validate without repeated `None` checks

Use `map` for a transformation that always produces a plain value. Use `bind` for the
next step when it can also be absent.
"""

# %%
def positive(value: int) -> Option[int]:
    return Some(value) if value > 0 else Nothing


timeout = read_timeout({"TIMEOUT_SECONDS": "30"}).bind(positive).map(lambda value: value * 1_000)
missing_timeout = read_timeout({}).bind(positive)

assert timeout == Some(30_000)
assert missing_timeout is Nothing

# %% [markdown]
"""
At an application boundary, choose an intentional fallback or convert absence to a
`Result` with a useful error. Do not unwrap an `Option` just to recreate unchecked
`None` handling.
"""
