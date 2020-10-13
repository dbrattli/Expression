from typing import Callable, Any, TypeVar, overload
from functools import reduce

from fslash.core.result import Result


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
def kleisli(fn: Callable[[A], Result[B, TError]]) -> Callable[[A], Result[B, TError]]:
    ...


@overload
def kleisli(
    fn1: Callable[[A], Result[B, TError]], fn2: Callable[[B], Result[C, TError]]
) -> Callable[[A], Result[C, TError]]:
    ...


@overload
def kleisli(
    fn1: Callable[[A], Result[B, TError]], fn2: Callable[[B], Result[C, TError]], fn3: Callable[[C], Result[D, TError]]
) -> Callable[[A], D]:
    ...


@overload
def kleisli(
    op4: Callable[[A], Result[B, TError]],
    op3: Callable[[B], Result[C, TError]],
    op2: Callable[[C], Result[D, TError]],
    op1: Callable[[D], Result[E, TError]],
) -> Callable[[A], E]:
    ...


@overload
def kleisli(
    fn1: Callable[[A], Result[B, TError]],
    fn2: Callable[[B], Result[C, TError]],
    fn3: Callable[[C], Result[D, TError]],
    fn4: Callable[[D], Result[E, TError]],
    fn5: Callable[[E], Result[F, TError]],
) -> Callable[[A], F]:
    ...


@overload
def kleisli(
    fn1: Callable[[A], Result[B, TError]],
    fn2: Callable[[B], Result[C, TError]],
    fn3: Callable[[C], Result[D, TError]],
    fn4: Callable[[D], Result[E, TError]],
    fn5: Callable[[E], Result[F, TError]],
    fn6: Callable[[F], Result[G, TError]],
) -> Callable[[A], G]:
    ...


def kleisli(*fns: Callable) -> Callable:  # type: ignore
    """Kleisli (>=>) compose multiple functions left to right.

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
            return fn(acc.value) if acc.is_ok() else acc
        return reduce(reducer, fns, source)

    return _kleisli


__all__ = ["kleisli"]
