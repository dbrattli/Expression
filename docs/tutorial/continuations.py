# %% [markdown]
"""
# Advanced concept: callbacks and async code

A callback is a function supplied to receive a future value. It is useful in some APIs,
but a callback chain can hide the order of work and make error handling difficult.
"""

# %%
from collections.abc import Callable


def load_count(callback: Callable[[int], None]) -> None:
    callback(42)


received: list[int] = []
load_count(received.append)

assert received == [42]

# %% [markdown]
"""
## Prefer `async` and `await` for asynchronous workflows

`async` functions return their result normally from the reader's perspective. The event
loop manages the continuation instead of requiring each caller to provide one.
"""

# %%
import asyncio


async def load_count_async() -> int:
    await asyncio.sleep(0)
    return 42


async def check_load_count() -> None:
    assert await load_count_async() == 42


await check_load_count()  # noqa: F704 - valid top-level await in a Jupyter cell

# %% [markdown]
"""
Expression's asynchronous effect builders combine this direct style with explicit
`Option` or `Result` short-circuiting when an asynchronous workflow can be absent or
fail in an expected way.
"""
