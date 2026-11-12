from collections.abc import Callable, Generator, Iterable
from typing import Any

from expression.collections import seq
from expression.core import Builder


class SeqBuilder[TSource](Builder[TSource, Iterable[Any]]):
    def bind[TResult](self, xs: Iterable[TSource], fn: Callable[[TSource], Iterable[TResult]]) -> Iterable[TResult]:
        """Bind a function to a sequence value.

        In F# computation expressions, this corresponds to let! and enables
        sequencing of computations.

        Args:
            xs: The sequence value to bind
            fn: The function to apply to each value in the sequence

        Returns:
            The concatenated results of applying fn to each value in the sequence
        """
        # We do this eagerly to have progress in the sequence
        return [y for x in xs for y in fn(x)]

    def return_(self, x: TSource) -> Iterable[TSource]:
        """Wrap a value in a sequence.

        Args:
            x: The value to wrap

        Returns:
            A singleton sequence containing the value
        """
        return seq.singleton(x)

    def return_from(self, xs: Iterable[TSource]) -> Iterable[TSource]:
        """Return a sequence value directly.

        Args:
            xs: The sequence value to return

        Returns:
            The sequence value unchanged
        """
        return xs

    def combine(self, xs: Iterable[TSource], ys: Iterable[TSource]) -> Iterable[TSource]:
        """Combine two sequence computations.

        Args:
            xs: First sequence computation
            ys: Second sequence computation

        Returns:
            The concatenated sequences
        """
        return seq.concat(xs, ys)

    def zero(self) -> Iterable[TSource]:
        """Return the zero value for sequences.

        Returns:
            An empty sequence
        """
        return seq.empty

    def delay(self, fn: Callable[[], Iterable[TSource]]) -> Iterable[TSource]:
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

    def run(self, computation: Iterable[TSource]) -> Iterable[TSource]:
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
            Generator[TSource | None, TSource, TSource | None]
            | Generator[TSource | None, None, TSource | None]
            | TSource
            | None,
        ],
    ) -> Callable[..., Iterable[TSource]]:
        return super().__call__(fn)


__all__ = ["SeqBuilder"]
