import asyncio
from typing import Callable, List, Tuple

from hypothesis import given  # type: ignore
from hypothesis import strategies as st

from expression import AsyncReplyChannel, MailboxProcessor


@given(st.lists(st.integers()))  # type: ignore
def test_mailbox(xs: List[int]) -> None:
    result: List[int] = []

    async def runner():
        async def process(inbox: MailboxProcessor[int]) -> None:
            """the message processing function."""

            async def message_loop() -> None:
                msg: int = await inbox.receive()
                result.append(msg)

                return await message_loop()

            return await message_loop()  # start the loop

        agent = MailboxProcessor.start(process)
        for x in xs:
            agent.post(x)
        await asyncio.sleep(0)

    asyncio.run(runner())

    assert result == xs


@given(st.integers())  # type: ignore
def test_mailbox_post_and_async_reply(x: int):
    async def runner():
        async def process(
            inbox: MailboxProcessor[Tuple[int, AsyncReplyChannel[str]]]
        ) -> None:
            """the message processing function."""

            async def message_loop() -> None:
                msg, rc = await inbox.receive()
                rc.reply(f"Got {msg}")

                return await message_loop()

            # start the loop
            return await message_loop()

        agent: MailboxProcessor[
            Tuple[int, AsyncReplyChannel[str]]
        ] = MailboxProcessor.start(process)
        build_message: Callable[
            [AsyncReplyChannel[str]], Tuple[int, AsyncReplyChannel[str]]
        ] = lambda r: (x, r)
        reply = await agent.post_and_async_reply(build_message)

        assert reply == f"Got {x}"

    asyncio.run(runner())
