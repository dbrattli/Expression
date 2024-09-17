from collections.abc import Callable
from functools import reduce
from typing import Any, TypeVar, overload

from typing_extensions import TypeVarTuple, Unpack


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
_X = TypeVarTuple("_X")
_Y = TypeVarTuple("_Y")
_Z = TypeVarTuple("_Z")


@overload
def compose() -> Callable[[_A], _A]: ...


@overload
def compose(__fn1: Callable[[_A], _B]) -> Callable[[_A], _B]: ...


@overload
def compose(__fn1: Callable[[_A], _B], __fn2: Callable[[_B], _C]) -> Callable[[_A], _C]: ...


@overload
def compose(__fn1: Callable[[_A], _B], __fn2: Callable[[_B], _C], __fn3: Callable[[_C], _D]) -> Callable[[_A], _D]: ...


@overload
def compose(
    fn1: Callable[[_A], _B],
    fn2: Callable[[_B], _C],
    fn3: Callable[[_C], _D],
    fn4: Callable[[_D], _E],
    /,
) -> Callable[[_A], _E]: ...


@overload
def compose(
    fn1: Callable[[_A], _B],
    fn2: Callable[[_B], _C],
    fn3: Callable[[_C], _D],
    fn4: Callable[[_D], _E],
    fn5: Callable[[_E], _F],
    /,
) -> Callable[[_A], _F]: ...


@overload
def compose(
    fn1: Callable[[_A], _B],
    fn2: Callable[[_B], _C],
    fn3: Callable[[_C], _D],
    fn4: Callable[[_D], _E],
    fn5: Callable[[_E], _F],
    fn6: Callable[[_F], _G],
    /,
) -> Callable[[_A], _G]: ...


@overload
def compose(
    fn1: Callable[[_A], _B],
    fn2: Callable[[_B], _C],
    fn3: Callable[[_C], _D],
    fn4: Callable[[_D], _E],
    fn5: Callable[[_E], _F],
    fn6: Callable[[_F], _G],
    fn7: Callable[[_G], _H],
    /,
) -> Callable[[_A], _H]: ...


@overload
def compose(
    fn1: Callable[[_A], _B],
    fn2: Callable[[_B], _C],
    fn3: Callable[[_C], _D],
    fn4: Callable[[_D], _E],
    fn5: Callable[[_E], _F],
    fn6: Callable[[_F], _G],
    fn7: Callable[[_G], _H],
    fn8: Callable[[_H], _T],
    /,
) -> Callable[[_A], _T]: ...


@overload
def compose(
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
) -> Callable[[_A], _J]: ...


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
def starcompose(fn1: Callable[[Unpack[_P]], _A], /) -> Callable[[Unpack[_P]], _A]: ...


@overload
def starcompose(
    fn1: Callable[[Unpack[_P]], tuple[Unpack[_Y]]], fn2: Callable[[Unpack[_Y]], _B], /
) -> Callable[[Unpack[_P]], _B]: ...


@overload
def starcompose(
    fn1: Callable[[Unpack[_P]], tuple[Unpack[_Y]]],
    fn2: Callable[[Unpack[_Y]], tuple[Unpack[_Z]]],
    fn3: Callable[[Unpack[_Z]], _C],
    /,
) -> Callable[[Unpack[_P]], _C]: ...


@overload
def starcompose(
    fn1: Callable[[Unpack[_P]], tuple[Unpack[_Y]]],
    fn2: Callable[[Unpack[_Y]], tuple[Unpack[_Z]]],
    fn3: Callable[[Unpack[_Z]], tuple[Unpack[_X]]],
    fn4: Callable[[Unpack[_X]], _D],
    /,
) -> Callable[[Unpack[_P]], _D]: ...


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
