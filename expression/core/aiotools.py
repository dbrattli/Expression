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

TSource = TypeVar("TSource")

Continuation = Callable[[TSource], None]
Callbacks = Callable[[Continuation[TSource], Continuation[Exception], Continuation[OperationCanceledError]], None]


def from_continuations(callback: Callbacks[TSource]) -> Awaitable[TSource]:
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
    future: "Future[TSource]" = asyncio.Future()

    def done(value: TSource) -> None:
        future.set_result(value)

    def error(err: Exception) -> None:
        future.set_exception(err)

    def cancel(_: OperationCanceledError) -> None:
        future.cancel()

    callback(done, error, cancel)
    return future


def start(computation: Awaitable[Any], token: Optional[CancellationToken] = None) -> None:
    """Starts the asynchronous computation in the event loop. Do not
    await its result.

    If no cancellation token is provided then the default cancellation
    token is used.
    """

    task = asyncio.create_task(computation)

    def cb():
        task.cancel()

    if token:
        token.register(cb)
    return None


def start_immediate(computation: Awaitable[Any], token: Optional[CancellationToken] = None) -> None:
    """Runs an asynchronous computation, starting immediately on the
    current operating system thread."""
    task = asyncio.create_task(computation)

    def cb() -> None:
        task.cancel()

    if token:
        token.register(cb)
    return None


def run_synchronously(computation: Awaitable[TSource]) -> TSource:
    """Runs the asynchronous computation and await its result."""
    return asyncio.run(computation)


async def singleton(value: TSource) -> TSource:
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


def from_result(result: TSource) -> Awaitable[TSource]:
    """Creates a async operation that's completed successfully with the
    specified result."""

    async def from_result(result: TSource) -> TSource:
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
