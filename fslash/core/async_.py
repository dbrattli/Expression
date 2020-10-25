import asyncio
from typing import Any, Awaitable, TypeVar

from fslash.system import CancellationToken

TSource = TypeVar("TSource")


def start(computation: Awaitable[Any], token: CancellationToken) -> None:
    task = asyncio.create_task(computation)

    def cb():
        task.cancel()

    token.register(cb)
    return None


def run_synchronous(computation: Awaitable[TSource]) -> TSource:
    return asyncio.run(computation)


async def singleton(value: TSource) -> TSource:
    """Async function that returns a single value."""
    return value


__all__ = ["singleton"]
