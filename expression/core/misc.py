from collections.abc import Callable
from typing import Any, TypeVar

from typing_extensions import TypeVarTuple, Unpack


_A = TypeVar("_A")
_B = TypeVar("_B")
_P = TypeVarTuple("_P")
_TSource = TypeVar("_TSource")
_TResult = TypeVar("_TResult")


def identity(value: _A) -> _A:
    """Identity function.

    Returns value given as argument.
    """
    return value


def starid(*value: Unpack[_P]) -> tuple[Unpack[_P]]:
    return value


def flip(fn: Callable[[_A, _B], _TResult]) -> Callable[[_B, _A], _TResult]:
    """Flips the arguments for a function taking two arguments.

    Example:
        >>> fn(a, b) == flip(fn)(b, a)
    """

    def _flip(b: _B, a: _A) -> Any:
        return fn(a, b)

    return _flip


def snd(value: tuple[Any, _TSource]) -> _TSource:
    """Return second argument of the tuple."""
    _, b = value
    return b


def fst(value: tuple[_TSource, Any]) -> _TSource:
    """Return first argument of the tuple."""
    a, _ = value
    return a


__all__ = ["fst", "identity", "starid", "flip", "snd"]
