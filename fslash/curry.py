from functools import partial


def curried(fn):
    """A curry decorator.

    Makes functions curryable. Note that the function will loose it's
    typing hints so use of it is not really recommented. Provided for
    completeness.

    Example:
        >>> @curried
        ... def add(a, b): return a + b
        ...
        >>> add(3)(4)
        7
    """
    def wrapper(*args, **kw):
        try:
            return fn(*args, **kw)
        except TypeError:
            return partial(fn, *args, **kw)
    return wrapper


__all__ = ["curried"]
