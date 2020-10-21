from functools import partial, wraps
from typing import Any, Callable


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

    @wraps(fn)
    def wrapper(*args: Any, **kw: Any) -> Any:
        try:
            return fn(*args, **kw)
        except TypeError:
            return partial(fn, *args, **kw)

    return wrapper


__all__ = ["curried"]
