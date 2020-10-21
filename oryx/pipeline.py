from functools import reduce
from typing import Any, Awaitable, Callable

from fslash.core import Result_

from .context import Context

HttpFunc = Callable[
    [Context[Any]],
    Awaitable[Result_[Context[Any], Any]],
]

HttpHandler = Callable[
    [
        Callable[[Context[Any]], Awaitable[Result_[Context[Any], Any]]],
        Context[Any],
    ],
    Awaitable[Result_[Context[Any], Any]],
]


def pipeline(*fns: HttpHandler) -> HttpHandler:
    """Kleisli compose multiple http handlers left to right.

    Kleisli composes zero or more http handlers into a functional composition.
    The handlers are composed left to right. A composition of zero
    handlers gives back the identity handler.

    >>> pipeline()(h) ==
    >>> pipeline(f)(next, ctx) == f(next, ctx)
    >>> pipeline(f, g)(next, ctx) == g(lambda next, ctx: f(next, ctx))(next, ctx)
    >>> pipeline(f, g, h)(x) == h(lambda next, ctx: g(lambda next, ctx: f(next, ctx))(next, ctx)
    ...

    Returns:
        The kleisli composed handler.
    """

    def kleisli(next: HttpFunc, ctx: Context[Any]) -> Awaitable[Result_[Context[Any], Any]]:
        """Return a pipeline of composed handlers."""

        def reducer(first: HttpHandler, second: HttpHandler) -> HttpHandler:
            def _(next: HttpFunc, ctx: Context[Any]):
                return first(lambda c: second(next, c), ctx)

            return _

        return reduce(reducer, fns)(next, ctx)

    return kleisli


__all__ = ["pipeline"]
