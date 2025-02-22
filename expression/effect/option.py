from collections.abc import Callable, Generator
from typing import Any, TypeVar

from typing_extensions import ParamSpec

from expression.core import Builder, Nothing, Option, Some, option


_TSource = TypeVar("_TSource")
_TResult = TypeVar("_TResult")
_P = ParamSpec("_P")


class OptionBuilder(Builder[_TSource, Option[Any]]):
    def bind(self, xs: Option[_TSource], fn: Callable[[_TSource], Option[_TResult]]) -> Option[_TResult]:
        """Bind a function to an option value.

        In F# computation expressions, this corresponds to let! and enables
        sequencing of computations.

        Args:
            xs: The option value to bind
            fn: The function to apply to the value if Some

        Returns:
            The result of applying fn to the value if Some, otherwise Nothing
        """
        return option.bind(fn)(xs)

    def return_(self, x: _TSource) -> Option[_TSource]:
        """Wrap a value in an option.

        In F# computation expressions, this corresponds to return and lifts
        a value into the option context.

        Args:
            x: The value to wrap

        Returns:
            Some containing the value
        """
        return Some(x)

    def return_from(self, xs: Option[_TSource]) -> Option[_TSource]:
        """Return an option value directly.

        In F# computation expressions, this corresponds to return! and allows
        returning an already wrapped value.

        Args:
            xs: The option value to return

        Returns:
            The option value unchanged
        """
        return xs

    def combine(self, xs: Option[_TSource], ys: Option[_TSource]) -> Option[_TSource]:
        """Combine two option computations.

        In F# computation expressions, this enables sequencing multiple
        expressions where we only care about the final result.

        Args:
            xs: First option computation
            ys: Second option computation

        Returns:
            The second computation if first is Some, otherwise Nothing
        """
        return xs.bind(lambda _: ys)

    def zero(self) -> Option[_TSource]:
        """Return the zero value for options.

        In F# computation expressions, this is used when no value is returned,
        corresponding to None in F#.

        Returns:
            Nothing
        """
        return Nothing

    def delay(self, fn: Callable[[], Option[_TSource]]) -> Option[_TSource]:
        """Delay an option computation.

        In F# computation expressions, delay ensures proper sequencing of effects
        by controlling when computations are evaluated.

        Args:
            fn: The computation to delay

        Returns:
            The result of evaluating the computation
        """
        return fn()

    def __call__(
        self,  # Ignored self parameter
        fn: Callable[
            _P,
            Generator[_TSource | None, _TSource, _TSource | None] | Generator[_TSource | None, None, _TSource | None],
        ],
    ) -> Callable[_P, Option[_TSource]]:
        return super().__call__(fn)


__all__ = ["OptionBuilder"]
