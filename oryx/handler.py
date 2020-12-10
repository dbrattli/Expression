from typing import Any, Awaitable, Callable, Dict, TypeVar

from aiohttp import ClientResponse
from expression.core import Nothing, Option, Success, Try, aiotools, compose, option

from .context import Context, HttpContext, HttpMethod

TSource = TypeVar("TSource")
TResult = TypeVar("TResult")
TNext = TypeVar("TNext")


# HttpFuncResult[TResult]
HttpFuncResult = Try[Context[TResult]]
# HttpFuncResultAsync[TResult]
HttpFuncResultAsync = Awaitable[Try[Context[TResult]]]

# HttpFunc[TNext, TResult]
HttpFunc = Callable[
    [Context[TNext]],
    HttpFuncResultAsync[TResult],
]

# HttpHandler[TNext, TResult, TSource]
HttpHandler = Callable[
    [
        HttpFunc[TNext, TResult],
        Context[TSource],
    ],
    HttpFuncResultAsync[TResult],
]

finish_early: HttpFunc[Any, Any] = compose(Success, aiotools.from_result)


async def run_async(
    ctx: Context[TSource],
    handler: HttpHandler[TNext, TResult, TSource],
) -> Try[TResult]:
    next: Callable[[Context[TResult]], HttpFuncResultAsync[TResult]] = finish_early
    result = await handler(next, ctx)

    def mapper(x: Context[TResult]) -> TResult:
        return x.Response

    return result.map(mapper)


def with_url_builder(
    builder: Callable[[Any], str]
) -> HttpHandler[Option[ClientResponse], TResult, Option[ClientResponse]]:
    def _with_url_builder(
        next: HttpFunc[Option[ClientResponse], TResult],
        context: HttpContext,
    ) -> HttpFuncResultAsync[TResult]:
        return next(context.replace(Request=context.Request.replace(UrlBuilder=builder)))

    return _with_url_builder


def with_url(
    url: str,
) -> HttpHandler[Option[ClientResponse], TResult, Option[ClientResponse]]:
    def _with_url(
        next: HttpFunc[Option[ClientResponse], TResult],
        context: HttpContext,
    ) -> HttpFuncResultAsync[TResult]:
        fn = with_url_builder(lambda _: url)
        ret: HttpFuncResultAsync[TResult] = fn(next, context)
        return ret

    return _with_url


def with_method(
    method: HttpMethod,
) -> HttpHandler[Option[ClientResponse], TResult, Option[ClientResponse]]:
    def _with_method(
        next: HttpFunc[Option[ClientResponse], TResult],
        ctx: HttpContext,
    ) -> HttpFuncResultAsync[TResult]:
        context: HttpContext = ctx.replace(Request=ctx.Request.replace(Method=method))
        return next(context)

    return _with_method


def GET(
    next: HttpFunc[Option[ClientResponse], TResult],
    context: HttpContext,
) -> HttpFuncResultAsync[TResult]:
    ctx: HttpContext = context.replace(Request=context.Request.replace(Method=HttpMethod.GET, ContentBuilder=Nothing))
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
    next: HttpFunc[str, TResult],
    context: HttpContext,
) -> HttpFuncResult[TResult]:
    """Text decoding handler."""

    resp = context.Response
    ret: str = ""
    for resp in option.to_list(context.Response):
        ret = await resp.text()

    return await next(context.replace(Response=ret))


async def json(
    next: Callable[[Context[TSource]], Awaitable[Try[Context[TResult]]]],
    context: HttpContext,
) -> HttpFuncResult[TResult]:
    """JSON decoding handler."""

    resp = context.Response
    ret: Dict[str, Any] = {}
    for resp in option.to_list(context.Response):
        ret = await resp.json()

    return await next(context.replace(Response=ret))
