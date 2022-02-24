from functools import reduce
from typing import Any, Callable, TypeVar, overload

from expression.core import Option, Some

_A = TypeVar("_A")
_B = TypeVar("_B")
_C = TypeVar("_C")
_D = TypeVar("_D")
_E = TypeVar("_E")
_F = TypeVar("_F")
_G = TypeVar("_G")
_TError = TypeVar("_TError")


@overload
def pipeline() -> Callable[[_A], Option[_A]]:
    ...


@overload
def pipeline(__fn: Callable[[_A], Option[_B]]) -> Callable[[_A], Option[_B]]:
    ...


@overload
def pipeline(
    __fn1: Callable[[_A], Option[_B]], __fn2: Callable[[_B], Option[_C]]
) -> Callable[[_A], Option[_C]]:
    ...


@overload
def pipeline(
    __fn1: Callable[[_A], Option[_B]],
    __fn2: Callable[[_B], Option[_C]],
    __fn3: Callable[[_C], Option[_D]],
) -> Callable[[_A], Option[_D]]:
    ...


@overload
def pipeline(
    __fn1: Callable[[_A], Option[_B]],
    __fn2: Callable[[_B], Option[_C]],
    __fn3: Callable[[_C], Option[_D]],
    __fn4: Callable[[_D], Option[_E]],
) -> Callable[[_A], Option[_E]]:
    ...


@overload
def pipeline(
    __fn1: Callable[[_A], Option[_B]],
    __fn2: Callable[[_B], Option[_C]],
    __fn3: Callable[[_C], Option[_D]],
    __fn4: Callable[[_D], Option[_E]],
    __fn5: Callable[[_E], Option[_F]],
) -> Callable[[_A], Option[_F]]:
    ...


@overload
def pipeline(
    __fn1: Callable[[_A], Option[_B]],
    __fn2: Callable[[_B], Option[_C]],
    __fn3: Callable[[_C], Option[_D]],
    __fn4: Callable[[_D], Option[_E]],
    __fn5: Callable[[_E], Option[_F]],
    __fn6: Callable[[_F], Option[_G]],
) -> Callable[[_A], Option[_G]]:
    ...


def pipeline(*fns: Callable[[Any], Option[Any]]) -> Callable[[Any], Option[Any]]:
    """pipeline multiple option returning functions left to right.

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

    def reducer(
        acc: Callable[[Any], Option[Any]], fn: Callable[[Any], Option[Any]]
    ) -> Callable[[Any], Option[Any]]:
        def gn(x: Any) -> Option[Any]:
            return acc(x).bind(fn)

        return gn

    return reduce(reducer, fns, Some)


__all__ = ["pipeline"]
