from typing import Any, Awaitable, Callable, Dict, TypeVar

from fslash.core import Async, Nothing, Ok, Option
from fslash.core import Result_ as Result
from fslash.core import compose as compose_

from .context import Context, HttpContext, HttpMethod

TSource = TypeVar("TSource")
TError = TypeVar("TError")
TResult = TypeVar("TResult")
TNext = TypeVar("TNext")

# Generator[YieldType, SendType, ReturnType]

HttpFuncResult = Result[Context[TResult], TError]
HttpFunc = Callable[
    [Context[TSource]],
    Awaitable[Result[Context[TResult], TError]],
]

HttpHandler = Callable[
    [
        Callable[[Context[TSource]], Awaitable[Result[Context[TResult], TError]]],
        Context[TSource],
    ],
    Awaitable[Result[Context[TResult], TError]],
]


finish_early = compose_(Ok, Async.singleton)


async def run_async(
    ctx: Context[TSource],
    handler: Callable[
        [
            Callable[[Context[TSource]], Awaitable[Result[Context[TResult], TError]]],
            Context[TSource],
        ],
        Awaitable[Result[Context[TResult], TError]],
    ],
) -> Result[Context[TResult], TError]:
    result = await handler(finish_early, ctx)
    return result.map(lambda x: x.Response)


def with_url_builder(builder: Callable[[Any], str]):
    def _with_url_builder(
        next: Callable[
            [Context[TSource]],
            Awaitable[Result[Context[TResult], TError]],
        ],
        context: HttpContext,
    ):
        return next(context.replace(Request=context.Request.replace(UrlBuilder=builder)))

    return _with_url_builder


def with_url(
    url: str,
) -> Callable[
    [
        Callable[
            [Context[TSource]],
            Awaitable[Result[Context[TResult], TError]],
        ],
        Context[TSource],
    ],
    Awaitable[Result[Context[TResult], TError]],
]:
    def _with_url(
        next: Callable[
            [Context[TSource]],
            Awaitable[Result[Context[TResult], TError]],
        ],
        context: HttpContext,
    ):
        return with_url_builder(lambda _: url)(next, context)

    return _with_url


def with_method(
    method: HttpMethod,
) -> Callable[
    [
        Callable[[Context[TSource]], Awaitable[Result[Context[TResult], TError]]],
        Context[TSource],
    ],
    Awaitable[Result[Context[TResult], TError]],
]:
    def _with_method(
        next: Callable[
            [Context[TSource]],
            Awaitable[Result[Context[TResult], TError]],
        ],
        ctx: HttpContext,
    ) -> Awaitable[Result[Context[TResult], TError]]:
        context = ctx.replace(Request=ctx.Request.replace(Method=method))
        return next(context)

    return _with_method


def GET(
    next: Callable[[Context[TSource]], Awaitable[Result[Context[TResult], TError]]],
    context: HttpContext,
) -> Awaitable[Result[Context[TResult], TError]]:
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
    next: Callable[
        [Context[str]],
        Awaitable[Result[Context[TResult], TError]],
    ],
    context: HttpContext,
):
    """Text decoding handler."""

    resp = context.Response
    ret: str = ""
    for resp in Option.to_list(context.Response):
        ret = await resp.text()

    return await next(context.replace(Response=ret))


async def json(
    next: Callable[[Context[TSource]], Awaitable[Result[Context[TResult], TError]]],
    context: HttpContext,
):
    """JSON decoding handler."""

    resp = context.Response
    ret: Dict[str, Any] = {}
    for resp in Option.to_list(context.Response):
        ret = await resp.json()

    return await next(context.replace(Response=ret))
