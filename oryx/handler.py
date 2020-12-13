from typing import Any, Awaitable, Callable, Dict, Protocol, TypeVar, cast

from aiohttp import ClientResponse
from expression.core import Nothing, Option, Success, Try, aiotools, compose, match, option

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

finish_early = cast(HttpFunc[Any, Any], compose(Success, aiotools.from_result))


class HttpHandlerFn(Protocol[TSource, TNext]):
    def __call__(self, __next: HttpFunc[TNext, TResult], __context: Context[TSource]) -> HttpFuncResultAsync[TResult]:
        raise NotImplementedError


async def run_async(
    ctx: Context[TSource],
    handler: HttpHandler[TNext, TResult, TSource],
) -> Try[TResult]:
    result = await handler(finish_early, ctx)

    def mapper(x: Context[TResult]) -> TResult:
        return x.Response

    return result.map(mapper)


def with_url_builder(builder: Callable[[Any], str]) -> HttpHandlerFn[Option[ClientResponse], Option[ClientResponse]]:
    def _with_url_builder(
        next: HttpFunc[Option[ClientResponse], TResult],
        context: HttpContext,
    ) -> HttpFuncResultAsync[TResult]:
        return next(context.replace(Request=context.Request.replace(UrlBuilder=builder)))

    return _with_url_builder


def with_url(
    url: str,
) -> HttpHandlerFn[Option[ClientResponse], Option[ClientResponse]]:
    return with_url_builder(lambda _: url)


def with_method(
    method: HttpMethod,
) -> HttpHandlerFn[Option[ClientResponse], Option[ClientResponse]]:
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
    with match(context.Response) as case:
        for resp in case(Success[ClientResponse]):
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
