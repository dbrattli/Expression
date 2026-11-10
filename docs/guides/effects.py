# %% [markdown]
"""
# Use effect builders for short-circuiting workflows

Most workflows are clearest with `map`, `bind`, and `pipe`. An effect builder is useful
when several `Option` or `Result` steps need local variables and early termination.
"""

# %%
from expression import Error, Nothing, Ok, Option, Result, Some, effect


def parse_count(value: str) -> Result[int, str]:
    return Ok(int(value)) if value.isdigit() else Error("Count must be numeric.")


@effect.result
def total(scope: effect.ResultScope[str], left: str, right: str) -> int:
    first = scope.bind(parse_count(left))
    second = scope.bind(parse_count(right))
    return first + second


assert total("2", "3") == Ok(5)
assert total("2", "three") == Error("Count must be numeric.")

# %% [markdown]
"""
## Preserve types in Option workflows

Each scope binding has its own payload type. The function return annotation describes
the final successful value. Pyright checks each binding independently:
"""


# %%
@effect.option
def maybe_add(scope: effect.OptionScope, left: Option[int], right: Option[int]) -> int:
    return scope.bind(left) + scope.bind(right)


assert maybe_add(Some(2), Some(3)) == Some(5)
assert maybe_add(Some(2), Nothing) == Nothing

# %% [markdown]
"""
When a bound `Result` is an `Error`, the remaining statements are skipped. The
library also provides `option`, `seq`, `async_option`, `async_result`, and `async_try`
builders. Use the [effects overview](../reference/effects) to choose one.
"""
