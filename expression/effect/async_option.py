"""AsyncOption builder module.

The AsyncOption builder allows for composing asynchronous operations that
may return an optional value, using the Option type. It's similar to the Option builder but
works with async operations.
"""

from collections.abc import AsyncGenerator, Awaitable, Callable
from typing import Any

from expression.core import NOTHING, Option, Some
from expression.core.async_builder import AsyncBuilder


class AsyncOptionBuilder[TSource](AsyncBuilder[TSource, Option[Any]]):
    """AsyncOption builder.

    The AsyncOption builder allows for composing asynchronous operations that
    may return an optional value, using the Option type.
    """

    async def bind[TResult](
        self,
        xs: Option[TSource],
        fn: Callable[[Any], Awaitable[Option[TResult]]],
    ) -> Option[TResult]:
        """Bind a function to an async option value.

        In F# computation expressions, this corresponds to ``let!`` and enables
        sequencing of computations.

        Args:
            xs: The async option value to bind
            fn: The function to apply to the value if Some

        Returns:
            The result of applying fn to the value if Some, otherwise NOTHING
        """
        match xs:
            case Some(value):
                return await fn(value)
            case _:
                return NOTHING

    async def return_(self, x: TSource) -> Option[TSource]:
        """Wrap a value in an async option.

        In F# computation expressions, this corresponds to ``return`` and lifts
        a value into the option context.

        Args:
            x: The value to wrap

        Returns:
            Some containing the value
        """
        return Some(x)

    async def return_from(self, xs: Option[TSource]) -> Option[TSource]:
        """Return an async option value directly.

        In F# computation expressions, this corresponds to ``return!`` and allows
        returning an already wrapped value.

        Args:
            xs: The async option value to return

        Returns:
            The async option value unchanged
        """
        return xs

    async def combine(self, xs: Option[TSource], ys: Option[TSource]) -> Option[TSource]:
        """Combine two async option computations.

        In F# computation expressions, this enables sequencing multiple
        expressions where we only care about the final result.

        Args:
            xs: First async option computation
            ys: Second async option computation

        Returns:
            The second computation if first is Some, otherwise NOTHING
        """
        match xs:
            case Some():
                return ys
            case _:
                return NOTHING

    async def zero(self) -> Option[Any]:
        """Return the zero value for async options.

        In F# computation expressions, this is used when no value is returned,
        corresponding to None in F#.

        Returns:
            NOTHING
        """
        return NOTHING

    async def delay(self, fn: Callable[[], Option[TSource]]) -> Option[TSource]:
        """Delay the computation.

        Default implementation is to return the result of the function.
        """
        return fn()

    async def run(self, computation: Option[TSource]) -> Option[TSource]:
        """Run a computation.

        Default implementation is to return the computation as is.
        """
        return computation

    def __call__[**P](
        self,
        fn: Callable[
            P,
            AsyncGenerator[TSource, TSource]
            | AsyncGenerator[TSource, None]
            | Awaitable[TSource | None]
            | TSource
            | None,
        ],
    ) -> Callable[P, Awaitable[Option[TSource]]]:
        """The builder decorator."""
        return super().__call__(fn)


# Create singleton instance
async_option: AsyncOptionBuilder[Any] = AsyncOptionBuilder()


__all__ = ["AsyncOptionBuilder", "async_option"]
