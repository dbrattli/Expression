from typing import Callable, Any, TypeVar, overload, cast
from functools import reduce

from expression.core.result import Result, Ok


A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")
D = TypeVar("D")
E = TypeVar("E")
F = TypeVar("F")
G = TypeVar("G")
TError = TypeVar("TError")


@overload
def pipeline() -> Callable[[A], A]:
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
) -> Callable[[A], D]:
    ...


@overload
def pipeline(
    __fn1: Callable[[A], Result[B, TError]],
    __fn2: Callable[[B], Result[C, TError]],
    __fn3: Callable[[C], Result[D, TError]],
    __fn4: Callable[[D], Result[E, TError]],
) -> Callable[[A], E]:
    ...


@overload
def pipeline(
    __fn1: Callable[[A], Result[B, TError]],
    __fn2: Callable[[B], Result[C, TError]],
    __fn3: Callable[[C], Result[D, TError]],
    __fn4: Callable[[D], Result[E, TError]],
    __fn5: Callable[[E], Result[F, TError]],
) -> Callable[[A], F]:
    ...


@overload
def pipeline(
    __fn1: Callable[[A], Result[B, TError]],
    __fn2: Callable[[B], Result[C, TError]],
    __fn3: Callable[[C], Result[D, TError]],
    __fn4: Callable[[D], Result[E, TError]],
    __fn5: Callable[[E], Result[F, TError]],
    __fn6: Callable[[F], Result[G, TError]],
) -> Callable[[A], G]:
    ...


def pipeline(*fns: Callable[[Any], Result[Any, Any]]) -> Callable[[Any], Result[Any, Any]]:
    """pipeline multiple result returning functions left to right.

    A pipeline kleisli (>=>) composes zero or more functions into a
    functional composition. The functions are composed left to right. A
    composition of zero functions gives back the identity function.

    >>> pipeline()(x) == x
    >>> pipeline(f)(x) == f(x)
    >>> pipeline(f, g)(x) == g(f(x))
    >>> pipeline(f, g, h)(x) == h(g(f(x)))
    ...

    Returns:
        The composed functions.
    """

    def kleisli(source: Any) -> Result[Any, Any]:
        def reducer(acc: Result[Any, Any], fn: Callable[[Any], Result[Any, Any]]):
            return fn(cast(Ok[Any, Any], acc).value) if acc.is_ok() else acc

        return reduce(reducer, fns, source)

    return kleisli


__all__ = ["pipeline"]
