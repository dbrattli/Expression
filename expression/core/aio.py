"""The aio (asyncio) module contains asynchronous functions similar to
the F# `Async` module.
"""
import asyncio
from asyncio import Future
from typing import Any, Awaitable, Callable, Optional, TypeVar

from expression.system import CancellationToken, OperationCanceledError

TSource = TypeVar("TSource")

Continuation = Callable[[TSource], None]


def from_continuations(
    callback: Callable[[Continuation[TSource], Continuation[Exception], Continuation[OperationCanceledError]], None]
) -> Awaitable[TSource]:
    """Creates an asynchronous computation that captures the current
    success, exception and cancellation continuations. The callback must
    eventually call exactly one of the given continuations.

    Args:
        callback: The function that accepts the current success,
            exception, and cancellation continuations.

    Returns:
        An asynchronous computation that provides the callback with
        the current continuations.
    """
    future: Future[Any] = asyncio.Future()

    def done(value: TSource) -> None:
        future.set_result(value)

    def error(error: Exception) -> None:
        future.set_exception(error)

    def cancel(cancel: OperationCanceledError) -> None:
        future.cancel()

    callback(done, error, cancel)
    return asyncio.ensure_future(future)


def start(computation: Awaitable[Any], token: Optional[CancellationToken] = None) -> None:
    """Starts the asynchronous computation in the event loop. Do not await its result.

    If no cancellation token is provided then the default cancellation token
    is used."""
    task = asyncio.create_task(computation)

    def cb():
        task.cancel()

    if token:
        token.register(cb)
    return None


def start_immediate(computation: Awaitable[Any], token: Optional[CancellationToken] = None) -> None:
    task = asyncio.create_task(computation)

    def cb():
        task.cancel()

    if token:
        token.register(cb)
    return None


def run_synchronous(computation: Awaitable[TSource]) -> TSource:
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
    return await asyncio.sleep(msecs / 1000.0)


__all__ = ["singleton"]
