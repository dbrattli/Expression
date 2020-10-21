from typing import Any


async def singleton(value: Any) -> Any:
    """Async function that returns a single value."""
    return value


__all__ = ["singleton"]
