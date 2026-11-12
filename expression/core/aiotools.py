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
from inspect import iscoroutine
from typing import Any

from expression.system import CancellationToken, ObjectDisposedException, OperationCanceledError


type Continuation[TSource] = Callable[[TSource], None]
type Callbacks[TSource] = Callable[
    [
        Continuation[TSource],
        Continuation[Exception],
        Continuation[OperationCanceledError],
    ],
    None,
]


def from_continuations[TSource](callback: Callbacks[TSource]) -> Awaitable[TSource]:
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
    future: Future[TSource] = asyncio.Future()

    def done(value: TSource) -> None:
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


def _start_task[TSource](computation: Awaitable[TSource], token: CancellationToken | None = None) -> Task[TSource]:
    async def runner() -> TSource:
        if token is not None and token.is_cancellation_requested:
            raise asyncio.CancelledError()
        return await computation

    loop = asyncio.get_running_loop()
    task = loop.create_task(runner())
    __running_tasks.add(task)
    registration = None

    def cancel() -> None:
        loop.call_soon_threadsafe(task.cancel)

    if token is not None:
        try:
            registration = token.register(cancel)
        except ObjectDisposedException:
            cancel()

    def cleanup(completed: Task[TSource]) -> None:
        __running_tasks.discard(completed)
        if registration is not None:
            registration.dispose()
        # The wrapper may be cancelled before it ever awaits the coroutine.
        if iscoroutine(computation):
            computation.close()

    task.add_done_callback(cleanup)
    return task


def start(computation: Awaitable[Any], token: CancellationToken | None = None) -> None:
    """Schedule a computation on the running event loop."""
    _start_task(computation, token)


def start_immediate(computation: Awaitable[Any], token: CancellationToken | None = None) -> None:
    """Schedule a computation on the running event loop.

    Execution begins when the event loop next runs the task.
    """
    _start_task(computation, token)


def run_synchronously[TSource](computation: Awaitable[TSource]) -> TSource:
    """Runs the asynchronous computation and await its result."""

    async def runner() -> TSource:
        return await computation

    return asyncio.run(runner())


async def singleton[TSource](value: TSource) -> TSource:
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


def from_result[TSource](result: TSource) -> Awaitable[TSource]:
    """Awaitable from result.

    Creates a async operation that's completed successfully with the
    specified result.
    """

    async def from_result(result: TSource) -> TSource:
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
