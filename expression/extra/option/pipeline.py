from collections.abc import Callable
from functools import reduce
from typing import Any, overload

from expression.core import Option, Some


@overload
def pipeline[A]() -> Callable[[A], Option[A]]: ...


@overload
def pipeline[A, B](__fn: Callable[[A], Option[B]]) -> Callable[[A], Option[B]]: ...


@overload
def pipeline[A, B, C](__fn1: Callable[[A], Option[B]], __fn2: Callable[[B], Option[C]]) -> Callable[[A], Option[C]]: ...


@overload
def pipeline[A, B, C, D](
    __fn1: Callable[[A], Option[B]],
    __fn2: Callable[[B], Option[C]],
    __fn3: Callable[[C], Option[D]],
) -> Callable[[A], Option[D]]: ...


@overload
def pipeline[A, B, C, D, E](
    __fn1: Callable[[A], Option[B]],
    __fn2: Callable[[B], Option[C]],
    __fn3: Callable[[C], Option[D]],
    __fn4: Callable[[D], Option[E]],
) -> Callable[[A], Option[E]]: ...


@overload
def pipeline[A, B, C, D, E, F](
    __fn1: Callable[[A], Option[B]],
    __fn2: Callable[[B], Option[C]],
    __fn3: Callable[[C], Option[D]],
    __fn4: Callable[[D], Option[E]],
    __fn5: Callable[[E], Option[F]],
) -> Callable[[A], Option[F]]: ...


@overload
def pipeline[A, B, C, D, E, F, G](
    __fn1: Callable[[A], Option[B]],
    __fn2: Callable[[B], Option[C]],
    __fn3: Callable[[C], Option[D]],
    __fn4: Callable[[D], Option[E]],
    __fn5: Callable[[E], Option[F]],
    __fn6: Callable[[F], Option[G]],
) -> Callable[[A], Option[G]]: ...


def pipeline(*fns: Callable[[Any], Option[Any]]) -> Callable[[Any], Option[Any]]:
    """Pipeline multiple option returning functions left to right.

    A pipeline kleisli (>=>) composes zero or more functions into a
    functional composition. The functions are composed left to right. A
    composition of zero functions gives back the identity function.

    >>> pipeline()(x) == Some(x)
    >>> pipeline(f)(x) == f(x)
    >>> pipeline(f, g)(x) == f(x).bind(g)
    >>> pipeline(f, g, h)(x) == f(x).bind(g).bind(h)
    ...

    Returns:
        The composed functions.
    """

    def reducer(acc: Callable[[Any], Option[Any]], fn: Callable[[Any], Option[Any]]) -> Callable[[Any], Option[Any]]:
        def gn(x: Any) -> Option[Any]:
            return acc(x).bind(fn)

        return gn

    return reduce(reducer, fns, Some)


__all__ = ["pipeline"]
