# %% [markdown]
"""
# Use effect builders for short-circuiting workflows

Most workflows are clearest with `map`, `bind`, and `pipe`. An effect builder is useful
when several `Option` or `Result` steps need local variables and early termination.
"""
# %%
from collections.abc import Generator

from expression import Error, Ok, Result, effect

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
When any yielded `Result` is an `Error`, the remaining statements are skipped. The
library also provides `option`, `seq`, `async_option`, `async_result`, and `async_try`
builders. Use the [effects overview](../reference/effects) to choose one.
"""
