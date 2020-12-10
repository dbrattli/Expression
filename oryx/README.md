Oryx is a high performance functional HTTP request handler library for writing HTTP clients and orchestrating web
requests in Python.

> An SDK for writing HTTP clients and orchestrating web requests.

This library enables you to write Web and REST clients and SDKs for various APIs.

Oryx is a port [Oryx for F#](https://github.com/cognitedata/oryx) and is heavily inspired by the
[Giraffe](https://github.com/giraffe-fsharp/Giraffe) web framework, and applies the same ideas to the client making the
web requests. You can think of Oryx as the client equivalent of Giraffe, and you could envision the HTTP request
processing pipeline starting at the client and going all the way to the server and back again.

```py
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

```

([source code](https://github.com/cognitedata/Expression/blob/main/oryx/examples/app.py))