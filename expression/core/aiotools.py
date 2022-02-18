"""The aiotools (async) module.

The aio (asyncio) module contains asynchronous utility functions for
working with async / await.

The module is inspired by the F# `Async` module, but builds on top of
Python async / await instead of providing an asynchronous IO mechanism
by itself.
"""
import asyncio
from asyncio import Future
from typing import Any, Awaitable, Callable, Optional, TypeVar

from expression.system import CancellationToken, OperationCanceledError

_TSource = TypeVar("_TSource")

Continuation = Callable[[_TSource], None]
Callbacks = Callable[
    [
        Continuation[_TSource],
        Continuation[Exception],
        Continuation[OperationCanceledError],
    ],
    None,
]


def from_continuations(callback: Callbacks[_TSource]) -> Awaitable[_TSource]:
    """Creates an asynchronous computation that captures the current
    success, exception and cancellation continuations. The callback must
    eventually call exactly one of the given continuations.

    Args:
        callback: The function that accepts the current success,
            exception, and cancellation continuations.

    Returns:
        An asynchronous computation that provides the callback with the
        current continuations.
    """
    future: "Future[_TSource]" = asyncio.Future()

    def done(value: _TSource) -> None:
        future.set_result(value)

    def error(err: Exception) -> None:
        future.set_exception(err)

    def cancel(_: OperationCanceledError) -> None:
        future.cancel()

    callback(done, error, cancel)
    return future


def start(
    computation: Awaitable[Any], token: Optional[CancellationToken] = None
) -> None:
    """Starts the asynchronous computation in the event loop. Do not
    await its result.

    If no cancellation token is provided then the default cancellation
    token is used.
    """

    async def runner() -> Any:
        return await computation

    task = asyncio.create_task(runner())

    def cb():
        task.cancel()

    if token:
        token.register(cb)
    return None


def start_immediate(
    computation: Awaitable[Any], token: Optional[CancellationToken] = None
) -> None:
    """Runs an asynchronous computation, starting immediately on the
    current operating system thread."""

    async def runner() -> Any:
        return await computation

    task = asyncio.create_task(runner())

    def cb() -> None:
        task.cancel()

    if token:
        token.register(cb)
    return None


def run_synchronously(computation: Awaitable[_TSource]) -> _TSource:
    """Runs the asynchronous computation and await its result."""
    return asyncio.run(computation)


async def singleton(value: _TSource) -> _TSource:
    """Async function that returns a single value."""
    return value


async def sleep(msecs: int) -> None:
    """Creates an asynchronous computation that will sleep for the given
    time. This is scheduled using a System.Threading.Timer object. The
    operation will not block operating system threads for the duration
    of the wait."""
    await asyncio.sleep(msecs / 1000.0)


async def empty() -> None:
    """Async no-op"""


def from_result(result: _TSource) -> Awaitable[_TSource]:
    """Creates a async operation that's completed successfully with the
    specified result."""

    async def from_result(result: _TSource) -> _TSource:
        """Async return value"""
        return result

    return from_result(result)


__all__ = [
    "Continuation",
    "empty",
    "from_continuations",
    "singleton",
    "sleep",
    "start",
    "start_immediate",
    "run_synchronously",
]
