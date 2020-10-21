from typing import Any, Callable, Tuple, TypeVar

A = TypeVar("A")
B = TypeVar("B")
TSource = TypeVar("TSource")


def identity(value: A) -> A:
    """Identity function.

    Returns value given as argument.
    """
    return value


def starid(*value: Any) -> Tuple[Any, ...]:
    return value


def flip(fn: Callable[[A, B], Any]) -> Callable[[B, A], Any]:
    """Flips the arguments for a function taking two arguments.

    Example:
        >>> fn(a, b) == flip(fn(b, a)) ==
    """

    def _(b: B, a: A) -> Any:
        return fn(a, b)

    return _


__all__ = ["identity", "starid", "flip"]
