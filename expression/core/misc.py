from typing import Any, Callable, Tuple, TypeVar

A = TypeVar("A")
B = TypeVar("B")
TSource = TypeVar("TSource")
TResult = TypeVar("TResult")
Base = TypeVar("Base")
Derived = TypeVar("Derived")


def identity(value: A) -> A:
    """Identity function.

    Returns value given as argument.
    """
    return value


def starid(*value: Any) -> Tuple[Any, ...]:
    return value


def flip(fn: Callable[[A, B], TResult]) -> Callable[[B, A], TResult]:
    """Flips the arguments for a function taking two arguments.

    Example:
        >>> fn(a, b) == flip(fn)(b, a)
    """

    def _flip(b: B, a: A) -> Any:
        return fn(a, b)

    return _flip


def snd(value: Tuple[Any, TSource]) -> TSource:
    """Return second argument of the tuple."""

    _, b = value
    return b


def fst(value: Tuple[TSource, Any]) -> TSource:
    """Return first argument of the tuple."""

    a, _ = value
    return a


__all__ = ["fst", "identity", "starid", "flip", "snd"]
