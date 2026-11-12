from collections.abc import Callable


def identity[A](value: A) -> A:
    """Identity function.

    Returns value given as argument.
    """
    return value


def starid[*P](*value: *P) -> tuple[*P]:
    return value


def flip[A, B, TResult](fn: Callable[[A, B], TResult]) -> Callable[[B, A], TResult]:
    """Flips the arguments for a function taking two arguments.

    Example:
        >>> fn(a, b) == flip(fn)(b, a)
    """

    def _flip(b: B, a: A) -> TResult:
        return fn(a, b)

    return _flip


def snd[TSource](value: tuple[object, TSource]) -> TSource:
    """Return second argument of the tuple."""
    _, b = value
    return b


def fst[TSource](value: tuple[TSource, object]) -> TSource:
    """Return first argument of the tuple."""
    a, _ = value
    return a


__all__ = ["flip", "fst", "identity", "snd", "starid"]
