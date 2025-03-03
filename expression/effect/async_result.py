"""AsyncResult builder module.

The AsyncResult builder allows for composing asynchronous operations that
may fail, using the Result type. It's similar to the Result builder but
works with async operations.
"""

from collections.abc import AsyncGenerator, Awaitable, Callable
from typing import Any, ParamSpec, TypeVar

from expression.core import Ok, Result
from expression.core.async_builder import AsyncBuilder


_TSource = TypeVar("_TSource")
_TResult = TypeVar("_TResult")
_TError = TypeVar("_TError")
_P = ParamSpec("_P")


class AsyncResultBuilder(AsyncBuilder[_TSource, Result[Any, _TError]]):
    """AsyncResult builder.

    The AsyncResult builder allows for composing asynchronous operations that
    may fail, using the Result type.
    """

    async def bind(
        self,
        xs: Result[_TSource, _TError],
        fn: Callable[[Any], Awaitable[Result[_TResult, _TError]]],
    ) -> Result[_TResult, _TError]:
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
            case Result(tag="ok", ok=value):
                return await fn(value)
            case Result(error=error):
                return Result[_TResult, _TError].Error(error)

    async def return_(self, x: _TSource) -> Result[_TSource, _TError]:
        """Wrap a value in an async result.

        In F# computation expressions, this corresponds to ``return`` and lifts
        a value into the result context.

        Args:
            x: The value to wrap

        Returns:
            Ok containing the value
        """
        return Ok(x)

    async def return_from(self, xs: Result[_TSource, _TError]) -> Result[_TSource, _TError]:
        """Return an async result value directly.

        In F# computation expressions, this corresponds to ``return!`` and allows
        returning an already wrapped value.

        Args:
            xs: The async result value to return

        Returns:
            The async result value unchanged
        """
        return xs

    async def combine(self, xs: Result[_TSource, _TError], ys: Result[_TSource, _TError]) -> Result[_TSource, _TError]:
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
            case Result(tag="ok", ok=_):
                return ys
            case Result(error=error):
                return Result[_TSource, _TError].Error(error)

    async def zero(self) -> Result[Any, _TError]:
        """Return the zero value for async results.

        In F# computation expressions, this is used when no value is returned,
        corresponding to Ok(()) in F#.

        Returns:
            Ok(None)
        """
        return Ok(None)

    async def delay(self, fn: Callable[[], Result[_TSource, _TError]]) -> Result[_TSource, _TError]:
        """Delay the computation.

        Default implementation is to return the result of the function.
        """
        return fn()

    async def run(self, computation: Result[_TSource, _TError]) -> Result[_TSource, _TError]:
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
    ) -> Callable[_P, Awaitable[Result[_TSource, _TError]]]:
        """The builder decorator."""
        return super().__call__(fn)


# Create singleton instances
async_result: AsyncResultBuilder[Any, Any] = AsyncResultBuilder()


class AsyncTryBuilder(AsyncResultBuilder[_TSource, Exception]):
    """AsyncTry builder.

    The AsyncTry builder allows for composing asynchronous operations that
    may throw exceptions, using the Result type with Exception as the error type.
    """

    pass


# Create singleton instance
async_try: AsyncTryBuilder[Any] = AsyncTryBuilder()


__all__ = ["AsyncResultBuilder", "AsyncTryBuilder", "async_result", "async_try"]
