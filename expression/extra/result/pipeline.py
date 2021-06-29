from functools import reduce
from typing import Any, Callable, TypeVar, overload

from expression.core.result import Ok, Result

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")
D = TypeVar("D")
E = TypeVar("E")
F = TypeVar("F")
G = TypeVar("G")
TError = TypeVar("TError")


@overload
def pipeline() -> Callable[[Any], Result[Any, Any]]:
    ...


@overload
def pipeline(__fn: Callable[[A], Result[B, TError]]) -> Callable[[A], Result[B, TError]]:
    ...


@overload
def pipeline(
    __fn1: Callable[[A], Result[B, TError]], __fn2: Callable[[B], Result[C, TError]]
) -> Callable[[A], Result[C, TError]]:
    ...


@overload
def pipeline(
    __fn1: Callable[[A], Result[B, TError]],
    __fn2: Callable[[B], Result[C, TError]],
    __fn3: Callable[[C], Result[D, TError]],
) -> Callable[[A], Result[D, TError]]:
    ...


@overload
def pipeline(
    __fn1: Callable[[A], Result[B, TError]],
    __fn2: Callable[[B], Result[C, TError]],
    __fn3: Callable[[C], Result[D, TError]],
    __fn4: Callable[[D], Result[E, TError]],
) -> Callable[[A], Result[E, TError]]:
    ...


@overload
def pipeline(
    __fn1: Callable[[A], Result[B, TError]],
    __fn2: Callable[[B], Result[C, TError]],
    __fn3: Callable[[C], Result[D, TError]],
    __fn4: Callable[[D], Result[E, TError]],
    __fn5: Callable[[E], Result[F, TError]],
) -> Callable[[A], Result[F, TError]]:
    ...


@overload
def pipeline(
    __fn1: Callable[[A], Result[B, TError]],
    __fn2: Callable[[B], Result[C, TError]],
    __fn3: Callable[[C], Result[D, TError]],
    __fn4: Callable[[D], Result[E, TError]],
    __fn5: Callable[[E], Result[F, TError]],
    __fn6: Callable[[F], Result[G, TError]],
) -> Callable[[A], Result[G, TError]]:
    ...


def pipeline(*fns: Callable[[Any], Result[Any, Any]]) -> Callable[[Any], Result[Any, Any]]:  # type: ignore
    """pipeline multiple result returning functions left to right.

    A pipeline kleisli (>=>) composes zero or more functions into a
    functional composition. The functions are composed left to right. A
    composition of zero functions gives back the identity function.

    >>> pipeline()(x) == Ok(x)
    >>> pipeline(f)(x) == f(x)
    >>> pipeline(f, g)(x) == f(x).bind(g)
    >>> pipeline(f, g, h)(x) == f(x).bind(g).bind(h)
    ...

    Returns:
        The composed functions.
    """

    def reducer(
        acc: Callable[[Any], Result[Any, Any]], fn: Callable[[Any], Result[Any, Any]]
    ) -> Callable[[Any], Result[Any, Any]]:
        def gn(x: Any) -> Result[Any, Any]:
            return acc(x).bind(fn)

        return gn

    return reduce(reducer, fns, Ok)


__all__ = ["pipeline"]
