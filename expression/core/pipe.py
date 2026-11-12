"""Pipe module.

Contains pipe function including necessary overloads to get the type-hints right.

Example:
    >>> from expression import pipe
    >>>
    >>> v = 1
    >>> fn = lambda x: x + 1
    >>> gn = lambda x: x * 2
    >>>
    >>> assert pipe(v, fn, gn) == gn(fn(v))
"""

from collections.abc import Callable
from typing import Any, Unpack, cast, overload

from .compose import compose, starcompose
from .misc import starid


@overload
def pipe[A](value: A, /) -> A: ...


@overload
def pipe[A, B](value: A, fn1: Callable[[A], B], /) -> B: ...


@overload
def pipe[A, B, C](value: A, fn1: Callable[[A], B], fn2: Callable[[B], C], /) -> C: ...


@overload
def pipe[A, B, C, D](
    value: A,
    fn1: Callable[[A], B],
    fn2: Callable[[B], C],
    fn3: Callable[[C], D],
    /,
) -> D: ...


@overload
def pipe[A, B, C, D, E](
    value: A,
    fn1: Callable[[A], B],
    fn2: Callable[[B], C],
    fn3: Callable[[C], D],
    fn4: Callable[[D], E],
    /,
) -> E: ...


@overload
def pipe[A, B, C, D, E, F](
    value: A,
    fn1: Callable[[A], B],
    fn2: Callable[[B], C],
    fn3: Callable[[C], D],
    fn4: Callable[[D], E],
    fn5: Callable[[E], F],
    /,
) -> F: ...


@overload
def pipe[A, B, C, D, E, F, G](
    value: A,
    fn1: Callable[[A], B],
    fn2: Callable[[B], C],
    fn3: Callable[[C], D],
    fn4: Callable[[D], E],
    fn5: Callable[[E], F],
    fn6: Callable[[F], G],
    /,
) -> G: ...


@overload
def pipe[A, B, C, D, E, F, G, H](
    value: A,
    fn1: Callable[[A], B],
    fn2: Callable[[B], C],
    fn3: Callable[[C], D],
    fn4: Callable[[D], E],
    fn5: Callable[[E], F],
    fn6: Callable[[F], G],
    fn7: Callable[[G], H],
    /,
) -> H: ...


@overload
def pipe[A, B, C, D, E, F, G, H, T](
    value: A,
    fn1: Callable[[A], B],
    fn2: Callable[[B], C],
    fn3: Callable[[C], D],
    fn4: Callable[[D], E],
    fn5: Callable[[E], F],
    fn6: Callable[[F], G],
    fn7: Callable[[G], H],
    fn8: Callable[[H], T],
    /,
) -> T: ...


@overload
def pipe[A, B, C, D, E, F, G, H, T, J](
    value: A,
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
) -> J: ...


@overload
def pipe[A, B, C, D, E, F, G, H, T, J, I](
    value: A,
    fn1: Callable[[A], B],
    fn2: Callable[[B], C],
    fn3: Callable[[C], D],
    fn4: Callable[[D], E],
    fn5: Callable[[E], F],
    fn6: Callable[[F], G],
    fn7: Callable[[G], H],
    fn8: Callable[[H], T],
    fn9: Callable[[T], J],
    fn10: Callable[[J], I],
    /,
) -> I: ...


@overload
def pipe[A, B, C, D, E, F, G, H, T, J, I, K1](
    value: A,
    fn1: Callable[[A], B],
    fn2: Callable[[B], C],
    fn3: Callable[[C], D],
    fn4: Callable[[D], E],
    fn5: Callable[[E], F],
    fn6: Callable[[F], G],
    fn7: Callable[[G], H],
    fn8: Callable[[H], T],
    fn9: Callable[[T], J],
    fn10: Callable[[J], I],
    fn11: Callable[[I], K1],
    /,
) -> K1: ...


@overload
def pipe[A, B, C, D, E, F, G, H, T, J, I, K1, L](
    value: A,
    fn1: Callable[[A], B],
    fn2: Callable[[B], C],
    fn3: Callable[[C], D],
    fn4: Callable[[D], E],
    fn5: Callable[[E], F],
    fn6: Callable[[F], G],
    fn7: Callable[[G], H],
    fn8: Callable[[H], T],
    fn9: Callable[[T], J],
    fn10: Callable[[J], I],
    fn11: Callable[[I], K1],
    fn12: Callable[[K1], L],
    /,
) -> L: ...


@overload
def pipe[A, B, C, D, E, F, G, H, T, J, I, K1, L, M](
    value: A,
    fn1: Callable[[A], B],
    fn2: Callable[[B], C],
    fn3: Callable[[C], D],
    fn4: Callable[[D], E],
    fn5: Callable[[E], F],
    fn6: Callable[[F], G],
    fn7: Callable[[G], H],
    fn8: Callable[[H], T],
    fn9: Callable[[T], J],
    fn10: Callable[[J], I],
    fn11: Callable[[I], K1],
    fn12: Callable[[K1], L],
    fn13: Callable[[L], M],
    /,
) -> M: ...


@overload
def pipe[A, B, C, D, E, F, G, H, T, J, I, K1, L, M, N](
    value: A,
    fn1: Callable[[A], B],
    fn2: Callable[[B], C],
    fn3: Callable[[C], D],
    fn4: Callable[[D], E],
    fn5: Callable[[E], F],
    fn6: Callable[[F], G],
    fn7: Callable[[G], H],
    fn8: Callable[[H], T],
    fn9: Callable[[T], J],
    fn10: Callable[[J], I],
    fn11: Callable[[I], K1],
    fn12: Callable[[K1], L],
    fn13: Callable[[L], M],
    fn14: Callable[[M], N],
    /,
) -> N: ...


@overload
def pipe[A, B, C, D, E, F, G, H, T, J, I, K1, L, M, N, O](
    value: A,
    fn1: Callable[[A], B],
    fn2: Callable[[B], C],
    fn3: Callable[[C], D],
    fn4: Callable[[D], E],
    fn5: Callable[[E], F],
    fn6: Callable[[F], G],
    fn7: Callable[[G], H],
    fn8: Callable[[H], T],
    fn9: Callable[[T], J],
    fn10: Callable[[J], I],
    fn11: Callable[[I], K1],
    fn12: Callable[[K1], L],
    fn13: Callable[[L], M],
    fn14: Callable[[M], N],
    fn15: Callable[[N], O],
    /,
) -> O: ...


@overload
def pipe[A, B, C, D, E, F, G, H, T, J, I, K1, L, M, N, O, P1](
    value: A,
    fn1: Callable[[A], B],
    fn2: Callable[[B], C],
    fn3: Callable[[C], D],
    fn4: Callable[[D], E],
    fn5: Callable[[E], F],
    fn6: Callable[[F], G],
    fn7: Callable[[G], H],
    fn8: Callable[[H], T],
    fn9: Callable[[T], J],
    fn10: Callable[[J], I],
    fn11: Callable[[I], K1],
    fn12: Callable[[K1], L],
    fn13: Callable[[L], M],
    fn14: Callable[[M], N],
    fn15: Callable[[N], O],
    fn16: Callable[[O], P1],
    /,
) -> P1: ...


def pipe(value: Any, *fns: Callable[[Any], Any]) -> Any:
    """Functional pipe (`|>`).

    Allows the use of function argument on the left side of the
    function.

    Example:
        >>> pipe(x, fn) == fn(x)  # Same as x |> fn
        >>> pipe(x, fn, gn) == gn(fn(x))  # Same as x |> fn |> gn
        ...
    """
    return compose(*fns)(value)


@overload
def pipe2[A, B](values: tuple[A, B], /) -> tuple[A, B]: ...


@overload
def pipe2[A, B, C](values: tuple[A, B], fn1: Callable[[A], Callable[[B], C]], /) -> C: ...


@overload
def pipe2[A, B, C, D](
    values: tuple[A, B],
    fn1: Callable[[A], Callable[[B], C]],
    fn2: Callable[[C], D],
    /,
) -> D: ...


@overload
def pipe2[A, B, C, D, E](
    values: tuple[A, B],
    fn1: Callable[[A], Callable[[B], C]],
    fn2: Callable[[C], D],
    fn3: Callable[[D], E],
    /,
) -> E: ...


def pipe2(values: Any, /, *fns: Any) -> Any:
    return pipe(fns[0](values[0])(values[1]), *fns[1:]) if fns else values


def pipe3(values: Any, /, *fns: Any) -> Any:
    return pipe(fns[0](values[0])(values[1])(values[2]), *fns[1:]) if fns else values


@overload
def starpipe[*P, B](args: tuple[*P], fn1: Callable[[Unpack[P]], B], /) -> B: ...


@overload
def starpipe[*P, *Q, B](args: tuple[*P], fn1: Callable[[Unpack[P]], tuple[*Q]], fn2: Callable[[*Q], B], /) -> B: ...


@overload
def starpipe[*P, *Q, *X, B](
    args: tuple[*P],
    fn1: Callable[[Unpack[P]], tuple[*Q]],
    fn2: Callable[[Unpack[Q]], tuple[*X]],
    fn3: Callable[[Unpack[X]], B],
    /,
) -> B: ...


@overload
def starpipe[*P, *Q, *X, *Y, B](
    args: tuple[*P],
    fn1: Callable[[Unpack[P]], tuple[*Q]],
    fn2: Callable[[Unpack[Q]], tuple[*X]],
    fn3: Callable[[Unpack[X]], tuple[*Y]],
    fn4: Callable[[Unpack[Y]], B],
    /,
) -> B: ...


@overload
def starpipe[*P, *Q, *X, *Y, *Z, B](
    args: tuple[*P],
    fn1: Callable[[Unpack[P]], tuple[*Q]],
    fn2: Callable[[Unpack[Q]], tuple[*X]],
    fn3: Callable[[Unpack[X]], tuple[*Y]],
    fn4: Callable[[Unpack[Y]], tuple[*Z]],
    fn5: Callable[[Unpack[Z]], B],
    /,
) -> B: ...


@overload
def starpipe[*P, *Q, *X, *Y, *Z, *K, B](
    args: tuple[*P],
    fn1: Callable[[Unpack[P]], tuple[*Q]],
    fn2: Callable[[Unpack[Q]], tuple[*X]],
    fn3: Callable[[Unpack[X]], tuple[*Y]],
    fn4: Callable[[Unpack[Y]], tuple[*Z]],
    fn5: Callable[[Unpack[Z]], tuple[*K]],
    fn6: Callable[[Unpack[K]], B],
    /,
) -> B: ...


def starpipe(args: Any, /, *fns: Callable[..., Any]) -> Any:
    """Functional pipe_n (`||>`, `||>`, `|||>`, etc).

    Allows the use of function arguments on the left side of the
    function. Calls the function with tuple arguments unpacked.

    Example:
        >>> starpipe((x, y), fn) == fn(x, y)  # Same as (x, y) ||> fn
        >>> starpipe((x, y), fn, gn) == gn(*fn(x))  # Same as (x, y) ||> fn |||> gn
        >>> starpipe((x, y), fn, gn, hn) == hn(*gn(*fn(x)))  # Same as (x, y) ||> fn |||> gn ||> hn
        ...
    """
    # Cast since unpacked arguments be used with TypeVarTuple
    _starid = cast(Callable[..., Any], starid)
    fn = fns[0] if len(fns) else _starid

    return starcompose(*fns[1:])(fn(*args))


class PipeMixin:
    """A pipe mixin class that enabled a class to use pipe fluently."""

    __slots__ = ()

    @overload
    def pipe[A, B](self: A, fn1: Callable[[A], B], /) -> B: ...

    @overload
    def pipe[A, B, C](self: A, fn1: Callable[[A], B], fn2: Callable[[B], C], /) -> C: ...

    @overload
    def pipe[A, B, C, D](self: A, fn1: Callable[[A], B], fn2: Callable[[B], C], fn3: Callable[[C], D], /) -> D: ...

    @overload
    def pipe[A, B, C, D, E](
        self: A,
        fn1: Callable[[A], B],
        fn2: Callable[[B], C],
        fn3: Callable[[C], D],
        fn4: Callable[[D], E],
        /,
    ) -> E: ...

    @overload
    def pipe[A, B, C, D, E, F](
        self: A,
        fn1: Callable[[A], B],
        fn2: Callable[[B], C],
        fn3: Callable[[C], D],
        fn4: Callable[[D], E],
        fn5: Callable[[E], F],
        /,
    ) -> F: ...

    @overload
    def pipe[A, B, C, D, E, F, G](
        self: A,
        fn1: Callable[[A], B],
        fn2: Callable[[B], C],
        fn3: Callable[[C], D],
        fn4: Callable[[D], E],
        fn5: Callable[[E], F],
        fn6: Callable[[F], G],
        /,
    ) -> G: ...

    @overload
    def pipe[A, B, C, D, E, F, G, H](
        self: A,
        fn1: Callable[[A], B],
        fn2: Callable[[B], C],
        fn3: Callable[[C], D],
        fn4: Callable[[D], E],
        fn5: Callable[[E], F],
        fn6: Callable[[F], G],
        fn7: Callable[[G], H],
        /,
    ) -> H: ...

    @overload
    def pipe[A, B, C, D, E, F, G, H, T](
        self: A,
        fn1: Callable[[A], B],
        fn2: Callable[[B], C],
        fn3: Callable[[C], D],
        fn4: Callable[[D], E],
        fn5: Callable[[E], F],
        fn6: Callable[[F], G],
        fn7: Callable[[G], H],
        fn8: Callable[[H], T],
        /,
    ) -> T: ...

    @overload
    def pipe[A, B, C, D, E, F, G, H, T, J](
        self: A,
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
    ) -> J: ...

    @overload
    def pipe[A, B, C, D, E, F, G, H, T, J, I](
        self: A,
        fn1: Callable[[A], B],
        fn2: Callable[[B], C],
        fn3: Callable[[C], D],
        fn4: Callable[[D], E],
        fn5: Callable[[E], F],
        fn6: Callable[[F], G],
        fn7: Callable[[G], H],
        fn8: Callable[[H], T],
        fn9: Callable[[T], J],
        fn10: Callable[[J], I],
        /,
    ) -> I: ...

    @overload
    def pipe[A, B, C, D, E, F, G, H, T, J, I, K1](
        self: A,
        fn1: Callable[[A], B],
        fn2: Callable[[B], C],
        fn3: Callable[[C], D],
        fn4: Callable[[D], E],
        fn5: Callable[[E], F],
        fn6: Callable[[F], G],
        fn7: Callable[[G], H],
        fn8: Callable[[H], T],
        fn9: Callable[[T], J],
        fn10: Callable[[J], I],
        fn11: Callable[[I], K1],
        /,
    ) -> K1: ...

    @overload
    def pipe[A, B, C, D, E, F, G, H, T, J, I, K1, L](
        self: A,
        fn1: Callable[[A], B],
        fn2: Callable[[B], C],
        fn3: Callable[[C], D],
        fn4: Callable[[D], E],
        fn5: Callable[[E], F],
        fn6: Callable[[F], G],
        fn7: Callable[[G], H],
        fn8: Callable[[H], T],
        fn9: Callable[[T], J],
        fn10: Callable[[J], I],
        fn11: Callable[[I], K1],
        fn12: Callable[[K1], L],
        /,
    ) -> L: ...

    @overload
    def pipe[A, B, C, D, E, F, G, H, T, J, I, K1, L, M](
        self: A,
        fn1: Callable[[A], B],
        fn2: Callable[[B], C],
        fn3: Callable[[C], D],
        fn4: Callable[[D], E],
        fn5: Callable[[E], F],
        fn6: Callable[[F], G],
        fn7: Callable[[G], H],
        fn8: Callable[[H], T],
        fn9: Callable[[T], J],
        fn10: Callable[[J], I],
        fn11: Callable[[I], K1],
        fn12: Callable[[K1], L],
        fn13: Callable[[L], M],
        /,
    ) -> M: ...

    @overload
    def pipe[A, B, C, D, E, F, G, H, T, J, I, K1, L, M, N](
        self: A,
        fn1: Callable[[A], B],
        fn2: Callable[[B], C],
        fn3: Callable[[C], D],
        fn4: Callable[[D], E],
        fn5: Callable[[E], F],
        fn6: Callable[[F], G],
        fn7: Callable[[G], H],
        fn8: Callable[[H], T],
        fn9: Callable[[T], J],
        fn10: Callable[[J], I],
        fn11: Callable[[I], K1],
        fn12: Callable[[K1], L],
        fn13: Callable[[L], M],
        fn14: Callable[[M], N],
        /,
    ) -> N: ...

    @overload
    def pipe[A, B, C, D, E, F, G, H, T, J, I, K1, L, M, N, O](
        self: A,
        fn1: Callable[[A], B],
        fn2: Callable[[B], C],
        fn3: Callable[[C], D],
        fn4: Callable[[D], E],
        fn5: Callable[[E], F],
        fn6: Callable[[F], G],
        fn7: Callable[[G], H],
        fn8: Callable[[H], T],
        fn9: Callable[[T], J],
        fn10: Callable[[J], I],
        fn11: Callable[[I], K1],
        fn12: Callable[[K1], L],
        fn13: Callable[[L], M],
        fn14: Callable[[M], N],
        fn15: Callable[[N], O],
        /,
    ) -> O: ...

    @overload
    def pipe[A, B, C, D, E, F, G, H, T, J, I, K1, L, M, N, O, P1](
        self: A,
        fn1: Callable[[A], B],
        fn2: Callable[[B], C],
        fn3: Callable[[C], D],
        fn4: Callable[[D], E],
        fn5: Callable[[E], F],
        fn6: Callable[[F], G],
        fn7: Callable[[G], H],
        fn8: Callable[[H], T],
        fn9: Callable[[T], J],
        fn10: Callable[[J], I],
        fn11: Callable[[I], K1],
        fn12: Callable[[K1], L],
        fn13: Callable[[L], M],
        fn14: Callable[[M], N],
        fn15: Callable[[N], O],
        fn16: Callable[[O], P1],
        /,
    ) -> P1: ...

    def pipe(self, *args: Any) -> Any:
        """Pipe the left side object through the given functions."""
        return pipe(self, *args)


__all__ = ["PipeMixin", "pipe", "pipe2", "pipe3", "starpipe"]
