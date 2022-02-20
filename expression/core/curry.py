from typing import Any, Callable, Literal, Tuple, TypeVar, overload

from typing_extensions import Concatenate, ParamSpec

_P = ParamSpec("_P")
_A = TypeVar("_A")
_B = TypeVar("_B")
_C = TypeVar("_C")
_D = TypeVar("_D")
_E = TypeVar("_E")


@overload
def curried(args: Literal[0]) -> Callable[[Callable[_P, _B]], Callable[_P, _B]]:
    ...


@overload
def curried(
    args: Literal[1],
) -> Callable[[Callable[Concatenate[_A, _P], _B]], Callable[[_A], Callable[_P, _B]]]:
    ...


@overload
def curried(
    args: Literal[2],
) -> Callable[
    [Callable[Concatenate[_A, _B, _P], _C]],
    Callable[[_A], Callable[[_B], Callable[_P, _C]]],
]:
    ...


@overload
def curried(
    args: Literal[3],
) -> Callable[
    [Callable[Concatenate[_A, _B, _C, _P], _D]],
    Callable[[_A], Callable[[_B], Callable[[_C], Callable[_P, _D]]]],
]:
    ...


@overload
def curried(
    args: Literal[4],
) -> Callable[
    [Callable[Concatenate[_A, _B, _C, _D, _P], _E]],
    Callable[[_A], Callable[[_B], Callable[[_C], Callable[[_D], Callable[_P, _E]]]]],
]:
    ...


def curried(args: int) -> Callable[..., Any]:
    """A curry decorator.

    Makes a function curried.

    Args:
        args: The number of args to curry from the start of the function

    Example:
        @curried(1)
        def add(a: int, b: int) -> int:
            return a + b

        assert add(3)(4) == 7
    """

    def _curry(
        args: Tuple[Any, ...], arity: int, fn: Callable[..., Any]
    ) -> Callable[..., Any]:
        def wrapper(*arg: Any, **kw: Any) -> Any:
            if arity == 1:
                return fn(*args, *arg, **kw)
            return _curry(args + arg, arity - 1, fn)

        return wrapper

    def wrapper(fn: Callable[..., Any]) -> Callable[..., Any]:
        return _curry((), args + 1, fn)

    return wrapper


__all__ = ["curried"]
