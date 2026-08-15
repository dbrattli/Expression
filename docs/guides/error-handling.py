# %% [markdown]
"""
# Model expected failures with `Result`

Use `Result[T, E]` when an operation may fail in an expected way and its caller needs
the error. `Ok(value)` holds a successful result; `Error(error)` holds the reason.
"""
# %%
from expression import Error, Ok, Result

def parse_age(value: str) -> Result[int, str]:
    if not value.isdigit():
        return Error("Age must be a whole number.")

    age = int(value)
    if age < 0:
        return Error("Age cannot be negative.")
    return Ok(age)


# %% [markdown]
"""
## Continue only after success

Use `map` for a safe transformation and `bind` when the next operation returns another
`Result`. Errors pass through unchanged, so every step does not need its own `if`.
"""
# %%
def adult(age: int) -> Result[bool, str]:
    return Ok(age >= 18)

assert parse_age("42").bind(adult) == Ok(True)
assert parse_age("unknown").bind(adult) == Error("Age must be a whole number.")

# %% [markdown]
"""
Use `map_error` to turn low-level errors into a domain message, and `default_with` only
at a boundary where a fallback is appropriate:
"""
# %%
message = parse_age("unknown").default_with(lambda error: f"Input error: {error}")
assert message == "Input error: Age must be a whole number."

# %% [markdown]
"""
`Result` is not a replacement for unexpected exceptions such as programming errors.
Catch and convert only exceptions that are part of your application's expected contract.
See [Result](reference_result) and [Try](reference_try) for the complete API.
"""
