from typing import Any, Callable, Tuple, TypeVar

_A = TypeVar("_A")
_B = TypeVar("_B")
_TSource = TypeVar("_TSource")
_TResult = TypeVar("_TResult")


def identity(value: _A) -> _A:
    """Identity function.

    Returns value given as argument.
    """
    return value


def starid(*value: Any) -> Tuple[Any, ...]:
    return value


def flip(fn: Callable[[_A, _B], _TResult]) -> Callable[[_B, _A], _TResult]:
    """Flips the arguments for a function taking two arguments.

    Example:
        >>> fn(a, b) == flip(fn)(b, a)
    """

    def _flip(b: _B, a: _A) -> Any:
        return fn(a, b)

    return _flip


def snd(value: Tuple[Any, _TSource]) -> _TSource:
    """Return second argument of the tuple."""

    _, b = value
    return b


def fst(value: Tuple[_TSource, Any]) -> _TSource:
    """Return first argument of the tuple."""

    a, _ = value
    return a


__all__ = ["fst", "identity", "starid", "flip", "snd"]
