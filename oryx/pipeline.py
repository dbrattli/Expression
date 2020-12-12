from functools import reduce
from typing import Any, TypeVar, overload

from aiohttp import ClientResponse
from expression.core import Option

from .context import Context
from .handler import HttpFunc, HttpFuncResultAsync, HttpHandler, HttpHandlerFn

T1 = TypeVar("T1")
T2 = TypeVar("T2")
T3 = TypeVar("T3")
T4 = TypeVar("T4")
T5 = TypeVar("T5")
T6 = TypeVar("T6")
T7 = TypeVar("T7")
T8 = TypeVar("T8")
TError = TypeVar("TError")
TResult = TypeVar("TResult")


@overload
def pipeline(
    __fn: HttpHandlerFn[Option[ClientResponse], T2],
) -> HttpHandlerFn[Option[ClientResponse], T2]:
    ...


@overload
def pipeline(
    __fn1: HttpHandlerFn[Option[ClientResponse], T2],
    __fn2: HttpHandlerFn[T2, T3],
) -> HttpHandlerFn[Option[ClientResponse], T3]:
    ...


@overload
def pipeline(
    __fn1: HttpHandlerFn[Option[ClientResponse], T2],
    __fn2: HttpHandlerFn[T2, T3],
    __fn3: HttpHandlerFn[T3, T4],
) -> HttpHandlerFn[Option[ClientResponse], T4]:
    ...


@overload
def pipeline(
    __fn1: HttpHandlerFn[Option[ClientResponse], T2],
    __fn2: HttpHandlerFn[T2, T3],
    __fn3: HttpHandlerFn[T3, T4],
    __fn4: HttpHandlerFn[T4, T5],
) -> HttpHandlerFn[Option[ClientResponse], T5]:
    ...


@overload
def pipeline(
    __fn1: HttpHandlerFn[Option[ClientResponse], T2],
    __fn2: HttpHandlerFn[T2, T3],
    __fn3: HttpHandlerFn[T3, T4],
    __fn4: HttpHandlerFn[T4, T5],
    __fn5: HttpHandlerFn[T5, T6],
) -> HttpHandlerFn[Option[ClientResponse], T6]:
    ...


@overload
def pipeline(
    __fn1: HttpHandlerFn[Option[ClientResponse], T2],
    __fn2: HttpHandlerFn[T2, T3],
    __fn3: HttpHandlerFn[T3, T4],
    __fn4: HttpHandlerFn[T4, T5],
    __fn5: HttpHandlerFn[T5, T6],
    __fn6: HttpHandlerFn[T6, T7],
) -> HttpHandlerFn[Option[ClientResponse], T7]:
    ...


@overload
def pipeline(
    __fn1: HttpHandlerFn[Option[ClientResponse], T2],
    __fn2: HttpHandlerFn[T2, T3],
    __fn3: HttpHandlerFn[T3, T4],
    __fn4: HttpHandlerFn[T4, T5],
    __fn5: HttpHandlerFn[T5, T6],
    __fn6: HttpHandlerFn[T6, T7],
    __fn7: HttpHandlerFn[T7, T8],
) -> HttpHandlerFn[Option[ClientResponse], T8]:
    ...


def pipeline(*fns: HttpHandlerFn[Any, Any]) -> HttpHandlerFn[Any, Any]:
    """Kleisli compose multiple http handlers left to right.

    Kleisli composes zero or more http handlers into a functional composition.
    The handlers are composed left to right. A composition of zero
    handlers gives back the identity handler.

    >>> pipeline()(h) ==
    >>> pipeline(f)(next, ctx) == f(next, ctx)
    >>> pipeline(f, g)(next, ctx) == g(lambda next, ctx: f(next, ctx))(next, ctx)
    >>> pipeline(f, g, h)(next, ctx) == h(lambda next, ctx: g(lambda next, ctx: f(next, ctx))(next, ctx)
    ...

    Returns:
        The kleisli composed handler.
    """

    def kleisli(next: HttpFunc[Any, TResult], ctx: Context[Any]) -> HttpFuncResultAsync[TResult]:
        """Return a pipeline of composed handlers."""

        def reducer(
            first: HttpHandler[Any, TResult, Any], second: HttpHandler[Any, TResult, Any]
        ) -> HttpHandler[Any, TResult, Any]:
            def _(next: HttpFunc[Any, TResult], ctx: Context[Any]):
                return first(lambda c: second(next, c), ctx)

            return _

        return reduce(reducer, fns)(next, ctx)

    return kleisli


__all__ = ["pipeline"]
