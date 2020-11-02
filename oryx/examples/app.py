import asyncio

import aiohttp
from expression.core import pipe
from oryx.context import default_context, with_http_session
from oryx.fetch import fetch
from oryx.handler import GET, run_async, text, with_url
from oryx.pipeline import pipeline


async def main():
    async with aiohttp.ClientSession() as session:
        ctx = pipe(default_context, with_http_session(session))

        request = pipeline(
            GET,
            with_url("https://www.vg.no"),
            fetch,
            text,
        )

        result = await run_async(ctx, request)
        for output in result:
            print(output)


if __name__ == "__main__":
    asyncio.run(main())
