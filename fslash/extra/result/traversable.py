"""Data structures that can be traversed from left to right, performing an action on each element."""
from typing import Callable, Generator, List, TypeVar

from fslash.builders import result
from fslash.collections import Seq
from fslash.core import Ok, Result_, identity

TSource = TypeVar("TSource")
TResult = TypeVar("TResult")
TError = TypeVar("TError")


def traverse(fn: Callable[[TSource], Result_[TResult, TError]], lst: List[TSource]) -> Result_[List[TResult], TError]:
    """Traverses a list of items.

    Threads an applicative computation though a list of items.
    """

    # flake8: noqa: T484
    @result
    def folder(head: TSource, tail: Result_[List[TResult], TError]) -> Generator[TResult, TResult, List[TResult]]:
        """Same as:
        >>> fn(head).bind(lambda head: tail.bind(lambda tail: Ok([head] + tail)))
        """
        h = yield from fn(head)
        t = yield from tail
        return [h] + t

    return Seq.fold_back(folder, lst)(Ok([]))


def sequence(lst: List[Result_[TSource, TError]]) -> Result_[List[TSource], TError]:
    """Execute a sequence of result returning commands and collect the
    sequence of their response."""

    return traverse(identity, lst)
