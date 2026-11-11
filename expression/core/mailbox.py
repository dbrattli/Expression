# Attribution to original authors of this code
# --------------------------------------------
# This code has been originally ported from the Fable project (https://fable.io)
# Copyright (c) Alfonso García-Caro and contributors.
#
# The original code was authored by
# - Alfonso Garcia-Caro (https://github.com/alfonsogarciacaro)
# - ncave (https://github.com/ncave)
#
# You can find the original implementation here:
# - https://github.com/fable-compiler/Fable/blob/nagareyama/src/fable-library/MailboxProcessor.ts

from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator, Awaitable, Callable
from contextlib import asynccontextmanager
from queue import Empty, SimpleQueue
from typing import Generic, TypeVar

from expression.system import CancellationToken, ObjectDisposedException

from .aiotools import _start_task  # pyright: ignore[reportPrivateUsage]


_Msg = TypeVar("_Msg")
_Reply = TypeVar("_Reply")
_StartedMsg = TypeVar("_StartedMsg")


class AsyncReplyChannel(Generic[_Reply]):
    def __init__(self, fn: Callable[[_Reply], None]) -> None:
        self.fn = fn

    def reply(self, r: _Reply) -> None:
        self.fn(r)


class MailboxProcessor(Generic[_Msg]):
    """A FIFO mailbox with one reader and thread-safe posting and replies.

    Construct and receive on the same running event loop. Timeouts use seconds,
    as in asyncio. Cancelling a reply wait does not retract its posted message.
    """

    def __init__(self, cancellation_token: CancellationToken | None = None) -> None:
        self.messages: SimpleQueue[_Msg] = SimpleQueue()
        self.token = cancellation_token or CancellationToken.none()
        self.loop = asyncio.get_running_loop()
        # Presence owns the reader slot, even after the signal completes.
        self._receive_signal: asyncio.Future[None] | None = None
        self._task: asyncio.Task[None] | None = None

    def _check_loop(self) -> None:
        if asyncio.get_running_loop() is not self.loop:
            raise RuntimeError("Mailbox operations must run on the owning event loop")

    def _wake(self) -> None:
        if self._receive_signal is not None and not self._receive_signal.done():
            self._receive_signal.set_result(None)

    def post(self, msg: _Msg) -> None:
        """Post a message synchronously, including from another thread."""
        if self.loop.is_closed():
            raise RuntimeError("Mailbox event loop is closed")
        self.messages.put(msg)
        self.loop.call_soon_threadsafe(self._wake)

    def post_and_async_reply(
        self, build_message: Callable[[AsyncReplyChannel[_Reply]], _Msg], timeout: float | None = None
    ) -> Awaitable[_Reply]:
        """Post immediately and await a reply, optionally timing out in seconds.

        The first reply wins, including None. Replies may come from any thread;
        late replies after cancellation or timeout are ignored.
        """
        self._check_loop()
        future: asyncio.Future[_Reply] = self.loop.create_future()

        def complete(value: _Reply) -> None:
            if not future.done():
                future.set_result(value)

        def reply(value: _Reply) -> None:
            if not self.loop.is_closed():
                self.loop.call_soon_threadsafe(complete, value)

        self.post(build_message(AsyncReplyChannel(reply)))
        if timeout is None:
            return future
        return asyncio.wait_for(future, timeout)

    async def receive(self, timeout: float | None = None) -> _Msg:
        """Receive the next message; raise TimeoutError after timeout seconds.

        Only one receive may be active. Cancellation or timeout releases the
        reader without consuming a message. Token cancellation raises
        asyncio.CancelledError, including when messages are already queued.
        """
        async with self._receive_scope(timeout) as signal:
            while True:
                if self.token.is_cancellation_requested:
                    raise asyncio.CancelledError()
                try:
                    return self.messages.get_nowait()
                except Empty:
                    await signal
                    signal = self.loop.create_future()
                    self._receive_signal = signal

    @asynccontextmanager
    async def _receive_scope(self, timeout: float | None) -> AsyncGenerator[asyncio.Future[None], None]:
        """Own the single reader and release its resources on every exit path."""
        self._check_loop()
        if self._receive_signal is not None:
            raise RuntimeError("Only one receive may be active at a time")
        signal: asyncio.Future[None] = self.loop.create_future()
        self._receive_signal = signal
        registration = None

        def wake() -> None:
            self.loop.call_soon_threadsafe(self._wake)

        try:
            try:
                registration = self.token.register(wake)
            except ObjectDisposedException:
                # Cancellation may win the race with listener registration.
                raise asyncio.CancelledError() from None
            async with asyncio.timeout(timeout):
                yield signal
        finally:
            self._receive_signal = None
            if registration is not None:
                registration.dispose()

    async def wait(self) -> None:
        """Await body termination and propagate its failure or cancellation.

        Cancelling this wait does not cancel the body. A directly constructed
        mailbox has no body and cannot be waited on.
        """
        self._check_loop()
        if self._task is None:
            raise RuntimeError("Mailbox has not been started")
        await asyncio.shield(self._task)

    @staticmethod
    def start(
        body: Callable[[MailboxProcessor[_StartedMsg]], Awaitable[None]],
        cancellation_token: CancellationToken | None = None,
    ) -> MailboxProcessor[_StartedMsg]:
        """Start a body whose completion can be observed with wait()."""
        mbox: MailboxProcessor[_StartedMsg] = MailboxProcessor(cancellation_token)
        mbox._task = _start_task(body(mbox), cancellation_token)
        return mbox


__all__ = ["AsyncReplyChannel", "MailboxProcessor"]
