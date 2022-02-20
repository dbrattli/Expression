from typing import Any, Callable, Literal, Tuple, TypeVar, overload

from typing_extensions import Concatenate, ParamSpec

_P = ParamSpec("_P")
_A = TypeVar("_A")
_B = TypeVar("_B")
_C = TypeVar("_C")
_D = TypeVar("_D")
_E = TypeVar("_E")

_Arity = Literal[0, 1, 2, 3, 4]


def _curry(
    args: Tuple[Any, ...], arity: int, fun: Callable[..., Any]
) -> Callable[..., Any]:
    def wrapper(*arg: Any, **kw: Any) -> Any:
        if arity == 1:
            return fun(*args, *arg, **kw)
        return _curry(args + arg, arity - 1, fun)

    return wrapper


@overload
def curry(num_args: Literal[0]) -> Callable[[Callable[_P, _B]], Callable[_P, _B]]:
    ...


@overload
def curry(
    num_args: Literal[1],
) -> Callable[[Callable[Concatenate[_A, _P], _B]], Callable[[_A], Callable[_P, _B]]]:
    ...


@overload
def curry(
    num_args: Literal[2],
) -> Callable[
    [Callable[Concatenate[_A, _B, _P], _C]],
    Callable[[_A], Callable[[_B], Callable[_P, _C]]],
]:
    ...


@overload
def curry(
    num_args: Literal[3],
) -> Callable[
    [Callable[Concatenate[_A, _B, _C, _P], _D]],
    Callable[[_A], Callable[[_B], Callable[[_C], Callable[_P, _D]]]],
]:
    ...


@overload
def curry(
    num_args: Literal[4],
) -> Callable[
    [Callable[Concatenate[_A, _B, _C, _D, _P], _E]],
    Callable[[_A], Callable[[_B], Callable[[_C], Callable[[_D], Callable[_P, _E]]]]],
]:
    ...


def curry(num_args: _Arity) -> Callable[..., Any]:
    """A curry decorator.

    Makes a function curried.

    Args:
        num_args: The number of args to curry from the start of the function

    Example:
        @curried(1)
        def add(a: int, b: int) -> int:
            return a + b

        assert add(3)(4) == 7
    """

    def wrapper(fun: Callable[..., Any]) -> Callable[..., Any]:
        return _curry((), num_args + 1, fun)

    return wrapper


@overload
def curry_flipped(
    num_args: Literal[0],
) -> Callable[[Callable[_P, _B]], Callable[_P, _B]]:
    ...


@overload
def curry_flipped(
    num_args: Literal[1],
) -> Callable[[Callable[Concatenate[_A, _P], _B]], Callable[_P, Callable[[_A], _B]]]:
    ...


@overload
def curry_flipped(
    num_args: Literal[2],
) -> Callable[
    [Callable[Concatenate[_A, _B, _P], _C]],
    Callable[_P, Callable[[_A], Callable[[_B], _C]]],
]:
    ...


@overload
def curry_flipped(
    num_args: Literal[3],
) -> Callable[
    [Callable[Concatenate[_A, _B, _C, _P], _D]],
    Callable[_P, Callable[[_A], Callable[[_B], Callable[[_C], _D]]]],
]:
    ...


@overload
def curry_flipped(
    num_args: Literal[4],
) -> Callable[
    [Callable[Concatenate[_A, _B, _C, _D, _P], _E]],
    Callable[_P, Callable[[_A], Callable[[_B], Callable[[_C], Callable[[_D], _E]]]]],
]:
    ...


def curry_flipped(
    num_args: _Arity,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def _wrap_fun(fun: Callable[..., Any]) -> Callable[..., Any]:
        def _wrap_args(*args: Any, **kwargs: Any) -> Callable[..., Any]:
            def _wrap_curried(*curry_args: Any) -> Any:
                return fun(*curry_args, *args, **kwargs)

            return _curry((), num_args, _wrap_curried)

        return _wrap_args

    return _wrap_fun


__all__ = ["curry", "curry_flipped"]
