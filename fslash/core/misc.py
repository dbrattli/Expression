from typing import TypeVar, Tuple, Any

A = TypeVar("A")
TSource = TypeVar("TSource")


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


class ComputationalExpressionExit(Exception):
    """An error that will exit any computational expression.

    We use this to detect if sub-generators causes an exit, since
    yielding nothing will be silently ignored.
    """


__all__ = ["identity", "starid", "flip", "ComputationalExpressionExit"]
