# %% [markdown]
"""
# Which type should I use?

Start with ordinary Python values. Introduce an Expression type when it communicates an
important part of a function's contract.

| Situation | Use | Why |
| --- | --- | --- |
| Every input produces a value | A normal return type | The simplest API is best. |
| A value may legitimately be absent | `Option[T]` | Callers must handle `Some` or `Nothing`. |
| An operation can fail and callers need the reason | `Result[T, E]` | The success and error values are both explicit. |
| An existing API raises exceptions | `Try[T]` or a boundary adapter | Convert only expected exceptions at the boundary. |
| You are transforming many values | `Seq[T]`, `Block[T]`, or `Map[K, V]` | Get composable collection operations and immutable choices. |
| A series of `Option` or `Result` steps becomes noisy | An effect builder | Keep short-circuiting workflow code linear. |

## Option or Result?

Use `Option` when absence is sufficient information:
"""
# %%
from expression import Nothing, Option, Some

def find_discount(code: str) -> Option[int]:
    return Some(10) if code == "WELCOME" else Nothing


# %% [markdown]
"""
Use `Result` when the caller needs to know what went wrong:
"""
# %%
from expression import Error, Ok, Result

def parse_quantity(value: str) -> Result[int, str]:
    if value.isdigit():
        return Ok(int(value))
    return Error("Quantity must contain only digits.")

# %% [markdown]
"""
Do not use `Option` to hide an error a caller should see, or `Result` for a normal,
uninteresting absence. See [Optional values](optional-values) and
[Expected failures](error-handling) for complete workflows.
"""
