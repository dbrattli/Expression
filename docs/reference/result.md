(reference_result)=

# Result

```{eval-rst}
.. automodule:: expression.core.result
    :members:
    :imported-members:
```

## Async mapping and binding

Use `amap` when a callback returns an awaitable value. Use `abind` when it returns
an awaitable containing another `Result`. Both have fluent methods and
pipe-friendly module functions.

```python
from expression import Error, Ok, Result, apipe, result


async def describe(value: int) -> str:
    return f"item-{value}"


async def lookup(value: int) -> Result[int, str]:
    return Ok(value * 2) if value > 0 else Error("not found")


async def example() -> None:
    assert await Ok(2).amap(describe) == Ok("item-2")
    assert await Ok(2).abind(lookup) == Ok(4)
    assert await apipe(Ok(2), result.abind(lookup), result.amap(describe)) == Ok("item-4")
```

Awaiting either operation returns an ordinary `Result`. The callback is invoked
only when the operation is awaited, and only for `Ok`. `Error` is preserved
without invoking the callback. `amap` wraps the callback's resolved value even
when it is `None` or another container; `abind` returns the callback's container
directly. Neither operation recursively awaits the returned payload or container.

Callbacks can return any `Awaitable`, including futures and tasks. Exceptions and
cancellation propagate; they are not converted into `Error`. No background tasks
are started by these operations.

For a single functional step, `await pipe(value, result.amap(callback))` works.
Use `apipe` for multiple async stages so each stage's coroutine is awaited before
its result reaches the next stage. An `amap`/`abind` stage skips its callback on
`Error`; `apipe` itself still calls later stages with that container.
