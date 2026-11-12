"""AsyncResult builder module.

The AsyncResult builder allows for composing asynchronous operations that
may fail, using the Result type. It's similar to the Result builder but
works with async operations.
"""

from collections.abc import AsyncGenerator, Awaitable, Callable
from typing import Any

from expression.core import Error, Ok, Result
from expression.core.async_builder import AsyncBuilder


class AsyncResultBuilder[TSource, TError](AsyncBuilder[TSource, Result[Any, TError]]):
    """AsyncResult builder.

    The AsyncResult builder allows for composing asynchronous operations that
    may fail, using the Result type.
    """

    async def bind[TResult](
        self,
        xs: Result[TSource, TError],
        fn: Callable[[Any], Awaitable[Result[TResult, TError]]],
    ) -> Result[TResult, TError]:
        """Bind a function to an async result value.

        In F# computation expressions, this corresponds to ``let!`` and enables
        sequencing of computations.

        Args:
            xs: The async result value to bind
            fn: The function to apply to the value if Ok

        Returns:
            The result of applying fn to the value if Ok, otherwise Error
        """
        match xs:
            case Ok(value):
                return await fn(value)
            case Error(error):
                return Error(error)

    async def return_(self, x: TSource) -> Result[TSource, TError]:
        """Wrap a value in an async result.

        In F# computation expressions, this corresponds to ``return`` and lifts
        a value into the result context.

        Args:
            x: The value to wrap

        Returns:
            Ok containing the value
        """
        return Ok(x)

    async def return_from(self, xs: Result[TSource, TError]) -> Result[TSource, TError]:
        """Return an async result value directly.

        In F# computation expressions, this corresponds to ``return!`` and allows
        returning an already wrapped value.

        Args:
            xs: The async result value to return

        Returns:
            The async result value unchanged
        """
        return xs

    async def combine(self, xs: Result[TSource, TError], ys: Result[TSource, TError]) -> Result[TSource, TError]:
        """Combine two async result computations.

        In F# computation expressions, this enables sequencing multiple
        expressions where we only care about the final result.

        Args:
            xs: First async result computation
            ys: Second async result computation

        Returns:
            The second computation if first is Ok, otherwise Error
        """
        match xs:
            case Ok(_):
                return ys
            case Error(error):
                return Error(error)

    async def zero(self) -> Result[Any, TError]:
        """Return the zero value for async results.

        In F# computation expressions, this is used when no value is returned,
        corresponding to Ok(()) in F#.

        Returns:
            Ok(None)
        """
        return Ok(None)

    async def delay(self, fn: Callable[[], Result[TSource, TError]]) -> Result[TSource, TError]:
        """Delay the computation.

        Default implementation is to return the result of the function.
        """
        return fn()

    async def run(self, computation: Result[TSource, TError]) -> Result[TSource, TError]:
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
    ) -> Callable[P, Awaitable[Result[TSource, TError]]]:
        """The builder decorator."""
        return super().__call__(fn)


# Create singleton instances
async_result: AsyncResultBuilder[Any, Any] = AsyncResultBuilder()


class AsyncTryBuilder[TSource](AsyncResultBuilder[TSource, Exception]):
    """AsyncTry builder.

    The AsyncTry builder allows for composing asynchronous operations that
    may throw exceptions, using the Result type with Exception as the error type.
    """

    pass


# Create singleton instance
async_try: AsyncTryBuilder[Any] = AsyncTryBuilder()


__all__ = ["AsyncResultBuilder", "AsyncTryBuilder", "async_result", "async_try"]
