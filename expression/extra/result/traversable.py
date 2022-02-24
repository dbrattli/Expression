"""Data structures that can be traversed from left to right, performing an action on each element."""
from typing import Any, Callable, List, TypeVar, cast

from expression import effect
from expression.collections import seq
from expression.core import Ok, Result, identity, pipe

_TSource = TypeVar("_TSource")
_TResult = TypeVar("_TResult")
_TError = TypeVar("_TError")


def traverse(
    fn: Callable[[_TSource], Result[_TResult, _TError]], lst: List[_TSource]
) -> Result[List[_TResult], _TError]:
    """Traverses a list of items.

    Threads an applicative computation though a list of items.
    """

    @effect.result[List[_TResult], _TError]()
    def folder(head: _TSource, tail: Result[List[_TResult], _TError]) -> Any:
        """Same as:
        >>> fn(head).bind(lambda head: tail.bind(lambda tail: Ok([head] + tail)))
        """
        h: _TResult = yield from fn(head)
        t: List[_TResult] = yield from tail

        return [h] + t

    state: Result[List[_TResult], _TError] = Ok([])
    ret = pipe(
        state,
        seq.fold_back(folder, lst),
    )
    return ret


def sequence(lst: List[Result[_TSource, _TError]]) -> Result[List[_TSource], _TError]:
    """Execute a sequence of result returning commands and collect the
    sequence of their response."""

    fn = cast(
        Callable[[Result[_TSource, _TError]], Result[_TSource, _TError]], identity
    )
    return traverse(fn, lst)
