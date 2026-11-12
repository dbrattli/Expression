"""Data structures that can be traversed from left to right, performing an action on each element."""

from collections.abc import Callable
from typing import Any, cast

from expression import effect
from expression.collections import Block, block, seq
from expression.core import Ok, Result, identity, pipe


def traverse[TSource, TResult, TError](
    fn: Callable[[TSource], Result[TResult, TError]], lst: Block[TSource]
) -> Result[Block[TResult], TError]:
    """Traverses a list of items.

    Threads an applicative computation though a list of items.
    """

    @effect.result[Block[TResult], TError]()
    def folder(head: TSource, tail: Result[Block[TResult], TError]) -> Any:
        """Fold back function.

        Same as:
        >>> fn(head).bind(lambda head: tail.bind(lambda tail: Ok([head] + tail))).
        """
        # Pyright #11881 loses the return type for a union of iterable cases.
        h = cast(TResult, (yield from fn(head)))
        t = cast(Block[TResult], (yield from tail))

        return Block([h]) + t

    state: Result[Block[TResult], TError] = Ok(block.empty)
    ret = pipe(
        state,
        seq.fold_back(folder, lst),
    )
    return ret


def sequence[TSource, TError](lst: Block[Result[TSource, TError]]) -> Result[Block[TSource], TError]:
    """Sequence block.

    Execute a sequence of result returning commands and collect the
    sequence of their response.
    """
    return traverse(identity, lst)
