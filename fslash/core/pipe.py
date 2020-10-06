from typing import TypeVar, Callable, Tuple, overload

from .compose import compose
from .misc import starid


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
def pipe(value: A, fn1: Callable[[A], B], fn2: Callable[[B], C]) -> C:
    ...


@overload
def pipe(
    value: A,
    fn1: Callable[[A], B], fn2: Callable[[B], C], fn3: Callable[[C], D]
) -> D:
    ...


@overload
def pipe(
    value: A,
    fn1: Callable[[A], B],
    fn2: Callable[[B], C],
    fn3: Callable[[C], D],
    fn4: Callable[[D], E],
) -> E:
    ...


@overload
def pipe(
    value: A,
    fn1: Callable[[A], B],
    fn2: Callable[[B], C],
    fn3: Callable[[C], D],
    fn4: Callable[[D], E],
    fn5: Callable[[E], F],
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
    """Functional pipe (`|>`)

    Allows the use of function argument on the left side of the function.

    Example:
        >>> pipe(x, fn) == fn(x)  # Same as x |> fn
        >>> pipe(x, fn, gn) == gn(fn(x))  # Same as x |> fn |> gn
        ...
    """

    return compose(*fns)(x)  # type: ignore


@overload
def pipe2(value: Tuple[A, B]) -> Tuple[A, B]:
    ...


@overload
def pipe2(value: Tuple[A, B], fn1: Callable[[A, B], C]) -> C:
    ...


@overload
def pipe2(value: Tuple[A, B], fn1: Callable[[A, B], C], fn2: Callable[[C], D]) -> D:
    ...


@overload
def pipe2(
    value: Tuple[A, B],
    fn1: Callable[[A, B], C], fn2: Callable[[C], D], fn3: Callable[[D], E]
) -> D:
    ...


def pipe2(args, *fns):
    return starpipe(args, *fns)


def pipe3(args, *fns):
    return starpipe(args, *fns)


def starpipe(args, *fns):  # type: ignore
    """Functional pipe_n (`||>`, `||>`, `|||>`, etc)

    Allows the use of function arguments on the left side of the function.

    Example:
        >>> starpipe((x, y), fn) == fn(x, y)  # Same as (x, y) ||> fn
        >>> starpipe((x, y), fn, gn) == gn(fn(x))  # Same as (x, y) ||> fn |> gn
        ...
    """

    fn = fns[0] if len(fns) else starid

    return compose(*fns[1:])(fn(*args))  # type: ignore


__all__ = ["pipe", "pipe2", "pipe3", "starpipe"]
