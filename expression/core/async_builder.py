"""Async builder module.

This module provides the base class for async builders, which are used to
create computational expressions for async operations.
"""

import inspect
from abc import ABC
from collections.abc import AsyncGenerator, Awaitable, Callable
from functools import wraps
from typing import Any, Generic, TypeVar, cast

from typing_extensions import ParamSpec

from .error import EffectError


_T = TypeVar("_T")  # The container item type
_M = TypeVar("_M")  # for container type
_P = ParamSpec("_P")


class AsyncBuilderState(Generic[_T]):
    """Encapsulates the state of an async builder computation."""

    def __init__(self):
        self.is_done = False


class AsyncBuilder(Generic[_T, _M], ABC):  # Corrected Generic definition
    """Async effect builder."""

    # Required methods
    async def bind(
        self, xs: _M, fn: Callable[[_T], Awaitable[_M]]
    ) -> _M:  # Use concrete types for Callable input and output
        raise NotImplementedError("AsyncBuilder does not implement a `bind` method")

    async def return_(self, x: _T) -> _M:
        raise NotImplementedError("AsyncBuilder does not implement a `return` method")

    async def return_from(self, xs: _M) -> _M:
        raise NotImplementedError("AsyncBuilder does not implement a `return` from method")

    async def combine(self, xs: _M, ys: _M) -> _M:
        """Used for combining multiple statements in the effect."""
        raise NotImplementedError("AsyncBuilder does not implement a `combine` method")

    async def zero(self) -> _M:
        """Zero effect.

        Called if the effect raises StopAsyncIteration without a value, i.e
        returns None.
        """
        raise NotImplementedError("AsyncBuilder does not implement a `zero` method")

    # Optional methods for control flow
    async def delay(self, fn: Callable[[], _M]) -> _M:
        """Delay the computation.

        Default implementation is to return the result of the function.
        """
        return fn()

    async def run(self, computation: _M) -> _M:
        """Run a computation.

        Default implementation is to return the computation as is.
        """
        return computation

    # Internal implementation
    async def _send(
        self,
        gen: AsyncGenerator[_T, Any],
        state: AsyncBuilderState[_T],  # Use AsyncBuilderState
        value: _T,
    ) -> _M:
        try:
            yielded = await gen.asend(value)
            return await self.return_(yielded)
        except EffectError as error:
            # Effect errors (Nothing, Error, etc) short circuits
            state.is_done = True
            return await self.return_from(cast("_M", error.args[0]))
        except StopAsyncIteration:
            state.is_done = True
            raise
        except Exception:
            state.is_done = True
            raise

    def __call__(
        self,
        fn: Callable[
            _P,
            AsyncGenerator[_T, Any] | Awaitable[_T | None] | _T | None,
        ],
    ) -> Callable[_P, Awaitable[_M]]:
        """The builder decorator.

        A body without a `yield` statement is a plain async function. Its
        return value is treated like a `return` statement (F# `return`): a
        value is lifted with `return_`, and a `None` return value maps to
        `zero()`.
        """

        @wraps(fn)
        async def wrapper(*args: _P.args, **kw: _P.kwargs) -> _M:
            body = fn(*args, **kw)

            if not inspect.isasyncgen(body):
                # A body without a `yield` statement is a plain (async)
                # function. Treat its return value like a `return` statement:
                # a value maps to return_(value), a None return value maps
                # to zero().
                result_value: _T | None
                if inspect.iscoroutine(body):
                    result_value = await cast("Awaitable[_T]", body)
                else:
                    result_value = cast("_T | None", body)
                if result_value is None:
                    return await self.run(await self.zero())
                return await self.run(await self.return_(result_value))

            gen = cast("AsyncGenerator[_T, Any]", body)
            state = AsyncBuilderState[_T]()  # Initialize AsyncBuilderState
            result: _M = await self.zero()  # Initialize result
            value: _M

            async def binder(value: Any) -> _M:
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
