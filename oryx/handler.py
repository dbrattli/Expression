from typing import Any, Awaitable, Callable, Dict, TypeVar

from aiohttp import ClientResponse
from expression.core import Nothing, Ok, Option, Result, option

from .context import Context, HttpContext, HttpMethod

TSource = TypeVar("TSource")
TError = TypeVar("TError")
TResult = TypeVar("TResult")
TNext = TypeVar("TNext")


# HttpFuncResult[TResult, TError]
HttpFuncResult = Result[Context[TResult], TError]
# HttpFuncResultAsync[TResult, TError]
HttpFuncResultAsync = Awaitable[Result[Context[TResult], TError]]

# HttpFunc[TNext, TResult, TError]
HttpFunc = Callable[
    [Context[TNext]],
    HttpFuncResultAsync[TResult, TError],
]

# HttpHandler[TNext, TResult, TError, TSource]
HttpHandler = Callable[
    [
        HttpFunc[TNext, TResult, TError],
        Context[TSource],
    ],
    HttpFuncResultAsync[TResult, TError],
]


async def finish_early(ctx: Context[TNext]) -> HttpFuncResult[TResult, TError]:
    return Ok(ctx)


async def run_async(
    ctx: Context[TSource],
    handler: HttpHandler[TNext, TResult, TError, TSource],
) -> Result[TResult, TError]:
    result = await handler(finish_early, ctx)

    def mapper(x: Context[TResult]) -> TResult:
        return x.Response

    return result.map(mapper)


def with_url_builder(
    builder: Callable[[Any], str]
) -> HttpHandler[Option[ClientResponse], TResult, TError, Option[ClientResponse]]:
    def _with_url_builder(
        next: HttpFunc[Option[ClientResponse], TResult, TError],
        context: HttpContext,
    ) -> HttpFuncResultAsync[TResult, TError]:
        return next(context.replace(Request=context.Request.replace(UrlBuilder=builder)))

    return _with_url_builder


def with_url(
    url: str,
) -> HttpHandler[Option[ClientResponse], TResult, TError, Option[ClientResponse]]:
    def _with_url(
        next: HttpFunc[Option[ClientResponse], TResult, TError],
        context: HttpContext,
    ) -> HttpFuncResultAsync[TResult, TError]:
        return with_url_builder(lambda _: url)(next, context)

    return _with_url


def with_method(
    method: HttpMethod,
) -> HttpHandler[Option[ClientResponse], TResult, TError, Option[ClientResponse]]:
    def _with_method(
        next: HttpFunc[Option[ClientResponse], TResult, TError],
        ctx: HttpContext,
    ) -> HttpFuncResultAsync[TResult, TError]:
        context = ctx.replace(Request=ctx.Request.replace(Method=method))
        return next(context)

    return _with_method


def GET(
    next: HttpFunc[Option[ClientResponse], TResult, TError],
    context: HttpContext,
) -> HttpFuncResultAsync[TResult, TError]:
    ctx = context.replace(Request=context.Request.replace(Method=HttpMethod.GET, ContentBuilder=Nothing))
    return next(ctx)


POST = with_method(HttpMethod.POST)
"""Http POST request."""

PUT = with_method(HttpMethod.PUT)
"""Http PUT request."""

DELETE = with_method(HttpMethod.DELETE)
"""Http DELETE request."""

OPTIONS = with_method(HttpMethod.OPTIONS)
"""Http Options request."""


async def text(
    next: HttpFunc[str, TResult, TError],
    context: HttpContext,
) -> HttpFuncResult[TResult, TError]:
    """Text decoding handler."""

    resp = context.Response
    ret: str = ""
    for resp in option.to_list(context.Response):
        ret = await resp.text()

    return await next(context.replace(Response=ret))


async def json(
    next: Callable[[Context[TSource]], Awaitable[Result[Context[TResult], TError]]],
    context: HttpContext,
) -> HttpFuncResult[TResult, TError]:
    """JSON decoding handler."""

    resp = context.Response
    ret: Dict[str, Any] = {}
    for resp in option.to_list(context.Response):
        ret = await resp.json()

    return await next(context.replace(Response=ret))
