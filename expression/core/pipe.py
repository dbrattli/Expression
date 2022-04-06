from typing import Any, Callable, Tuple, TypeVar, overload

from .compose import compose
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
    """Functional pipe (`|>`)

    Allows the use of function argument on the left side of the
    function.

    Example:
        >>> pipe(x, fn) == __fn(x)  # Same as x |> fn
        >>> pipe(x, fn, gn) == gn(fn(x))  # Same as x |> fn |> gn
        ...
    """

    return compose(*fns)(__value)


@overload
def pipe2(__values: Tuple[_A, _B]) -> Tuple[_A, _B]:
    ...


@overload
def pipe2(__values: Tuple[_A, _B], __fn1: Callable[[_A, _B], _C]) -> _C:
    ...


@overload
def pipe2(
    __values: Tuple[_A, _B], __fn1: Callable[[_A, _B], _C], __fn2: Callable[[_C], _D]
) -> _D:
    ...


@overload
def pipe2(
    __values: Tuple[_A, _B],
    __fn1: Callable[[_A, _B], _C],
    __fn2: Callable[[_C], _D],
    __fn3: Callable[[_D], _E],
) -> _E:
    ...


def pipe2(__values: Any, *fns: Any) -> Any:
    return starpipe(__values, *fns)


def pipe3(args: Any, *fns: Any) -> Any:
    return starpipe(args, *fns)


def starpipe(args: Any, *fns: Callable[..., Any]):
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
