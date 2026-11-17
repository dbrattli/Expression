(reference_option)=

# Option

```{eval-rst}
.. automodule:: expression.core.option
    :members:
    :imported-members:
```

## Async mapping and binding

Use `amap` when a callback returns an awaitable value. Use `abind` when it returns
an awaitable containing another `Option`. Both have fluent methods and
pipe-friendly module functions.

```python
from expression import NOTHING, Option, Some, apipe, option


async def describe(value: int) -> str:
    return f"item-{value}"


async def lookup(value: int) -> Option[int]:
    return Some(value * 2) if value > 0 else NOTHING


async def example() -> None:
    assert await Some(2).amap(describe) == Some("item-2")
    assert await Some(2).abind(lookup) == Some(4)
    assert await apipe(Some(2), option.abind(lookup), option.amap(describe)) == Some("item-4")
```

Awaiting either operation returns an ordinary `Option`. The callback is invoked
only when the operation is awaited, and only for `Some`. `Nothing` is preserved
without invoking the callback. `amap` wraps the callback's resolved value even
when it is `None` or another container; `abind` returns the callback's container
directly. Neither operation recursively awaits the returned payload or container.

Callbacks can return any `Awaitable`, including futures and tasks. Exceptions and
cancellation propagate; they are not converted into `Nothing`. No background tasks
are started by these operations.

For a single functional step, `await pipe(value, option.amap(callback))` works.
Use `apipe` for multiple async stages so each stage's coroutine is awaited before
its result reaches the next stage. An `amap`/`abind` stage skips its callback on
`Nothing`; `apipe` itself still calls later stages with that container.
