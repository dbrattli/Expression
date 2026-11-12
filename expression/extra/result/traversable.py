"""Data structures that can be traversed from left to right, performing an action on each element."""

from collections.abc import Callable

from expression.collections import Block, block, seq
from expression.core import Ok, Result, identity, pipe


def traverse[TSource, TResult, TError](
    fn: Callable[[TSource], Result[TResult, TError]], lst: Block[TSource]
) -> Result[Block[TResult], TError]:
    """Traverses a list of items.

    Threads an applicative computation though a list of items.
    """

    def folder(head: TSource, tail: Result[Block[TResult], TError]) -> Result[Block[TResult], TError]:
        """Prepend a successful result, preserving the first error in input order."""

        def prepend(h: TResult) -> Result[Block[TResult], TError]:
            return tail.map(lambda t: Block([h]) + t)

        return fn(head).bind(prepend)

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
