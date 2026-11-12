from collections.abc import Callable
from functools import reduce
from typing import Any, Unpack, overload


@overload
def compose[A]() -> Callable[[A], A]: ...


@overload
def compose[B, A](__fn1: Callable[[A], B]) -> Callable[[A], B]: ...


@overload
def compose[B, A, C](__fn1: Callable[[A], B], __fn2: Callable[[B], C]) -> Callable[[A], C]: ...


@overload
def compose[B, A, C, D](
    __fn1: Callable[[A], B], __fn2: Callable[[B], C], __fn3: Callable[[C], D]
) -> Callable[[A], D]: ...


@overload
def compose[B, A, C, D, E](
    fn1: Callable[[A], B],
    fn2: Callable[[B], C],
    fn3: Callable[[C], D],
    fn4: Callable[[D], E],
    /,
) -> Callable[[A], E]: ...


@overload
def compose[B, A, C, D, E, F](
    fn1: Callable[[A], B],
    fn2: Callable[[B], C],
    fn3: Callable[[C], D],
    fn4: Callable[[D], E],
    fn5: Callable[[E], F],
    /,
) -> Callable[[A], F]: ...


@overload
def compose[B, A, C, D, E, F, G](
    fn1: Callable[[A], B],
    fn2: Callable[[B], C],
    fn3: Callable[[C], D],
    fn4: Callable[[D], E],
    fn5: Callable[[E], F],
    fn6: Callable[[F], G],
    /,
) -> Callable[[A], G]: ...


@overload
def compose[B, A, C, D, E, F, G, H](
    fn1: Callable[[A], B],
    fn2: Callable[[B], C],
    fn3: Callable[[C], D],
    fn4: Callable[[D], E],
    fn5: Callable[[E], F],
    fn6: Callable[[F], G],
    fn7: Callable[[G], H],
    /,
) -> Callable[[A], H]: ...


@overload
def compose[B, A, C, D, E, F, G, H, T](
    fn1: Callable[[A], B],
    fn2: Callable[[B], C],
    fn3: Callable[[C], D],
    fn4: Callable[[D], E],
    fn5: Callable[[E], F],
    fn6: Callable[[F], G],
    fn7: Callable[[G], H],
    fn8: Callable[[H], T],
    /,
) -> Callable[[A], T]: ...


@overload
def compose[B, A, C, D, E, F, G, H, T, J](
    fn1: Callable[[A], B],
    fn2: Callable[[B], C],
    fn3: Callable[[C], D],
    fn4: Callable[[D], E],
    fn5: Callable[[E], F],
    fn6: Callable[[F], G],
    fn7: Callable[[G], H],
    fn8: Callable[[H], T],
    fn9: Callable[[T], J],
    /,
) -> Callable[[A], J]: ...


def compose(*fns: Callable[[Any], Any]) -> Callable[[Any], Any]:
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

    def _compose(source: Any) -> Any:
        """Return a pipeline of composed functions."""
        return reduce(lambda acc, f: f(acc), fns, source)

    return _compose


@overload
def starcompose() -> Callable[[Any], Any]: ...


@overload
def starcompose[A, *P](fn1: Callable[[Unpack[P]], A], /) -> Callable[[Unpack[P]], A]: ...


@overload
def starcompose[*P, *Y, B](
    fn1: Callable[[Unpack[P]], tuple[*Y]], fn2: Callable[[Unpack[Y]], B], /
) -> Callable[[Unpack[P]], B]: ...


@overload
def starcompose[*P, *Y, *Z, C](
    fn1: Callable[[Unpack[P]], tuple[*Y]],
    fn2: Callable[[Unpack[Y]], tuple[*Z]],
    fn3: Callable[[Unpack[Z]], C],
    /,
) -> Callable[[Unpack[P]], C]: ...


@overload
def starcompose[*P, *Y, *Z, *X, D](
    fn1: Callable[[Unpack[P]], tuple[*Y]],
    fn2: Callable[[Unpack[Y]], tuple[*Z]],
    fn3: Callable[[Unpack[Z]], tuple[*X]],
    fn4: Callable[[Unpack[X]], D],
    /,
) -> Callable[[Unpack[P]], D]: ...


def starcompose(*fns: Callable[..., Any]) -> Callable[..., Any]:
    """Compose multiple functions left to right.

    Composes zero or more functions into a functional composition. The
    functions are composed left to right. A composition of zero
    functions gives back the identity function.

    The first function must accept a variable number of positional
    arguments and if it returns a tuple, the subsequent functions must
    accept the same number of arguments as the length of the tuple of
    the previous function.
    """

    def _compose(source: Any) -> Any:
        """Return a pipeline of composed functions."""
        return reduce(lambda fields, f: f(*fields), fns, source)

    return _compose


__all__ = ["compose"]
