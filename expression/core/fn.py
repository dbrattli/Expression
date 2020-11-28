import functools
from typing import Any, Awaitable, Callable, TypeVar, Union

TResult = TypeVar("TResult")


class TailCall:
    """Returns a tail call.

    If a `tailrec` decorated function return a `TailCall` then the
    function will be called again with the new arguments provided.
    """

    def __init__(self, *args: Any, **kw: Any):
        self.args = args
        self.kw = kw


TailCallResult = Union[TResult, TailCall]


def tailrec(fn: Callable[..., TailCallResult[TResult]]) -> Callable[..., TResult]:
    """Tail call recursive function decorator.

    Can be used to create tail call recursive functions that will not
    stack overflow. To recurse the function needs to return an instance
    of `TailCall` with the next arguments to be used for the next call.
    """

    def trampoline(bouncer: TailCallResult[TResult]) -> TResult:
        while isinstance(bouncer, TailCall):
            args, kw = bouncer.args, bouncer.kw
            bouncer = fn(*args, **kw)

        return bouncer

    @functools.wraps(fn)
    def wrapper(*args: Any, **kw: Any) -> TResult:
        return trampoline(fn(*args, **kw))

    return wrapper


def tailrec_async(fn: Callable[..., Awaitable[TailCallResult[TResult]]]) -> Callable[..., Awaitable[TResult]]:
    """Tail call recursive async function decorator."""

    async def trampoline(bouncer: TailCallResult[TResult]) -> TResult:
        while isinstance(bouncer, TailCall):
            args, kw = bouncer.args, bouncer.kw
            bouncer = await fn(*args, **kw)

        return bouncer

    @functools.wraps(fn)
    async def wrapper(*args: Any) -> TResult:
        result = await fn(*args)
        return await trampoline(result)

    return wrapper


__all__ = ["TailCall", "TailCallResult", "tailrec", "tailrec_async"]
