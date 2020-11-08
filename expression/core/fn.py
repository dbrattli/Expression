import functools
from typing import Any, Awaitable, Callable, TypeVar

from .result import Error, Ok, Result

TResult = TypeVar("TResult")


class TailCall(Ok[TResult, Exception]):
    """Returns a tail call."""

    def __init__(self, *args: Any, **kw: Any):
        self.args = args
        self.kw = kw


def recursive(fn: Callable[..., Result[TResult, Exception]]) -> Callable[..., TResult]:
    """Tail call bouncing decorator."""

    def _trampoline(bouncer: Result[TResult, Exception]) -> TResult:
        while isinstance(bouncer, TailCall):
            try:
                bouncer = fn(*bouncer.args, **bouncer.kw)
            except Exception as ex:
                bouncer = Error(ex)

        for value in bouncer:
            return value

    @functools.wraps(fn)
    def wrapper(*args: Any, **kw: Any) -> TResult:
        return _trampoline(fn(*args, **kw))

    return wrapper


def recursive_async(fn: Callable[..., Awaitable[TResult]]) -> Callable[..., Awaitable[TResult]]:
    """Thunk bouncing async decorator."""

    async def _trampoline(bouncer: Result[TResult, Exception]) -> TResult:
        while isinstance(bouncer, TailCall):
            bouncer = await fn(*bouncer.args, **bouncer.kw)

        for value in bouncer:
            return value

    @functools.wraps(fn)
    async def _(*args: Any) -> TResult:
        result = await fn(*args)
        return await _trampoline(result)

    return _


__all__ = ["TailCall", "recursive", "recursive_async"]
