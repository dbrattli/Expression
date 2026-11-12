(reference_pipe)=

# Pipe

```{eval-rst}
.. automodule:: expression.core.pipe
    :members:
```

## Asynchronous pipelines

Use `apipe` to mix synchronous functions and coroutine-returning functions:

```python
from expression import apipe

async def increment(value: int) -> int:
    return value + 1

async def example() -> str:
    return await apipe(2, increment, lambda value: value * 3, str)
```

`apipe` starts when awaited and executes stages sequentially. It awaits a native
coroutine supplied as the initial value or returned by a stage once. Exceptions
and cancellation propagate, and later stages do not run.

Other values pass through unchanged, including `Option` and `Result`, even though
these types implement `__await__`. Tasks, futures, and custom awaitables also pass
through unchanged: use an `async def` wrapper that explicitly awaits them when
you want their resolved values. The existing `pipe` never inserts awaits.

For asynchronous Result mapping, use `expression.extra.async_result.bind`:

```python
from expression import Ok, Result, apipe
from expression.extra import async_result

async def increment(value: int) -> Result[int, str]:
    return Ok(value + 1)

async def example() -> Result[str, str]:
    return await apipe(Ok(2), async_result.bind(increment), lambda value: value.map(str))
```

`bind` skips the mapper on `Error`; plain `apipe` itself does not short-circuit
Result values.

```{eval-rst}
.. automodule:: expression.core.apipe
    :members:
```
