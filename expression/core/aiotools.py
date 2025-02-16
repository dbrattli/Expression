"""The aiotools (async) module.

The aio (asyncio) module contains asynchronous utility functions for
working with async / await.

The module is inspired by the F# `Async` module, but builds on top of
Python async / await instead of providing an asynchronous IO mechanism
by itself.
"""

import asyncio
from asyncio import Future, Task
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

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
    """Create async computation from continuations.

    Creates an asynchronous computation that captures the current
    success, exception and cancellation continuations. The callback must
    eventually call exactly one of the given continuations.

    Args:
        callback: The function that accepts the current success,
            exception, and cancellation continuations.

    Returns:
        An asynchronous computation that provides the callback with the
        current continuations.
    """
    future: Future[_TSource] = asyncio.Future()

    def done(value: _TSource) -> None:
        if not future.done():
            future.set_result(value)

    def error(err: Exception) -> None:
        if not future.done():
            future.set_exception(err)

    def cancel(_: OperationCanceledError) -> None:
        if not future.done():
            future.cancel()

    callback(done, error, cancel)
    return future


# Tasks that are scheduled on the main event loop. The main event loop keeps a
# a weak reference to the tasks, so we need to keep a strong reference to them until
# they are completed.
__running_tasks: set[Task[Any]] = set()


def start(computation: Awaitable[Any], token: CancellationToken | None = None) -> None:
    """Start computation.

    Starts the asynchronous computation in the event loop. Do not await
    its result.

    If no cancellation token is provided then the default cancellation
    token is used.
    """

    async def runner() -> Any:
        result = await computation
        __running_tasks.remove(task)
        return result

    task = asyncio.create_task(runner())
    __running_tasks.add(task)

    def cb():
        task.cancel()

    if token:
        token.register(cb)
    return None


def start_immediate(computation: Awaitable[Any], token: CancellationToken | None = None) -> None:
    """Start computation immediately.

    Runs an asynchronous computation, starting immediately on the
    current operating system thread.
    """

    async def runner() -> Any:
        result = await computation
        __running_tasks.remove(task)
        return result

    task = asyncio.create_task(runner())
    __running_tasks.add(task)

    def cb() -> None:
        task.cancel()

    if token:
        token.register(cb)
    return None


def run_synchronously(computation: Awaitable[_TSource]) -> _TSource:
    """Runs the asynchronous computation and await its result."""

    async def runner() -> _TSource:
        return await computation

    return asyncio.run(runner())


async def singleton(value: _TSource) -> _TSource:
    """Async function that returns a single value."""
    return value


async def sleep(msecs: int) -> None:
    """Sleep.

    Creates an asynchronous computation that will sleep for the given
    time. This is scheduled using a System.Threading.Timer object. The
    operation will not block operating system threads for the duration
    of the wait.
    """
    await asyncio.sleep(msecs / 1000.0)


async def empty() -> None:
    """Async no-op."""


def from_result(result: _TSource) -> Awaitable[_TSource]:
    """Awaitable from result.

    Creates a async operation that's completed successfully with the
    specified result.
    """

    async def from_result(result: _TSource) -> _TSource:
        """Async return value."""
        return result

    return from_result(result)


__all__ = [
    "Continuation",
    "empty",
    "from_continuations",
    "run_synchronously",
    "singleton",
    "sleep",
    "start",
    "start_immediate",
]
