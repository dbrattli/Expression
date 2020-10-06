from typing import TypeVar, Callable, overload

from .compose import compose

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")
D = TypeVar("D")
E = TypeVar("E")
F = TypeVar("F")
G = TypeVar("G")


@overload
def pipe(value: A) -> A:
    ...


@overload
def pipe(value: A, fn1: Callable[[A], B]) -> B:
    ...


@overload
def pipe(value: A, fn2: Callable[[A], B], fn1: Callable[[B], C]) -> C:
    ...


@overload
def pipe(
    value: A,
    fn3: Callable[[A], B], fn2: Callable[[B], C], fn1: Callable[[C], D]
) -> D:
    ...


@overload
def pipe(
    value: A,
    fn4: Callable[[A], B],
    fn3: Callable[[B], C],
    fn2: Callable[[C], D],
    fn1: Callable[[D], E],
) -> E:
    ...


@overload
def pipe(
    value: A,
    fn5: Callable[[A], B],
    fn4: Callable[[B], C],
    fn3: Callable[[C], D],
    fn2: Callable[[D], E],
    fn1: Callable[[E], F],
) -> F:
    ...


@overload
def pipe(
    value: A,
    fn1: Callable[[A], B],
    fn2: Callable[[B], C],
    fn3: Callable[[C], D],
    fn4: Callable[[D], E],
    fn5: Callable[[E], F],
    fn6: Callable[[F], G],
) -> G:
    ...


def pipe(x, *fns):  # type: ignore
    """Functional pipe (|>)

    Allows the use of function argument on the left side of the function.

    Example:
        pipe(x, fn) == fn(x)  # Same as x |> fn
        pipe(x, fn, gn) == gn(fn(x))  # Same as x |> fn |> gn
        ...
    """

    return compose(*fns)(x)  # type: ignore


__all__ = ["pipe"]
