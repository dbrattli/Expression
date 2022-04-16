import functools
from typing import Awaitable, Callable, Generic, TypeVar, Union

from typing_extensions import ParamSpec

_TResult = TypeVar("_TResult")
_P = ParamSpec("_P")


class TailCall(Generic[_P]):
    """Returns a tail call.

    If a `tailrec` decorated function return a `TailCall` then the
    function will be called again with the new arguments provided.
    """

    def __init__(self, *args: _P.args, **kw: _P.kwargs):
        self.args = args
        self.kw = kw


TailCallResult = Union[_TResult, TailCall[_P]]


def tailrec(fn: Callable[_P, TailCallResult[_TResult, _P]]) -> Callable[_P, _TResult]:
    """Tail call recursive function decorator.

    Can be used to create tail call recursive functions that will not
    stack overflow. To recurse the function needs to return an instance
    of `TailCall` with the next arguments to be used for the next call.
    """

    def trampoline(bouncer: TailCallResult[_TResult, _P]) -> _TResult:
        while isinstance(bouncer, TailCall):
            args, kw = bouncer.args, bouncer.kw
            bouncer = fn(*args, **kw)

        return bouncer

    @functools.wraps(fn)
    def wrapper(*args: _P.args, **kw: _P.kwargs) -> _TResult:
        return trampoline(fn(*args, **kw))

    return wrapper


def tailrec_async(
    fn: Callable[_P, Awaitable[TailCallResult[_TResult, _P]]]
) -> Callable[_P, Awaitable[_TResult]]:
    """Tail call recursive async function decorator."""

    async def trampoline(bouncer: TailCallResult[_TResult, _P]) -> _TResult:
        while isinstance(bouncer, TailCall):
            args, kw = bouncer.args, bouncer.kw
            bouncer = await fn(*args, **kw)

        return bouncer

    @functools.wraps(fn)
    async def wrapper(*args: _P.args, **kw: _P.kwargs) -> _TResult:
        result = await fn(*args, **kw)
        return await trampoline(result)

    return wrapper


__all__ = ["TailCall", "TailCallResult", "tailrec", "tailrec_async"]
