from functools import reduce
from typing import Any, TypeVar, overload

from .context import Context
from .handler import HttpFunc, HttpFuncResultAsync, HttpHandler

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
def pipeline(__fn1: HttpHandler[T2, TResult, T1], __fn2: HttpHandler[T3, TResult, T2]) -> HttpHandler[T3, TResult, T1]:
    ...


@overload
def pipeline(
    __fn1: HttpHandler[T2, TResult, T1],
    __fn2: HttpHandler[T3, TResult, T2],
    __fn3: HttpHandler[T4, TResult, T3],
) -> HttpHandler[T4, TResult, T1]:
    ...


@overload
def pipeline(
    __fn1: HttpHandler[T2, TResult, T1],
    __fn2: HttpHandler[T3, TResult, T2],
    __fn3: HttpHandler[T4, TResult, T3],
    __fn4: HttpHandler[T5, TResult, T4],
) -> HttpHandler[T5, TResult, T1]:
    ...


@overload
def pipeline(
    __fn1: HttpHandler[T2, TResult, T1],
    __fn2: HttpHandler[T3, TResult, T2],
    __fn3: HttpHandler[T4, TResult, T3],
    __fn4: HttpHandler[T5, TResult, T4],
    __fn5: HttpHandler[T6, TResult, T5],
) -> HttpHandler[T6, TResult, T1]:
    ...


@overload
def pipeline(
    __fn1: HttpHandler[T2, TResult, T1],
    __fn2: HttpHandler[T3, TResult, T2],
    __fn3: HttpHandler[T4, TResult, T3],
    __fn4: HttpHandler[T5, TResult, T4],
    __fn5: HttpHandler[T6, TResult, T5],
    __fn6: HttpHandler[T7, TResult, T6],
) -> HttpHandler[T7, TResult, T1]:
    ...


@overload
def pipeline(
    __fn1: HttpHandler[T2, TResult, T1],
    __fn2: HttpHandler[T3, TResult, T2],
    __fn3: HttpHandler[T4, TResult, T3],
    __fn4: HttpHandler[T5, TResult, T4],
    __fn5: HttpHandler[T6, TResult, T5],
    __fn6: HttpHandler[T7, TResult, T6],
    __fn7: HttpHandler[T8, TResult, T7],
) -> HttpHandler[T8, TResult, T1]:
    ...


def pipeline(*fns: HttpHandler[Any, TResult, Any]) -> HttpHandler[Any, TResult, Any]:
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
