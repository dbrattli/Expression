from typing import Any, Callable, Tuple, TypeVar, overload

from .compose import compose
from .misc import starid

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
def pipe(value: A) -> A:
    ...


@overload
def pipe(value: A, __fn1: Callable[[A], B]) -> B:
    ...


@overload
def pipe(value: A, __fn1: Callable[[A], B], __fn2: Callable[[B], C]) -> C:
    ...


@overload
def pipe(value: A, __fn1: Callable[[A], B], __fn2: Callable[[B], C], __fn3: Callable[[C], D]) -> D:
    ...


@overload
def pipe(
    value: A,
    __fn1: Callable[[A], B],
    __fn2: Callable[[B], C],
    __fn3: Callable[[C], D],
    __fn4: Callable[[D], E],
) -> E:
    ...


@overload
def pipe(
    value: A,
    __fn1: Callable[[A], B],
    __fn2: Callable[[B], C],
    __fn3: Callable[[C], D],
    __fn4: Callable[[D], E],
    __fn5: Callable[[E], F],
) -> F:
    ...


@overload
def pipe(
    value: A,
    __fn1: Callable[[A], B],
    __fn2: Callable[[B], C],
    __fn3: Callable[[C], D],
    __fn4: Callable[[D], E],
    __fn5: Callable[[E], F],
    __fn6: Callable[[F], G],
) -> G:
    ...


@overload
def pipe(
    value: A,
    __fn1: Callable[[A], B],
    __fn2: Callable[[B], C],
    __fn3: Callable[[C], D],
    __fn4: Callable[[D], E],
    __fn5: Callable[[E], F],
    __fn6: Callable[[F], G],
    __fn7: Callable[[G], H],
) -> H:
    ...


@overload
def pipe(
    value: A,
    __fn1: Callable[[A], B],
    __fn2: Callable[[B], C],
    __fn3: Callable[[C], D],
    __fn4: Callable[[D], E],
    __fn5: Callable[[E], F],
    __fn6: Callable[[F], G],
    __fn7: Callable[[G], H],
    __fn8: Callable[[H], T],
) -> T:
    ...


@overload
def pipe(
    value: A,
    __fn1: Callable[[A], B],
    __fn2: Callable[[B], C],
    __fn3: Callable[[C], D],
    __fn4: Callable[[D], E],
    __fn5: Callable[[E], F],
    __fn6: Callable[[F], G],
    __fn7: Callable[[G], H],
    __fn8: Callable[[H], T],
    __fn9: Callable[[T], J],
) -> J:
    ...


def pipe(value: Any, *fns: Callable[[Any], Any]) -> Any:  # type: ignore
    """Functional pipe (`|>`)

    Allows the use of function argument on the left side of the function.

    Example:
        >>> pipe(x, fn) == __fn(x)  # Same as x |> fn
        >>> pipe(x, fn, gn) == gn(fn(x))  # Same as x |> fn |> gn
        ...
    """

    return compose(*fns)(value)


@overload
def pipe2(values: Tuple[A, B]) -> Tuple[A, B]:
    ...


@overload
def pipe2(values: Tuple[A, B], __fn1: Callable[[A, B], C]) -> C:
    ...


@overload
def pipe2(values: Tuple[A, B], __fn1: Callable[[A, B], C], __fn2: Callable[[C], D]) -> D:
    ...


@overload
def pipe2(values: Tuple[A, B], __fn1: Callable[[A, B], C], __fn2: Callable[[C], D], __fn3: Callable[[D], E]) -> E:
    ...


def pipe2(values: Any, *fns: Any) -> Any:
    return starpipe(values, *fns)


def pipe3(args: Any, *fns: Any) -> Any:
    return starpipe(args, *fns)


def starpipe(args: Any, *fns: Any):
    """Functional pipe_n (`||>`, `||>`, `|||>`, etc)

    Allows the use of function arguments on the left side of the
    function. Calls the function with tuple arguments unpacked.

    Example:
        >>> starpipe((x, y), __fn) == __fn(x, y)  # Same as (x, y) ||> __fn
        >>> starpipe((x, y), __fn, gn) == gn(fn(x))  # Same as (x, y) ||> __fn |> gn
        ...
    """

    fn = fns[0] if len(fns) else starid

    return compose(*fns[1:])(fn(*args))


__all__ = ["pipe", "pipe2", "pipe3", "starpipe"]
