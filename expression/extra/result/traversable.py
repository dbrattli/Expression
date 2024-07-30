"""Data structures that can be traversed from left to right, performing an action on each element."""

from collections.abc import Callable
from typing import Any, TypeVar

from expression import effect
from expression.collections import Block, block, seq
from expression.core import Ok, Result, identity, pipe


_TSource = TypeVar("_TSource")
_TResult = TypeVar("_TResult")
_TError = TypeVar("_TError")


def traverse(
    fn: Callable[[_TSource], Result[_TResult, _TError]], lst: Block[_TSource]
) -> Result[Block[_TResult], _TError]:
    """Traverses a list of items.

    Threads an applicative computation though a list of items.
    """

    @effect.result[Block[_TResult], _TError]()
    def folder(head: _TSource, tail: Result[Block[_TResult], _TError]) -> Any:
        """Fold back function.

        Same as:
        >>> fn(head).bind(lambda head: tail.bind(lambda tail: Ok([head] + tail))).
        """
        h: _TResult = yield from fn(head)
        t: Block[_TResult] = yield from tail

        return Block([h]) + t

    state: Result[Block[_TResult], _TError] = Ok(block.empty)
    ret = pipe(
        state,
        seq.fold_back(folder, lst),
    )
    return ret


def sequence(lst: Block[Result[_TSource, _TError]]) -> Result[Block[_TSource], _TError]:
    """Sequence block.

    Execute a sequence of result returning commands and collect the
    sequence of their response.
    """
    return traverse(identity, lst)
