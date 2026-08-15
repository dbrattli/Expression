# %% [markdown]
"""
# Handle optional values with `Option`

Use `Option[T]` when a function may not have a meaningful `T` to return. `Some(value)`
contains a value; `Nothing` represents its absence. This makes absence visible in the
return type instead of relying on an unchecked `None`.
"""
# %%
from expression import Nothing, Option, Some

def find_port(environment: dict[str, str]) -> Option[int]:
    value = environment.get("PORT")
    return Some(int(value)) if value is not None and value.isdigit() else Nothing


# %% [markdown]
"""
## Transform without repeated checks

Use `map` when a transformation always returns a plain value. It runs only for `Some`;
`Nothing` stays `Nothing`.
"""
# %%
port = Some(8080).map(lambda value: f"http://localhost:{value}")
missing = Nothing.map(lambda value: value + 1)

assert port == Some("http://localhost:8080")
assert missing is Nothing


# %% [markdown]
"""
Use `bind` when the next operation can also be absent. It avoids nesting an
`Option` inside another `Option`.
"""
# %%
def positive(value: int) -> Option[int]:
    return Some(value) if value > 0 else Nothing

assert Some(3).bind(positive) == Some(3)
assert Some(-3).bind(positive) is Nothing

# %% [markdown]
"""
At the boundary where a plain Python value is required, choose a deliberate default:
"""
# %%
port = find_port({"PORT": "invalid"}).default_value(8000)
assert port == 8000

# %% [markdown]
"""
Do not read a wrapped value directly. Use `map`, `bind`, structural pattern matching,
or a boundary method such as `default_value`. For the full API, see [Option](reference_option).
"""
