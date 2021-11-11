import inspect
from functools import partial, wraps
from typing import Any, Callable, Tuple, TypeVar

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")
D = TypeVar("D")
E = TypeVar("E")


def curried(fn: Callable[..., Any]) -> Callable[..., Any]:
    """A curry decorator.

    Makes a function curryable. Note that the function will loose it's
    typing hints so you will need to provide typed overloads for the
    intended uses of the function you are decorating.

    Example:
        @overload
        def add(a: int, b: int) -> int:
            ...

        @overload
        def add(a: int) -> Callable[[int], int]:
            ...

        @curried
        def add(a: int, b: int) -> int:
            return a + b

        assert add(3, 4) == 7
        assert add(3)(4) == 7

    """
    spec = inspect.getfullargspec(fn)
    # Number of arguments needed is length of args and kwargs - default args
    count = len(spec.args) + len(spec.kwonlyargs) - len(spec.kwonlydefaults or [])

    @wraps(fn)
    def wrapper(*args: Any, **kw: Any) -> Any:
        if len(args) + len(kw) >= count:
            return fn(*args, **kw)
        return curried(partial(fn, *args, **kw))

    return wrapper


def curry1of2(fn: Callable[[A, B], C]) -> Callable[[A], Callable[[B], C]]:
    """Curry 1 of 2 arguments."""
    return lambda a: lambda b: fn(a, b)


def curry2of2(fn: Callable[[A, B], C]) -> Callable[[A], Callable[[B], Callable[[], C]]]:
    """Curry 2 of 2 arguments."""
    return lambda a: lambda b: lambda: fn(a, b)


def curry1of3(fn: Callable[[A, B, C], D]) -> Callable[[A], Callable[[B, C], D]]:
    """Curry 1 of 3 arguments."""
    return lambda a: lambda b, c: fn(a, b, c)


def curry2of3(fn: Callable[[A, B, C], D]) -> Callable[[A], Callable[[B], Callable[[C], D]]]:
    """Curry 2 of 3 arguments."""
    return lambda a: lambda b: lambda c: fn(a, b, c)


def curry3of3(fn: Callable[[A, B, C], D]) -> Callable[[A], Callable[[B], Callable[[C], Callable[[], D]]]]:
    """Curry 3 of 3 arguments."""
    return lambda a: lambda b: lambda c: lambda: fn(a, b, c)


def curry1of4(fn: Callable[[A, B, C, D], E]) -> Callable[[A], Callable[[B, C, C], E]]:
    """Curry 1 of 4 arguments."""
    return lambda a: lambda b, c, d: fn(a, b, c, d)


def curry2of4(fn: Callable[[A, B, C, D], E]) -> Callable[[A], Callable[[B], Callable[[C, D], E]]]:
    """Curry 2 of 4 arguments."""
    return lambda a: lambda b: lambda c, d: fn(a, b, c, d)


def curry3of4(fn: Callable[[A, B, C, D], E]) -> Callable[[A], Callable[[B], Callable[[C], Callable[[D], E]]]]:
    """Curry 3 of 4 arguments."""
    return lambda a: lambda b: lambda c: lambda d: fn(a, b, c, d)


def curry4of4(
    fn: Callable[[A, B, C, D], E]
) -> Callable[[A], Callable[[B], Callable[[C], Callable[[D], Callable[[], D]]]]]:
    """Curry 4 of 4 arguments."""
    return lambda a: lambda b: lambda c: lambda d: lambda: fn(a, b, c, d)


__all__ = ["curried"]
