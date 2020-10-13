from functools import reduce
from typing import Callable, Any, TypeVar, overload

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")
D = TypeVar("D")
E = TypeVar("E")
F = TypeVar("F")
G = TypeVar("G")


@overload
def compose() -> Callable[[A], A]:
    ...


@overload
def compose(fn1: Callable[[A], B]) -> Callable[[A], B]:
    ...


@overload
def compose(fn1: Callable[[A], B], fn2: Callable[[B], C]) -> Callable[[A], C]:
    ...


@overload
def compose(
    fn1: Callable[[A], B], fn2: Callable[[B], C], fn3: Callable[[C], D]
) -> Callable[[A], D]:
    ...


@overload
def compose(
    fn1: Callable[[A], B],
    fn2: Callable[[B], C],
    fn3: Callable[[C], D],
    fn4: Callable[[D], E],
) -> Callable[[A], E]:
    ...


@overload
def compose(
    fn1: Callable[[A], B],
    fn2: Callable[[B], C],
    fn3: Callable[[C], D],
    fn4: Callable[[D], E],
    fn5: Callable[[E], F],
) -> Callable[[A], F]:
    ...


@overload
def compose(
    fn1: Callable[[A], B],
    fn2: Callable[[B], C],
    fn3: Callable[[C], D],
    fn4: Callable[[D], E],
    fn5: Callable[[E], F],
    fn6: Callable[[F], G],
) -> Callable[[A], G]:
    ...


def compose(*fns: Callable) -> Callable:  # type: ignore
    """Compose multiple functions left to right.

    Composes zero or more functions into a functional composition. The
    functions are composed left to right. A composition of zero
    functions gives back the identity function.

    >>> compose()(x) == x
    >>> compose(f)(x) == f(x)
    >>> compose(f, g)(x) == g(f(x))
    >>> compose(f, g, h)(x) == h(g(f(x)))
    ...

    Returns:
        The composed function.
    """

    def _compose(source: Any) -> Any:
        return reduce(lambda acc, f: f(acc), fns, source)

    return _compose


__all__ = ["compose"]
