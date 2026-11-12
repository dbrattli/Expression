"""Async builder module.

This module provides the base class for async builders, which are used to
create computational expressions for async operations.
"""

import inspect
from abc import ABC
from collections.abc import AsyncGenerator, Awaitable, Callable
from functools import wraps
from typing import Any, cast

from .error import EffectError


class AsyncBuilderState[T]:
    """Encapsulates the state of an async builder computation."""

    def __init__(self):
        self.is_done = False


class AsyncBuilder[T, M](ABC):  # Corrected Generic definition
    """Async effect builder."""

    # Required methods
    async def bind(
        self, xs: M, fn: Callable[[T], Awaitable[M]]
    ) -> M:  # Use concrete types for Callable input and output
        raise NotImplementedError("AsyncBuilder does not implement a `bind` method")

    async def return_(self, x: T) -> M:
        raise NotImplementedError("AsyncBuilder does not implement a `return` method")

    async def return_from(self, xs: M) -> M:
        raise NotImplementedError("AsyncBuilder does not implement a `return` from method")

    async def combine(self, xs: M, ys: M) -> M:
        """Used for combining multiple statements in the effect."""
        raise NotImplementedError("AsyncBuilder does not implement a `combine` method")

    async def zero(self) -> M:
        """Zero effect.

        Called if the effect raises StopAsyncIteration without a value, i.e
        returns None.
        """
        raise NotImplementedError("AsyncBuilder does not implement a `zero` method")

    # Optional methods for control flow
    async def delay(self, fn: Callable[[], M]) -> M:
        """Delay the computation.

        Default implementation is to return the result of the function.
        """
        return fn()

    async def run(self, computation: M) -> M:
        """Run a computation.

        Default implementation is to return the computation as is.
        """
        return computation

    # Internal implementation
    async def _send(
        self,
        gen: AsyncGenerator[T, Any],
        state: AsyncBuilderState[T],  # Use AsyncBuilderState
        value: T,
    ) -> M:
        try:
            yielded = await gen.asend(value)
            return await self.return_(yielded)
        except EffectError as error:
            # Effect errors (Nothing, Error, etc) short circuits
            state.is_done = True
            return await self.return_from(cast("M", error.args[0]))
        except StopAsyncIteration:
            state.is_done = True
            raise
        except Exception:
            state.is_done = True
            raise

    def __call__[**P](
        self,
        fn: Callable[
            P,
            AsyncGenerator[T, Any] | Awaitable[T | None] | T | None,
        ],
    ) -> Callable[P, Awaitable[M]]:
        """The builder decorator.

        A body without a `yield` statement is a plain async function. Its
        return value is treated like a `return` statement (F# `return`): a
        value is lifted with `return_`, and a `None` return value maps to
        `zero()`.
        """

        @wraps(fn)
        async def wrapper(*args: P.args, **kw: P.kwargs) -> M:
            body = fn(*args, **kw)

            if not inspect.isasyncgen(body):
                # A body without a `yield` statement is a plain (async)
                # function. Treat its return value like a `return` statement:
                # a value maps to return_(value), a None return value maps
                # to zero().
                result_value: T | None
                if inspect.iscoroutine(body):
                    result_value = await cast("Awaitable[T]", body)
                else:
                    result_value = cast("T | None", body)
                if result_value is None:
                    return await self.run(await self.zero())
                return await self.run(await self.return_(result_value))

            gen = cast("AsyncGenerator[T, Any]", body)
            state = AsyncBuilderState[T]()  # Initialize AsyncBuilderState
            result: M = await self.zero()  # Initialize result
            value: M

            async def binder(value: Any) -> M:
                ret = await self._send(gen, state, value)  # Pass state to _send
                return await self.delay(lambda: ret)  # Delay every bind call

            try:
                # Initialize co-routine with None to start the generator and get the
                # first value
                result = value = await binder(None)

                while not state.is_done:  # Loop until coroutine is exhausted
                    value = await self.bind(value, binder)  # Send value to coroutine
                    result = await self.combine(result, value)  # Combine previous result with new value

            except StopAsyncIteration:
                # This will happens if the generator exits by returning None
                pass

            return await self.run(result)  # Run the result

        return wrapper


__all__ = ["AsyncBuilder", "AsyncBuilderState"]
