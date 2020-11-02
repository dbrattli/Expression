from enum import Enum
from typing import Any, Callable, Dict, Generic, NamedTuple, Tuple, TypeVar

from aiohttp import ClientResponse, ClientSession
from expression.collections import Seq, seq
from expression.core import Nothing, Option, failwith

T = TypeVar("T")
TResult = TypeVar("TResult")
HttpContent = Dict[str, Any]


class HttpMethod(Enum):
    GET = "get"
    POST = "post"
    PUT = "put"
    DELETE = "delete"
    OPTIONS = "options"


class HttpRequest(NamedTuple):
    SessionFactory: Callable[[], ClientSession]
    Method: HttpMethod
    ContentBuilder: Option[Callable[[], HttpContent]]
    Query: Seq[Tuple[str, str]]
    # Responsetype. JSON or Protobuf
    # ResponseType: ResponseType
    # Map of headers to be sent
    Headers: Seq[Tuple[str, str]]
    UrlBuilder: Callable[[Any], str]

    def replace(self, **kw: Any) -> "HttpRequest":
        return self._replace(**kw)


class Context_(NamedTuple):
    Request: HttpRequest
    Response: Any


class Context(Context_, Generic[T]):
    Response: T

    def replace(self, **kw: Any) -> "Context[TResult]":
        return self._replace(**kw)


# This is usually the context used until we decode a fetched result into some custom result type.
HttpContext = Context[Option[ClientResponse]]


def default_session() -> ClientSession:
    return failwith("Must set HTTP session")


default_result = Nothing
default_request = HttpRequest(
    SessionFactory=default_session,
    Method=HttpMethod.GET,
    Headers=seq.empty,
    ContentBuilder=Nothing,
    Query=seq.empty,
    UrlBuilder=lambda _: failwith("Url not set"),  # type: ignore
)
default_context: HttpContext = Context(Request=default_request, Response=default_result)


def with_http_session(session: ClientSession) -> Callable[[HttpContext], HttpContext]:
    """Set the HTTP client to useH for the requests."""

    def _(context: HttpContext) -> HttpContext:
        return context.replace(Request=context.Request.replace(SessionFactory=(lambda: session)))

    return _


def with_http_session_factory(factory: Callable[[], ClientSession]) -> Callable[[HttpContext], HttpContext]:
    """Set the HTTP client factory to use for the requests."""

    def _(context: HttpContext) -> HttpContext:
        return context.replace(Request=context.Request.replace(SessionFactory=factory))

    return _
