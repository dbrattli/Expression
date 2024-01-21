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
from typing import Any, TypeVar, TypeVarTuple, cast, overload

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


@overload
def pipe(__value: _A) -> _A:
    ...


@overload
def pipe(__value: _A, __fn1: Callable[[_A], _B]) -> _B:
    ...


@overload
def pipe(__value: _A, __fn1: Callable[[_A], _B], __fn2: Callable[[_B], _C]) -> _C:
    ...


@overload
def pipe(
    __value: _A,
    __fn1: Callable[[_A], _B],
    __fn2: Callable[[_B], _C],
    __fn3: Callable[[_C], _D],
) -> _D:
    ...


@overload
def pipe(
    __value: _A,
    __fn1: Callable[[_A], _B],
    __fn2: Callable[[_B], _C],
    __fn3: Callable[[_C], _D],
    __fn4: Callable[[_D], _E],
) -> _E:
    ...


@overload
def pipe(
    __value: _A,
    __fn1: Callable[[_A], _B],
    __fn2: Callable[[_B], _C],
    __fn3: Callable[[_C], _D],
    __fn4: Callable[[_D], _E],
    __fn5: Callable[[_E], _F],
) -> _F:
    ...


@overload
def pipe(
    __value: _A,
    __fn1: Callable[[_A], _B],
    __fn2: Callable[[_B], _C],
    __fn3: Callable[[_C], _D],
    __fn4: Callable[[_D], _E],
    __fn5: Callable[[_E], _F],
    __fn6: Callable[[_F], _G],
) -> _G:
    ...


@overload
def pipe(
    __value: _A,
    __fn1: Callable[[_A], _B],
    __fn2: Callable[[_B], _C],
    __fn3: Callable[[_C], _D],
    __fn4: Callable[[_D], _E],
    __fn5: Callable[[_E], _F],
    __fn6: Callable[[_F], _G],
    __fn7: Callable[[_G], _H],
) -> _H:
    ...


@overload
def pipe(
    __value: _A,
    __fn1: Callable[[_A], _B],
    __fn2: Callable[[_B], _C],
    __fn3: Callable[[_C], _D],
    __fn4: Callable[[_D], _E],
    __fn5: Callable[[_E], _F],
    __fn6: Callable[[_F], _G],
    __fn7: Callable[[_G], _H],
    __fn8: Callable[[_H], _T],
) -> _T:
    ...


@overload
def pipe(
    __value: _A,
    __fn1: Callable[[_A], _B],
    __fn2: Callable[[_B], _C],
    __fn3: Callable[[_C], _D],
    __fn4: Callable[[_D], _E],
    __fn5: Callable[[_E], _F],
    __fn6: Callable[[_F], _G],
    __fn7: Callable[[_G], _H],
    __fn8: Callable[[_H], _T],
    __fn9: Callable[[_T], _J],
) -> _J:
    ...


def pipe(__value: Any, *fns: Callable[[Any], Any]) -> Any:
    """Functional pipe (`|>`).

    Allows the use of function argument on the left side of the
    function.

    Example:
        >>> pipe(x, fn) == __fn(x)  # Same as x |> fn
        >>> pipe(x, fn, gn) == gn(fn(x))  # Same as x |> fn |> gn
        ...
    """
    return compose(*fns)(__value)


@overload
def pipe2(__values: tuple[_A, _B]) -> tuple[_A, _B]:
    ...


@overload
def pipe2(__values: tuple[_A, _B], __fn1: Callable[[_A], Callable[[_B], _C]]) -> _C:
    ...


@overload
def pipe2(
    __values: tuple[_A, _B],
    __fn1: Callable[[_A], Callable[[_B], _C]],
    __fn2: Callable[[_C], _D],
) -> _D:
    ...


@overload
def pipe2(
    __values: tuple[_A, _B],
    __fn1: Callable[[_A], Callable[[_B], _C]],
    __fn2: Callable[[_C], _D],
    __fn3: Callable[[_D], _E],
) -> _E:
    ...


def pipe2(__values: Any, *fns: Any) -> Any:
    return pipe(fns[0](__values[0])(__values[1]), *fns[1:]) if fns else __values


def pipe3(__values: Any, *fns: Any) -> Any:
    return pipe(fns[0](__values[0])(__values[1])(__values[2]), *fns[1:]) if fns else __values


@overload
def starpipe(__args: tuple[*_P], __fn1: Callable[[*_P], _B]) -> _B:
    ...


@overload
def starpipe(__args: tuple[*_P], __fn1: Callable[[*_P], tuple[*_Q]], __fn2: Callable[[*_Q], _B]) -> _B:
    ...


@overload
def starpipe(
    __args: tuple[*_P],
    __fn1: Callable[[*_P], tuple[*_Q]],
    __fn2: Callable[[*_Q], tuple[*_X]],
    __fn3: Callable[[*_X], _B],
) -> _B:
    ...


@overload
def starpipe(
    __args: tuple[*_P],
    __fn1: Callable[[*_P], tuple[*_Q]],
    __fn2: Callable[[*_Q], tuple[*_X]],
    __fn3: Callable[[*_X], tuple[*_Y]],
    __fn4: Callable[[*_Y], _B],
) -> _B:
    ...


def starpipe(__args: Any, *__fns: Callable[..., Any]) -> Any:
    """Functional pipe_n (`||>`, `||>`, `|||>`, etc).

    Allows the use of function arguments on the left side of the
    function. Calls the function with tuple arguments unpacked.

    Example:
        >>> starpipe((x, y), fn) == fn(x, y)  # Same as (x, y) ||> fn
        >>> starpipe((x, y), fn, gn) == gn(*fn(x))  # Same as (x, y) ||> fn |> gn
        ...
    """
    # Cast since unpacked arguments be used with TypeVarTuple
    _starid = cast(Callable[..., Any], starid)
    fn = __fns[0] if len(__fns) else _starid

    return starcompose(*__fns[1:])(fn(*__args))


class PipeMixin:
    """A pipe mixin class that enabled a class to use pipe fluently."""

    @overload
    def pipe(self: _A, __fn1: Callable[[_A], _B]) -> _B:
        ...

    @overload
    def pipe(self: _A, __fn1: Callable[[_A], _B], __fn2: Callable[[_B], _C]) -> _C:
        ...

    @overload
    def pipe(
        self: _A,
        __fn1: Callable[[_A], _B],
        __fn2: Callable[[_B], _C],
        __fn3: Callable[[_C], _D],
    ) -> _D:
        ...

    @overload
    def pipe(
        self: _A,
        __fn1: Callable[[_A], _B],
        __fn2: Callable[[_B], _C],
        __fn3: Callable[[_C], _D],
        __fn4: Callable[[_D], _E],
    ) -> _E:
        ...

    @overload
    def pipe(
        self: _A,
        __fn1: Callable[[_A], _B],
        __fn2: Callable[[_B], _C],
        __fn3: Callable[[_C], _D],
        __fn4: Callable[[_D], _E],
        __fn5: Callable[[_E], _F],
    ) -> _F:
        ...

    @overload
    def pipe(
        self: _A,
        __fn1: Callable[[_A], _B],
        __fn2: Callable[[_B], _C],
        __fn3: Callable[[_C], _D],
        __fn4: Callable[[_D], _E],
        __fn5: Callable[[_E], _F],
        __fn6: Callable[[_F], _G],
    ) -> _G:
        ...

    def pipe(self, *args: Any) -> Any:
        """Pipe the left side object through the given functions."""
        return pipe(self, *args)


__all__ = ["pipe", "pipe2", "pipe3", "PipeMixin", "starpipe"]
