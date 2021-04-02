from functools import reduce
from typing import Callable, TypeVar, overload

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")
D = TypeVar("D")
E = TypeVar("E")
F = TypeVar("F")
G = TypeVar("G")
H = TypeVar("H")
T = TypeVar("T")
J = TypeVar("J")


@overload
def compose() -> Callable[[A], A]:
    ...


@overload
def compose(__fn1: Callable[[A], B]) -> Callable[[A], B]:
    ...


@overload
def compose(__fn1: Callable[[A], B], __fn2: Callable[[B], C]) -> Callable[[A], C]:
    ...


@overload
def compose(__fn1: Callable[[A], B], __fn2: Callable[[B], C], __fn3: Callable[[C], D]) -> Callable[[A], D]:
    ...


@overload
def compose(
    __fn1: Callable[[A], B],
    __fn2: Callable[[B], C],
    __fn3: Callable[[C], D],
    __fn4: Callable[[D], E],
) -> Callable[[A], E]:
    ...


@overload
def compose(
    __fn1: Callable[[A], B],
    __fn2: Callable[[B], C],
    __fn3: Callable[[C], D],
    __fn4: Callable[[D], E],
    __fn5: Callable[[E], F],
) -> Callable[[A], F]:
    ...


@overload
def compose(
    __fn1: Callable[[A], B],
    __fn2: Callable[[B], C],
    __fn3: Callable[[C], D],
    __fn4: Callable[[D], E],
    __fn5: Callable[[E], F],
    __fn6: Callable[[F], G],
) -> Callable[[A], G]:
    ...


@overload
def compose(
    __fn1: Callable[[A], B],
    __fn2: Callable[[B], C],
    __fn3: Callable[[C], D],
    __fn4: Callable[[D], E],
    __fn5: Callable[[E], F],
    __fn6: Callable[[F], G],
    __fn7: Callable[[G], H],
) -> Callable[[A], H]:
    ...


@overload
def compose(
    __fn1: Callable[[A], B],
    __fn2: Callable[[B], C],
    __fn3: Callable[[C], D],
    __fn4: Callable[[D], E],
    __fn5: Callable[[E], F],
    __fn6: Callable[[F], G],
    __fn7: Callable[[G], H],
    __fn8: Callable[[H], T],
) -> Callable[[A], T]:
    ...


@overload
def compose(
    __fn1: Callable[[A], B],
    __fn2: Callable[[B], C],
    __fn3: Callable[[C], D],
    __fn4: Callable[[D], E],
    __fn5: Callable[[E], F],
    __fn6: Callable[[F], G],
    __fn7: Callable[[G], H],
    __fn8: Callable[[H], T],
    __fn9: Callable[[T], J],
) -> Callable[[A], J]:
    ...


def compose(*fns):  # type: ignore
    """Compose multiple functions left to right.

    Composes zero or more functions into a functional composition. The
    functions are composed left to right. A composition of zero
    functions gives back the identity function.

    >>> x = 42
    >>> f = lambda a: a * 10
    >>> g = lambda b: b + 3
    >>> h = lambda c: c / 2
    >>> compose()(x) == x
    >>> compose(f)(x) == f(x)
    >>> compose(f, g)(x) == g(f(x))
    >>> compose(f, g, h)(x) == h(g(f(x)))
    ...

    Returns:
        The composed function.
    """

    def _compose(source):  # type: ignore
        """Return a pipeline of composed functions."""
        return reduce(lambda acc, f: f(acc), fns, source)  # type: ignore

    return _compose  # type: ignore


__all__ = ["compose"]
