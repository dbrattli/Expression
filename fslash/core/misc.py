from typing import TypeVar, Tuple, Any

A = TypeVar("A")


def identity(value: A) -> A:
    """Identity function.

    Returns value given as argument.
    """
    return value


def starid(*value: Any) -> Tuple:
    return value


def flip(fn):
    """Flips the arguments for a function taking two arguments.

    Example:
        >>> fn(a, b) == flip(fn(b, a)) ==
    """
    lambda a, b: fn(b, a)


__all__ = ["identity", "starid", "flip"]
