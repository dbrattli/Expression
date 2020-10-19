from typing import Callable, Any, TypeVar, overload
from functools import reduce

from fslash.core.option import Option


A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")
D = TypeVar("D")
E = TypeVar("E")
F = TypeVar("F")
G = TypeVar("G")
TError = TypeVar("TError")


@overload
def kleisli() -> Callable[[A], A]:
    ...


@overload
def kleisli(__fn: Callable[[A], Option[B]]) -> Callable[[A], Option[B]]:
    ...


@overload
def kleisli(__fn1: Callable[[A], Option[B]], __fn2: Callable[[B], Option[C]]) -> Callable[[A], Option[C]]:
    ...


@overload
def kleisli(
    __fn1: Callable[[A], Option[B]], __fn2: Callable[[B], Option[C]], __fn3: Callable[[C], Option[D]]
) -> Callable[[A], Option[D]]:
    ...


@overload
def kleisli(
    __fn1: Callable[[A], Option[B]],
    __fn2: Callable[[B], Option[C]],
    __fn3: Callable[[C], Option[D]],
    __fn4: Callable[[D], Option[E]],
) -> Callable[[A], Option[E]]:
    ...


@overload
def kleisli(
    __fn1: Callable[[A], Option[B]],
    __fn2: Callable[[B], Option[C]],
    __fn3: Callable[[C], Option[D]],
    __fn4: Callable[[D], Option[E]],
    __fn5: Callable[[E], Option[F]],
) -> Callable[[A], Option[F]]:
    ...


@overload
def kleisli(
    __fn1: Callable[[A], Option[B]],
    __fn2: Callable[[B], Option[C]],
    __fn3: Callable[[C], Option[D]],
    __fn4: Callable[[D], Option[E]],
    __fn5: Callable[[E], Option[F]],
    __fn6: Callable[[F], Option[G]],
) -> Callable[[A], Option[G]]:
    ...


def kleisli(*fns: Callable) -> Callable:
    """Kleisli (>=>) compose multiple option returning functions left
    to right.

    Kleisli composes zero or more functions into a functional
    composition. The functions are composed left to right. A composition
    of zero functions gives back the identity function.

    >>> kleisli()(x) == x
    >>> kleisli(f)(x) == f(x)
    >>> kleisli(f, g)(x) == g(f(x))
    >>> kleisli(f, g, h)(x) == h(g(f(x)))
    ...

    Returns:
        The composed functions.
    """

    def _kleisli(source: Any) -> Any:
        def reducer(acc, fn):
            return fn(acc.value) if acc.is_some() else acc

        return reduce(reducer, fns, source)

    return _kleisli


__all__ = ["kleisli"]
