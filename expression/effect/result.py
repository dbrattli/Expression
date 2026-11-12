from collections.abc import Callable, Generator
from typing import Any

from expression.core import Builder, Ok, Result


class ResultBuilder[TSource, TError](Builder[TSource, Result[Any, TError]]):
    def bind[TResult](
        self,
        xs: Result[TSource, TError],
        fn: Callable[[Any], Result[TResult, TError]],
    ) -> Result[TResult, TError]:
        """Bind a function to a result value.

        In F# computation expressions, this corresponds to ``let!`` and enables
        sequencing of computations.

        Args:
            xs: The result value to bind
            fn: The function to apply to the value if Ok

        Returns:
            The result of applying fn to the value if Ok, otherwise Error
        """
        return xs.bind(fn)

    def return_(self, x: TSource) -> Result[TSource, TError]:  # Use Any for return_ type
        """Wrap a value in a result.

        In F# computation expressions, this corresponds to ``return`` and lifts
        a value into the result context.

        Args:
            x: The value to wrap

        Returns:
            Ok containing the value
        """
        return Ok(x)

    def return_from(self, xs: Result[TSource, TError]) -> Result[TSource, TError]:
        """Return a result value directly.

        In F# computation expressions, this corresponds to ``return!`` and allows
        returning an already wrapped value.

        Args:
            xs: The result value to return

        Returns:
            The result value unchanged
        """
        return xs

    def combine(self, xs: Result[TSource, TError], ys: Result[TSource, TError]) -> Result[TSource, TError]:
        """Combine two result computations.

        In F# computation expressions, this enables sequencing multiple
        expressions where we only care about the final result.

        Args:
            xs: First result computation
            ys: Second result computation

        Returns:
            The second computation if first is Ok, otherwise Error
        """
        return xs.bind(lambda _: ys)

    def zero(self) -> Result[Any, TError]:  # Use Any for zero return type
        """Return the zero value for results.

        In F# computation expressions, this is used when no value is returned,
        corresponding to Ok(()) in F#.

        Returns:
            Ok(None)
        """
        return Ok(None)

    def __call__[**P](
        self,  # Ignored self parameter
        fn: Callable[
            P,
            Generator[TSource | None, TSource, TSource | None]
            | Generator[TSource | None, None, TSource | None]
            | TSource
            | None,
        ],
    ) -> Callable[P, Result[TSource, TError]]:
        return super().__call__(fn)


class TryBuilder[TSource](ResultBuilder[TSource, Exception]): ...


__all__ = ["ResultBuilder", "TryBuilder"]
