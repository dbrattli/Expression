from collections.abc import Callable
from typing import Any


def identity[A](value: A) -> A:
    """Identity function.

    Returns value given as argument.
    """
    return value


def starid[*P](*value: *P) -> tuple[*P]:
    return value


def flip[TResult, A, B](fn: Callable[[A, B], TResult]) -> Callable[[B, A], TResult]:
    """Flips the arguments for a function taking two arguments.

    Example:
        >>> fn(a, b) == flip(fn)(b, a)
    """

    def _flip(b: B, a: A) -> Any:
        return fn(a, b)

    return _flip


def snd[TSource](value: tuple[Any, TSource]) -> TSource:
    """Return second argument of the tuple."""
    _, b = value
    return b


def fst[TSource](value: tuple[TSource, Any]) -> TSource:
    """Return first argument of the tuple."""
    a, _ = value
    return a


__all__ = ["flip", "fst", "identity", "snd", "starid"]
