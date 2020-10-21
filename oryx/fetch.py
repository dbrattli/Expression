from typing import Any, Awaitable, Callable, TypeVar

from fslash.core import Error, Option, Option_, Result_, Some, pipe

from .context import Context, HttpContent
from .handler import HttpContext

TSource = TypeVar("TSource")
TError = TypeVar("TError")
TResult = TypeVar("TResult")
TNext = TypeVar("TNext")


async def fetch(
    next: Callable[[Context[TSource]], Awaitable[Result_[Context[TResult], TError]]],
    ctx: HttpContext,
) -> Result_[Context[TResult], TError]:
    session = ctx.Request.SessionFactory()
    builder: Callable[[Any], HttpContent] = lambda builder: builder()

    result: Result_[Context[TResult], TError]
    try:
        content: Option_[Any] = pipe(ctx.Request.ContentBuilder, Option.map(builder))
        json = pipe(content, Option.default_value(None))
        method = ctx.Request.Method.value
        url = ctx.Request.UrlBuilder(ctx)

        print(f"Fetching: {url}")
        async with session.request(method=method, url=url, json=json) as resp:
            result = await next(ctx.replace(Response=Some(resp)))
    except Exception as ex:
        print(f"fetch: {ex}")
        result = Error(ex)

    return result
