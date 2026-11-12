from __future__ import annotations

import functools
from collections.abc import Awaitable, Callable
from typing import cast


class TailCall[**P]:
    """Returns a tail call.

    If a `tailrec` decorated function return a `TailCall` then the
    function will be called again with the new arguments provided.
    """

    def __init__(self, *args: P.args, **kw: P.kwargs):
        self.args = args
        self.kw = kw


type TailCallResult[TResult, **P] = TResult | TailCall[P]


def tailrec[**P, TResult](fn: Callable[P, TailCallResult[TResult, P]]) -> Callable[P, TResult]:
    """Tail call recursive function decorator.

    Can be used to create tail call recursive functions that will not
    stack overflow. To recurse the function needs to return an instance
    of `TailCall` with the next arguments to be used for the next call.
    """

    def trampoline(bouncer: TailCallResult[TResult, P]) -> TResult:
        while isinstance(bouncer, TailCall):
            bouncer = cast(TailCall[P], bouncer)

            args, kw = bouncer.args, bouncer.kw
            bouncer = fn(*args, **kw)

        return bouncer

    @functools.wraps(fn)
    def wrapper(*args: P.args, **kw: P.kwargs) -> TResult:
        return trampoline(fn(*args, **kw))

    return wrapper


def tailrec_async[**P, TResult](
    fn: Callable[P, Awaitable[TailCallResult[TResult, P]]],
) -> Callable[P, Awaitable[TResult]]:
    """Tail call recursive async function decorator."""

    async def trampoline(bouncer: TailCallResult[TResult, P]) -> TResult:
        while isinstance(bouncer, TailCall):
            bouncer = cast(TailCall[P], bouncer)
            args, kw = bouncer.args, bouncer.kw
            bouncer = await fn(*args, **kw)

        return bouncer

    @functools.wraps(fn)
    async def wrapper(*args: P.args, **kw: P.kwargs) -> TResult:
        result = await fn(*args, **kw)
        return await trampoline(result)

    return wrapper


__all__ = ["TailCall", "TailCallResult", "tailrec", "tailrec_async"]
