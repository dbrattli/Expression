(reference_mailbox)=

# Mailbox

`MailboxProcessor` provides a FIFO queue with one active receiver and multiple
producers. Create the mailbox and call `receive`, `post_and_async_reply`, and
`wait` on its owning running asyncio event loop. `post` and reply channels may
be used from other threads.

```python
import asyncio

from expression import AsyncReplyChannel, MailboxProcessor


async def main() -> None:
    async def body(inbox: MailboxProcessor[AsyncReplyChannel[None]]) -> None:
        channel = await inbox.receive(timeout=1.0)
        channel.reply(None)

    agent = MailboxProcessor.start(body)
    def request(channel: AsyncReplyChannel[None]) -> AsyncReplyChannel[None]:
        return channel

    await agent.post_and_async_reply(request, timeout=1.0)
    await agent.wait()


asyncio.run(main())
```

Timeouts are optional and measured in **seconds**, following asyncio conventions.
An expired timeout raises `TimeoutError`. Cancelling or timing out a receive
releases the reader without consuming a message. Concurrent receives raise
`RuntimeError`.

`post_and_async_reply` posts immediately. The first reply wins, including `None`;
duplicate replies and replies arriving after cancellation or timeout are ignored.
Cancelling a reply wait does not retract the request or stop its processing.
Without a timeout, a request that is never answered can wait indefinitely.

A cancellation token wakes an idle receiver and cancels a started body. An
already-cancelled token prevents the body coroutine from running, while
`CancellationToken.none()` behaves like an omitted token. `wait()` observes body
completion and propagates its exception or `asyncio.CancelledError`. Cancelling
`wait()` itself leaves the body running. A directly constructed mailbox has no
body to wait for.

Body termination does not close the queue or settle outstanding reply waits.
Use reply timeouts and observe `wait()` when coordinating shutdown. The queue is
unbounded; posting does not provide backpressure. This is a subset of F#'s
MailboxProcessor API: selective scanning and optional-result receive/reply
variants are not provided.

```{eval-rst}
.. automodule:: expression.core.mailbox
    :members:
```
