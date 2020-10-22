import inspect
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
    spec = inspect.getfullargspec(fn)
    # Number of arguments needed is length of args and kwargs - default args
    count = len(spec.args) + len(spec.kwonlyargs) - len(spec.kwonlydefaults or [])

    @wraps(fn)
    def wrapper(*args: Any, **kw: Any) -> Any:
        if len(args) + len(kw) >= count:
            return fn(*args, **kw)
        return curried(partial(fn, *args, **kw))

    return wrapper


__all__ = ["curried"]
