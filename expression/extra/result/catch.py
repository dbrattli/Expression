from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar, cast, overload

from expression.core import Error, Ok, Result


_TSource = TypeVar("_TSource")
_TError = TypeVar("_TError", bound=Exception)
_TError_ = TypeVar("_TError_", bound=Exception)


@overload
def catch(
    exception: type[_TError_],
) -> Callable[
    [Callable[..., _TSource | Result[_TSource, _TError]]],
    Callable[..., Result[_TSource, _TError | _TError_]],
]: ...


@overload
def catch(f: Callable[..., _TSource], *, exception: type[_TError]) -> Callable[..., Result[_TSource, _TError]]: ...


def catch(  # type: ignore
    f: Callable[..., _TSource] | None = None, *, exception: type[_TError]
) -> Callable[
    [Callable[..., _TSource]],
    Callable[..., Result[_TSource, _TError]] | Result[_TSource, _TError],
]:
    def decorator(fn: Callable[..., _TSource]) -> Callable[..., Result[_TSource, _TError]]:
        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Result[_TSource, _TError]:
            try:
                out = fn(*args, **kwargs)
            except exception as exn:
                return Error(cast(_TError, exn))
            else:
                if isinstance(out, Result):
                    return cast(Result[_TSource, _TError], out)

                return Ok(out)

        return wrapper

    if f is not None:
        return decorator(f)

    return decorator


__all__ = ["catch"]
