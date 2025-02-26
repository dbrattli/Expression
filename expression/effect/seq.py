from collections.abc import Callable, Generator, Iterable
from typing import Any, TypeVar

from expression.collections import seq
from expression.core import Builder


_TSource = TypeVar("_TSource")
_TResult = TypeVar("_TResult")


class SeqBuilder(Builder[_TSource, Iterable[Any]]):
    def bind(self, xs: Iterable[_TSource], fn: Callable[[_TSource], Iterable[_TResult]]) -> Iterable[_TResult]:
        """Bind a function to a sequence value.

        In F# computation expressions, this corresponds to let! and enables
        sequencing of computations.

        Args:
            xs: The sequence value to bind
            fn: The function to apply to each value in the sequence

        Returns:
            The concatenated results of applying fn to each value in the sequence
        """
        # This may look a bit weird, but it's essentially the
        # proccessing of each line in the generator function. The
        # `fn(x)` is the actual processing of the value in the sequence.
        # We do not process more than one line at a time anyway.
        for x in xs:
            return fn(x)

        return []

    def return_(self, x: _TSource) -> Iterable[_TSource]:
        """Wrap a value in a sequence.

        Args:
            x: The value to wrap

        Returns:
            A singleton sequence containing the value
        """
        return seq.singleton(x)

    def return_from(self, xs: Iterable[_TSource]) -> Iterable[_TSource]:
        """Return a sequence value directly.

        Args:
            xs: The sequence value to return

        Returns:
            The sequence value unchanged
        """
        return xs

    def combine(self, xs: Iterable[_TSource], ys: Iterable[_TSource]) -> Iterable[_TSource]:
        """Combine two sequence computations.

        Args:
            xs: First sequence computation
            ys: Second sequence computation

        Returns:
            The concatenated sequences
        """
        return seq.concat(xs, ys)

    def zero(self) -> Iterable[_TSource]:
        """Return the zero value for sequences.

        Returns:
            An empty sequence
        """
        return seq.empty

    def delay(self, fn: Callable[[], Iterable[_TSource]]) -> Iterable[_TSource]:
        """Delay the computation.

        Returns a sequence that is built from the given delayed specification of a
        sequence. The input function is evaluated each time an iterator for the sequence
        is requested.

        Args:
            fn: The generating function for the sequence.

        Returns:
            A sequence that will evaluate the function when iterated.
        """
        return fn()

    def run(self, computation: Iterable[_TSource]) -> Iterable[_TSource]:
        """Run a computation.

        In Python, the return value should be included in the sequence
        as it's essentially a "final yield".

        Args:
            computation: The computation to run

        Returns:
            The result of the computation including the return value
        """
        # Simply return the computation as is, including the return value
        return computation

    def __call__(
        self,
        fn: Callable[
            ...,
            Generator[_TSource | None, _TSource, _TSource | None] | Generator[_TSource | None, None, _TSource | None],
        ],
    ) -> Callable[..., Iterable[_TSource]]:
        return super().__call__(fn)


__all__ = ["SeqBuilder"]
