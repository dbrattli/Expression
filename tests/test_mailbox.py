# pyright: reportPrivateUsage=false
# Inspect task and listener registries to verify lifecycle cleanup.
import asyncio
from collections.abc import Callable
from threading import Thread
from typing import assert_type

import pytest
from hypothesis import given
from hypothesis import strategies as st

from expression import AsyncReplyChannel, MailboxProcessor
from expression.core import aiotools
from expression.system import CancellationToken, CancellationTokenSource


def int_reply_message(channel: AsyncReplyChannel[int]) -> AsyncReplyChannel[int]:
    return channel


def object_reply_message(channel: AsyncReplyChannel[object]) -> AsyncReplyChannel[object]:
    return channel


def run_in_thread(action: Callable[[], None]) -> None:
    errors: list[BaseException] = []

    def run() -> None:
        try:
            action()
        except BaseException as error:
            errors.append(error)

    thread = Thread(target=run)
    thread.start()
    thread.join(timeout=2)
    assert not thread.is_alive()
    if errors:
        raise errors[0]


@given(st.lists(st.integers()))
def test_mailbox(xs: list[int]) -> None:
    async def runner():
        result: list[int] = []

        async def process(inbox: MailboxProcessor[int]) -> None:
            for _ in xs:
                result.append(await inbox.receive())

        agent = MailboxProcessor.start(process)
        assert_type(agent, MailboxProcessor[int])
        for x in xs:
            agent.post(x)
        await agent.wait()
        assert result == xs

    asyncio.run(runner())


@pytest.mark.asyncio
@pytest.mark.parametrize("value", [None, False, 0, "", "reply"])
async def test_reply_values(value: object):
    async def process(inbox: MailboxProcessor[AsyncReplyChannel[object]]) -> None:
        channel = await inbox.receive()
        channel.reply(value)
        channel.reply("duplicate")

    agent = MailboxProcessor.start(process)
    assert await agent.post_and_async_reply(object_reply_message, timeout=1) == value
    await agent.wait()


@pytest.mark.asyncio
@pytest.mark.parametrize("wake_before_cancel", [False, True])
async def test_cancelled_receive_preserves_next_message(wake_before_cancel: bool):
    inbox: MailboxProcessor[int] = MailboxProcessor()
    pending = asyncio.create_task(inbox.receive())
    await asyncio.sleep(0)
    if wake_before_cancel:
        inbox.post(42)
        await asyncio.sleep(0)
    pending.cancel()
    if not wake_before_cancel:
        inbox.post(42)
    with pytest.raises(asyncio.CancelledError):
        await pending
    assert await inbox.receive() == 42


@pytest.mark.asyncio
async def test_receive_timeout_releases_reader():
    inbox: MailboxProcessor[int] = MailboxProcessor()
    with pytest.raises(TimeoutError):
        await inbox.receive(timeout=0)
    with pytest.raises(TimeoutError):
        await asyncio.wait_for(inbox.receive(), 0.001)
    inbox.post(42)
    assert await inbox.receive() == 42


@pytest.mark.asyncio
@pytest.mark.parametrize("wake_before_second_receive", [False, True])
async def test_concurrent_receive_rejected_without_disturbing_reader(wake_before_second_receive: bool):
    inbox: MailboxProcessor[int] = MailboxProcessor()
    first = asyncio.create_task(inbox.receive())
    await asyncio.sleep(0)
    if wake_before_second_receive:
        inbox.post(42)
        await asyncio.sleep(0)
    with pytest.raises(RuntimeError, match="Only one receive"):
        await inbox.receive()
    if not wake_before_second_receive:
        inbox.post(42)
    assert await first == 42


@pytest.mark.asyncio
async def test_token_cancels_idle_direct_receive_from_thread():
    source = CancellationTokenSource()
    inbox: MailboxProcessor[int] = MailboxProcessor(source.token)
    pending = asyncio.create_task(inbox.receive())
    await asyncio.sleep(0)
    run_in_thread(source.cancel)
    with pytest.raises(asyncio.CancelledError):
        await asyncio.wait_for(pending, 1)
    inbox.post(42)
    with pytest.raises(asyncio.CancelledError):
        await inbox.receive()
    assert inbox.messages.qsize() == 1


@pytest.mark.asyncio
async def test_post_and_reply_from_threads():
    loop = asyncio.get_running_loop()
    previous = loop.get_debug()
    loop.set_debug(True)
    try:
        inbox: MailboxProcessor[AsyncReplyChannel[int]] = MailboxProcessor()
        pending = asyncio.create_task(inbox.receive())
        await asyncio.sleep(0)
        result = inbox.post_and_async_reply(int_reply_message)
        channel = await pending
        run_in_thread(lambda: channel.reply(42))
        assert await asyncio.wait_for(result, 1) == 42
        ints: MailboxProcessor[int] = MailboxProcessor()
        pending_int = asyncio.create_task(ints.receive())
        await asyncio.sleep(0)
        run_in_thread(lambda: ints.post(7))
        assert await asyncio.wait_for(pending_int, 1) == 7
    finally:
        loop.set_debug(previous)


@pytest.mark.asyncio
async def test_late_reply_after_timeout_or_cancellation_is_ignored():
    inbox: MailboxProcessor[AsyncReplyChannel[int]] = MailboxProcessor()
    with pytest.raises(TimeoutError):
        await inbox.post_and_async_reply(int_reply_message, timeout=0)
    (await inbox.receive()).reply(1)
    result = asyncio.ensure_future(inbox.post_and_async_reply(int_reply_message))
    result.cancel()
    with pytest.raises(asyncio.CancelledError):
        await result
    (await inbox.receive()).reply(2)
    await asyncio.sleep(0)


@pytest.mark.asyncio
@pytest.mark.parametrize("cancelled", [False, True])
async def test_start_token_and_task_cleanup(cancelled: bool):
    source = CancellationTokenSource()
    entered = False
    if cancelled:
        source.cancel()

    async def body(inbox: MailboxProcessor[int]) -> None:
        nonlocal entered
        entered = True

    before = set(aiotools.__running_tasks)
    agent = MailboxProcessor.start(body, source.token if cancelled else CancellationToken.none())
    if cancelled:
        with pytest.raises(asyncio.CancelledError):
            await agent.wait()
        assert not entered
    else:
        await agent.wait()
        assert entered
    assert set(aiotools.__running_tasks) == before


@pytest.mark.asyncio
async def test_failed_body_observable_and_not_retained():
    before = set(aiotools.__running_tasks)
    source = CancellationTokenSource()

    async def body(inbox: MailboxProcessor[int]) -> None:
        raise ValueError("failure")

    agent = MailboxProcessor.start(body, source.token)
    with pytest.raises(ValueError, match="failure"):
        await agent.wait()
    assert set(aiotools.__running_tasks) == before
    assert not source._listeners


@pytest.mark.asyncio
async def test_cancel_wait_does_not_cancel_body():
    finish = asyncio.Event()

    async def body(inbox: MailboxProcessor[int]) -> None:
        await finish.wait()

    agent = MailboxProcessor.start(body)
    waiter = asyncio.create_task(agent.wait())
    await asyncio.sleep(0)
    waiter.cancel()
    with pytest.raises(asyncio.CancelledError):
        await waiter
    finish.set()
    await agent.wait()


@pytest.mark.asyncio
async def test_cancellation_cleans_up_started_body():
    source = CancellationTokenSource()
    ready = asyncio.Event()
    before = set(aiotools.__running_tasks)

    async def body(inbox: MailboxProcessor[int]) -> None:
        ready.set()
        await inbox.receive()

    agent = MailboxProcessor.start(body, source.token)
    await ready.wait()
    run_in_thread(source.cancel)
    with pytest.raises(asyncio.CancelledError):
        await agent.wait()
    assert set(aiotools.__running_tasks) == before
    assert not source._listeners


@pytest.mark.asyncio
async def test_wait_requires_started_mailbox():
    inbox: MailboxProcessor[int] = MailboxProcessor()
    with pytest.raises(RuntimeError, match="not been started"):
        await inbox.wait()
