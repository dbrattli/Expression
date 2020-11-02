from typing import Any, Callable, TypeVar

from aiohttp import ClientResponse
from expression.core import Error, Option, Result, Some, option, pipe

from .context import Context, HttpContent, HttpContext
from .handler import HttpFunc, HttpFuncResult

TSource = TypeVar("TSource")
TError = TypeVar("TError")
TResult = TypeVar("TResult")
TNext = TypeVar("TNext")


async def fetch(
    next: HttpFunc[Option[ClientResponse], TResult, TError],
    ctx: HttpContext,
) -> Result[Context[TResult], TError]:
    session = ctx.Request.SessionFactory()
    builder: Callable[[Any], HttpContent] = lambda builder: builder()

    result: HttpFuncResult
    try:
        content: Option[Any] = pipe(ctx.Request.ContentBuilder, option.map(builder))
        json = pipe(content, option.default_value(None))
        method = ctx.Request.Method.value
        url = ctx.Request.UrlBuilder(ctx)

        print(f"Fetching: {url}")
        async with session.request(method=method, url=url, json=json) as resp:
            result = await next(ctx.replace(Response=Some(resp)))
    except Exception as ex:
        print(f"fetch: {ex}")
        result = Error(ex)

    return result
