# %% [markdown]
"""
# Use effect builders for short-circuiting workflows

Most workflows are clearest with `map`, `bind`, and `pipe`. An effect builder is useful
when several `Option` or `Result` steps need local variables and early termination.
"""
# %%
from collections.abc import Generator

from expression import Error, Nothing, Ok, Option, Result, Some, effect

def parse_count(value: str) -> Result[int, str]:
    return Ok(int(value)) if value.isdigit() else Error("Count must be numeric.")

@effect.result[int, str]()
def total(left: str, right: str) -> Generator[int, int, int]:
    first = yield from parse_count(left)
    second = yield from parse_count(right)
    return first + second

assert total("2", "3") == Ok(5)
assert total("2", "three") == Error("Count must be numeric.")

# %% [markdown]
"""
## Preserve types in Option workflows

Python's generator type models every `yield` and sent value with one type parameter.
For an Option workflow with differently typed intermediate values, use a generator
comprehension. Pyright can infer each binding independently:
"""
# %%
@effect.option[int]()
def maybe_add(left: Option[int], right: Option[int]) -> Generator[int, int, int]:
    yield from (left_value + right_value for left_value in left for right_value in right)

assert maybe_add(Some(2), Some(3)) == Some(5)
assert maybe_add(Some(2), Nothing) == Nothing

# %% [markdown]
"""
When any yielded `Result` is an `Error`, the remaining statements are skipped. The
library also provides `option`, `seq`, `async_option`, `async_result`, and `async_try`
builders. Use the [effects overview](../reference/effects) to choose one.
"""
