from functools import reduce
from typing import Callable, Any, TypeVar, overload

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")
D = TypeVar("D")
E = TypeVar("E")
F = TypeVar("F")
G = TypeVar("G")
H = TypeVar("H")


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


def compose(*fns: Callable[[Any], Any]) -> Callable[[Any], Any]:
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

    def compose(source: Any) -> Any:
        """Return a pipeline of composed functions."""
        return reduce(lambda acc, f: f(acc), fns, source)

    return compose


__all__ = ["compose"]
