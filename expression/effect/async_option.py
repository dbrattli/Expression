"""AsyncOption builder module.

The AsyncOption builder allows for composing asynchronous operations that
may return an optional value, using the Option type. It's similar to the Option builder but
works with async operations.
"""

from collections.abc import AsyncGenerator, Awaitable, Callable
from typing import Any, ParamSpec, TypeVar

from expression.core import Nothing, Option, Some
from expression.core.async_builder import AsyncBuilder


_TSource = TypeVar("_TSource")
_TResult = TypeVar("_TResult")
_P = ParamSpec("_P")


class AsyncOptionBuilder(AsyncBuilder[_TSource, Option[Any]]):
    """AsyncOption builder.

    The AsyncOption builder allows for composing asynchronous operations that
    may return an optional value, using the Option type.
    """

    async def bind(
        self,
        xs: Option[_TSource],
        fn: Callable[[Any], Awaitable[Option[_TResult]]],
    ) -> Option[_TResult]:
        """Bind a function to an async option value.

        In F# computation expressions, this corresponds to ``let!`` and enables
        sequencing of computations.

        Args:
            xs: The async option value to bind
            fn: The function to apply to the value if Some

        Returns:
            The result of applying fn to the value if Some, otherwise Nothing
        """
        match xs:
            case Option(tag="some", some=value):
                return await fn(value)
            case _:
                return Nothing

    async def return_(self, x: _TSource) -> Option[_TSource]:
        """Wrap a value in an async option.

        In F# computation expressions, this corresponds to ``return`` and lifts
        a value into the option context.

        Args:
            x: The value to wrap

        Returns:
            Some containing the value
        """
        return Some(x)

    async def return_from(self, xs: Option[_TSource]) -> Option[_TSource]:
        """Return an async option value directly.

        In F# computation expressions, this corresponds to ``return!`` and allows
        returning an already wrapped value.

        Args:
            xs: The async option value to return

        Returns:
            The async option value unchanged
        """
        return xs

    async def combine(self, xs: Option[_TSource], ys: Option[_TSource]) -> Option[_TSource]:
        """Combine two async option computations.

        In F# computation expressions, this enables sequencing multiple
        expressions where we only care about the final result.

        Args:
            xs: First async option computation
            ys: Second async option computation

        Returns:
            The second computation if first is Some, otherwise Nothing
        """
        match xs:
            case Option(tag="some"):
                return ys
            case _:
                return Nothing

    async def zero(self) -> Option[Any]:
        """Return the zero value for async options.

        In F# computation expressions, this is used when no value is returned,
        corresponding to None in F#.

        Returns:
            Nothing
        """
        return Nothing

    async def delay(self, fn: Callable[[], Option[_TSource]]) -> Option[_TSource]:
        """Delay the computation.

        Default implementation is to return the result of the function.
        """
        return fn()

    async def run(self, computation: Option[_TSource]) -> Option[_TSource]:
        """Run a computation.

        Default implementation is to return the computation as is.
        """
        return computation

    def __call__(
        self,
        fn: Callable[
            _P,
            AsyncGenerator[_TSource, _TSource] | AsyncGenerator[_TSource, None],
        ],
    ) -> Callable[_P, Awaitable[Option[_TSource]]]:
        """The builder decorator."""
        return super().__call__(fn)


# Create singleton instance
async_option: AsyncOptionBuilder[Any] = AsyncOptionBuilder()


__all__ = ["AsyncOptionBuilder", "async_option"]
