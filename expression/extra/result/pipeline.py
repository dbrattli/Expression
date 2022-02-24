from functools import reduce
from typing import Any, Callable, TypeVar, overload

from expression.core.result import Ok, Result

_A = TypeVar("_A")
_B = TypeVar("_B")
_C = TypeVar("_C")
_D = TypeVar("_D")
_E = TypeVar("_E")
_F = TypeVar("_F")
_G = TypeVar("_G")
_TError = TypeVar("_TError")


@overload
def pipeline() -> Callable[[Any], Result[Any, Any]]:
    ...


@overload
def pipeline(
    __fn: Callable[[_A], Result[_B, _TError]]
) -> Callable[[_A], Result[_B, _TError]]:
    ...


@overload
def pipeline(
    __fn1: Callable[[_A], Result[_B, _TError]],
    __fn2: Callable[[_B], Result[_C, _TError]],
) -> Callable[[_A], Result[_C, _TError]]:
    ...


@overload
def pipeline(
    __fn1: Callable[[_A], Result[_B, _TError]],
    __fn2: Callable[[_B], Result[_C, _TError]],
    __fn3: Callable[[_C], Result[_D, _TError]],
) -> Callable[[_A], Result[_D, _TError]]:
    ...


@overload
def pipeline(
    __fn1: Callable[[_A], Result[_B, _TError]],
    __fn2: Callable[[_B], Result[_C, _TError]],
    __fn3: Callable[[_C], Result[_D, _TError]],
    __fn4: Callable[[_D], Result[_E, _TError]],
) -> Callable[[_A], Result[_E, _TError]]:
    ...


@overload
def pipeline(
    __fn1: Callable[[_A], Result[_B, _TError]],
    __fn2: Callable[[_B], Result[_C, _TError]],
    __fn3: Callable[[_C], Result[_D, _TError]],
    __fn4: Callable[[_D], Result[_E, _TError]],
    __fn5: Callable[[_E], Result[_F, _TError]],
) -> Callable[[_A], Result[_F, _TError]]:
    ...


@overload
def pipeline(
    __fn1: Callable[[_A], Result[_B, _TError]],
    __fn2: Callable[[_B], Result[_C, _TError]],
    __fn3: Callable[[_C], Result[_D, _TError]],
    __fn4: Callable[[_D], Result[_E, _TError]],
    __fn5: Callable[[_E], Result[_F, _TError]],
    __fn6: Callable[[_F], Result[_G, _TError]],
) -> Callable[[_A], Result[_G, _TError]]:
    ...


def pipeline(
    *fns: Callable[[Any], Result[Any, Any]]
) -> Callable[[Any], Result[Any, Any]]:
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
