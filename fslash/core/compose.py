from functools import reduce

from typing import Tuple, Callable, Any, TypeVar, overload  # noqa

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
def compose(op1: Callable[[A], B]) -> Callable[[A], B]:
    ...


@overload
def compose(op2: Callable[[A], B], op1: Callable[[B], C]) -> Callable[[A], C]:
    ...


@overload
def compose(
    op3: Callable[[A], B], op2: Callable[[B], C], op1: Callable[[C], D]
) -> Callable[[A], D]:
    ...


@overload
def compose(
    op4: Callable[[A], B],
    op3: Callable[[B], C],
    op2: Callable[[C], D],
    op1: Callable[[D], E],
) -> Callable[[A], E]:
    ...


@overload
def compose(
    op5: Callable[[A], B],
    op4: Callable[[B], C],
    op3: Callable[[C], D],
    op2: Callable[[D], E],
    op1: Callable[[E], F],
) -> Callable[[A], F]:
    ...


@overload
def compose(
    op1: Callable[[A], B],
    op2: Callable[[B], C],
    op3: Callable[[C], D],
    op4: Callable[[D], E],
    op5: Callable[[E], F],
    op6: Callable[[F], G],
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
