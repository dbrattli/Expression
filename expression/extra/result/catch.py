from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import Any, cast, overload

from expression.core import Error, Ok, Result


@overload
def catch[TError_: Exception, TSource, TError: Exception](
    exception: type[TError_],
) -> Callable[
    [Callable[..., TSource | Result[TSource, TError]]],
    Callable[..., Result[TSource, TError | TError_]],
]: ...


@overload
def catch[TSource, TError: Exception](
    f: Callable[..., TSource], *, exception: type[TError]
) -> Callable[..., Result[TSource, TError]]: ...


def catch[TSource, TError: Exception](  # type: ignore
    f: Callable[..., TSource] | None = None, *, exception: type[TError]
) -> Callable[
    [Callable[..., TSource]],
    Callable[..., Result[TSource, TError]] | Result[TSource, TError],
]:
    def decorator(fn: Callable[..., TSource]) -> Callable[..., Result[TSource, TError]]:
        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Result[TSource, TError]:
            try:
                out = fn(*args, **kwargs)
            except exception as exn:
                return Error(cast(TError, exn))
            else:
                if isinstance(out, (Ok, Error)):
                    return cast(Result[TSource, TError], out)

                return Ok(out)

        return wrapper

    if f is not None:
        return decorator(f)

    return decorator


__all__ = ["catch"]
