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
from typing import Any, TypeVar, cast, overload

from typing_extensions import TypeVarTuple, Unpack

from .compose import compose, starcompose
from .misc import starid


_A = TypeVar("_A")
_B = TypeVar("_B")
_C = TypeVar("_C")
_D = TypeVar("_D")
_E = TypeVar("_E")
_F = TypeVar("_F")
_G = TypeVar("_G")
_H = TypeVar("_H")
_T = TypeVar("_T")
_J = TypeVar("_J")
_P = TypeVarTuple("_P")
_Q = TypeVarTuple("_Q")
_X = TypeVarTuple("_X")
_Y = TypeVarTuple("_Y")
_Z = TypeVarTuple("_Z")
_K = TypeVarTuple("_K")


@overload
def pipe(value: _A, /) -> _A: ...


@overload
def pipe(value: _A, fn1: Callable[[_A], _B], /) -> _B: ...


@overload
def pipe(value: _A, fn1: Callable[[_A], _B], fn2: Callable[[_B], _C], /) -> _C: ...


@overload
def pipe(
    value: _A,
    fn1: Callable[[_A], _B],
    fn2: Callable[[_B], _C],
    fn3: Callable[[_C], _D],
    /,
) -> _D: ...


@overload
def pipe(
    value: _A,
    fn1: Callable[[_A], _B],
    fn2: Callable[[_B], _C],
    fn3: Callable[[_C], _D],
    fn4: Callable[[_D], _E],
    /,
) -> _E: ...


@overload
def pipe(
    value: _A,
    fn1: Callable[[_A], _B],
    fn2: Callable[[_B], _C],
    fn3: Callable[[_C], _D],
    fn4: Callable[[_D], _E],
    fn5: Callable[[_E], _F],
    /,
) -> _F: ...


@overload
def pipe(
    value: _A,
    fn1: Callable[[_A], _B],
    fn2: Callable[[_B], _C],
    fn3: Callable[[_C], _D],
    fn4: Callable[[_D], _E],
    fn5: Callable[[_E], _F],
    fn6: Callable[[_F], _G],
    /,
) -> _G: ...


@overload
def pipe(
    value: _A,
    fn1: Callable[[_A], _B],
    fn2: Callable[[_B], _C],
    fn3: Callable[[_C], _D],
    fn4: Callable[[_D], _E],
    fn5: Callable[[_E], _F],
    fn6: Callable[[_F], _G],
    fn7: Callable[[_G], _H],
    /,
) -> _H: ...


@overload
def pipe(
    value: _A,
    fn1: Callable[[_A], _B],
    fn2: Callable[[_B], _C],
    fn3: Callable[[_C], _D],
    fn4: Callable[[_D], _E],
    fn5: Callable[[_E], _F],
    fn6: Callable[[_F], _G],
    fn7: Callable[[_G], _H],
    fn8: Callable[[_H], _T],
    /,
) -> _T: ...


@overload
def pipe(
    value: _A,
    fn1: Callable[[_A], _B],
    fn2: Callable[[_B], _C],
    fn3: Callable[[_C], _D],
    fn4: Callable[[_D], _E],
    fn5: Callable[[_E], _F],
    fn6: Callable[[_F], _G],
    fn7: Callable[[_G], _H],
    fn8: Callable[[_H], _T],
    fn9: Callable[[_T], _J],
    /,
) -> _J: ...


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
def pipe2(values: tuple[_A, _B], /) -> tuple[_A, _B]: ...


@overload
def pipe2(values: tuple[_A, _B], fn1: Callable[[_A], Callable[[_B], _C]], /) -> _C: ...


@overload
def pipe2(
    values: tuple[_A, _B],
    fn1: Callable[[_A], Callable[[_B], _C]],
    fn2: Callable[[_C], _D],
    /,
) -> _D: ...


@overload
def pipe2(
    values: tuple[_A, _B],
    fn1: Callable[[_A], Callable[[_B], _C]],
    fn2: Callable[[_C], _D],
    fn3: Callable[[_D], _E],
    /,
) -> _E: ...


def pipe2(values: Any, /, *fns: Any) -> Any:
    return pipe(fns[0](values[0])(values[1]), *fns[1:]) if fns else values


def pipe3(values: Any, /, *fns: Any) -> Any:
    return pipe(fns[0](values[0])(values[1])(values[2]), *fns[1:]) if fns else values


@overload
def starpipe(args: tuple[Unpack[_P]], fn1: Callable[[Unpack[_P]], _B], /) -> _B: ...


@overload
def starpipe(
    args: tuple[Unpack[_P]], fn1: Callable[[Unpack[_P]], tuple[Unpack[_Q]]], fn2: Callable[[*_Q], _B], /
) -> _B: ...


@overload
def starpipe(
    args: tuple[Unpack[_P]],
    fn1: Callable[[Unpack[_P]], tuple[Unpack[_Q]]],
    fn2: Callable[[Unpack[_Q]], tuple[Unpack[_X]]],
    fn3: Callable[[Unpack[_X]], _B],
    /,
) -> _B: ...


@overload
def starpipe(
    args: tuple[Unpack[_P]],
    fn1: Callable[[Unpack[_P]], tuple[Unpack[_Q]]],
    fn2: Callable[[Unpack[_Q]], tuple[Unpack[_X]]],
    fn3: Callable[[Unpack[_X]], tuple[Unpack[_Y]]],
    fn4: Callable[[Unpack[_Y]], _B],
    /,
) -> _B: ...


@overload
def starpipe(
    args: tuple[Unpack[_P]],
    fn1: Callable[[Unpack[_P]], tuple[Unpack[_Q]]],
    fn2: Callable[[Unpack[_Q]], tuple[Unpack[_X]]],
    fn3: Callable[[Unpack[_X]], tuple[Unpack[_Y]]],
    fn4: Callable[[Unpack[_Y]], tuple[Unpack[_Z]]],
    fn5: Callable[[Unpack[_Z]], _B],
    /,
) -> _B: ...


@overload
def starpipe(
    args: tuple[Unpack[_P]],
    fn1: Callable[[Unpack[_P]], tuple[Unpack[_Q]]],
    fn2: Callable[[Unpack[_Q]], tuple[Unpack[_X]]],
    fn3: Callable[[Unpack[_X]], tuple[Unpack[_Y]]],
    fn4: Callable[[Unpack[_Y]], tuple[Unpack[_Z]]],
    fn5: Callable[[Unpack[_Z]], tuple[Unpack[_K]]],
    fn6: Callable[[Unpack[_K]], _B],
    /,
) -> _B: ...


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

    @overload
    def pipe(self: _A, fn1: Callable[[_A], _B], /) -> _B: ...

    @overload
    def pipe(self: _A, fn1: Callable[[_A], _B], fn2: Callable[[_B], _C], /) -> _C: ...

    @overload
    def pipe(self: _A, fn1: Callable[[_A], _B], fn2: Callable[[_B], _C], fn3: Callable[[_C], _D], /) -> _D: ...

    @overload
    def pipe(
        self: _A,
        fn1: Callable[[_A], _B],
        fn2: Callable[[_B], _C],
        fn3: Callable[[_C], _D],
        fn4: Callable[[_D], _E],
        /,
    ) -> _E: ...

    @overload
    def pipe(
        self: _A,
        fn1: Callable[[_A], _B],
        fn2: Callable[[_B], _C],
        fn3: Callable[[_C], _D],
        fn4: Callable[[_D], _E],
        fn5: Callable[[_E], _F],
        /,
    ) -> _F: ...

    @overload
    def pipe(
        self: _A,
        fn1: Callable[[_A], _B],
        fn2: Callable[[_B], _C],
        fn3: Callable[[_C], _D],
        fn4: Callable[[_D], _E],
        fn5: Callable[[_E], _F],
        fn6: Callable[[_F], _G],
        /,
    ) -> _G: ...

    def pipe(self, *args: Any) -> Any:
        """Pipe the left side object through the given functions."""
        return pipe(self, *args)


__all__ = ["PipeMixin", "pipe", "pipe2", "pipe3", "starpipe"]
