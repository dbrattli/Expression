from collections.abc import Callable, Generator
from typing import Any

from expression.core import NOTHING, Builder, Option, Some, option


class OptionBuilder[TSource](Builder[TSource, Option[Any]]):
    def bind[TResult](self, xs: Option[TSource], fn: Callable[[TSource], Option[TResult]]) -> Option[TResult]:
        """Bind a function to an option value.

        In F# computation expressions, this corresponds to let! and enables
        sequencing of computations.

        Args:
            xs: The option value to bind
            fn: The function to apply to the value if Some

        Returns:
            The result of applying fn to the value if Some, otherwise NOTHING
        """
        return option.bind(fn)(xs)

    def return_(self, x: TSource) -> Option[TSource]:
        """Wrap a value in an option.

        In F# computation expressions, this corresponds to return and lifts
        a value into the option context.

        Args:
            x: The value to wrap

        Returns:
            Some containing the value
        """
        return Some(x)

    def return_from(self, xs: Option[TSource]) -> Option[TSource]:
        """Return an option value directly.

        In F# computation expressions, this corresponds to return! and allows
        returning an already wrapped value.

        Args:
            xs: The option value to return

        Returns:
            The option value unchanged
        """
        return xs

    def combine(self, xs: Option[TSource], ys: Option[TSource]) -> Option[TSource]:
        """Combine two option computations.

        In F# computation expressions, this enables sequencing multiple
        expressions where we only care about the final result.

        Args:
            xs: First option computation
            ys: Second option computation

        Returns:
            The second computation if first is Some, otherwise NOTHING
        """
        return xs.bind(lambda _: ys)

    def zero(self) -> Option[TSource]:
        """Return the zero value for options.

        In F# computation expressions, this is used when no value is returned,
        corresponding to None in F#.

        Returns:
            NOTHING
        """
        return NOTHING

    def delay(self, fn: Callable[[], Option[TSource]]) -> Option[TSource]:
        """Delay an option computation.

        In F# computation expressions, delay ensures proper sequencing of effects
        by controlling when computations are evaluated.

        Args:
            fn: The computation to delay

        Returns:
            The result of evaluating the computation
        """
        return fn()

    def __call__[**P](
        self,  # Ignored self parameter
        fn: Callable[
            P,
            Generator[TSource | None, TSource, TSource | None]
            | Generator[TSource | None, None, TSource | None]
            | TSource
            | None,
        ],
    ) -> Callable[P, Option[TSource]]:
        return super().__call__(fn)


__all__ = ["OptionBuilder"]
