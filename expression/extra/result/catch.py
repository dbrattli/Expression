from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import Any, Never, ParamSpec, Protocol, cast, overload

from typing_extensions import TypeVar

from expression.core import Error, Ok, Result


# Use typing_extensions.TypeVar because type parameter defaults require Python 3.13 syntax.
# Keep Python 3.12 support while defaulting to Never so plain returns do not infer an Unknown error channel.
_TSource = TypeVar("_TSource")
_TExisting = TypeVar("_TExisting", default=Never)
_TError = TypeVar("_TError", bound=Exception, covariant=True, default=Exception)
_P = ParamSpec("_P")


class _Catch(Protocol[_TError]):
    def __call__(
        self, fn: Callable[_P, _TSource | Result[_TSource, _TExisting]]
    ) -> Callable[_P, Result[_TSource, _TExisting | _TError]]: ...


@overload
def catch[TError: Exception](*, exception: type[TError]) -> _Catch[TError]: ...


@overload
def catch(
    f: Callable[_P, _TSource | Result[_TSource, _TExisting]], *, exception: type[_TError]
) -> Callable[_P, Result[_TSource, _TExisting | _TError]]: ...


def catch[TError: Exception](
    f: Callable[..., Any] | None = None, *, exception: type[TError]
) -> _Catch[TError] | Callable[..., Result[Any, Any]]:
    """Catch the selected exception, preserving arguments and existing Result values."""

    def decorator(
        fn: Callable[_P, _TSource | Result[_TSource, _TExisting]],
    ) -> Callable[_P, Result[_TSource, _TExisting | TError]]:
        @wraps(fn)
        def wrapper(*args: _P.args, **kwargs: _P.kwargs) -> Result[_TSource, _TExisting | TError]:
            try:
                out = fn(*args, **kwargs)
            except exception as exn:
                return Error(exn)
            else:
                if isinstance(out, (Ok, Error)):
                    return cast(Result[_TSource, _TExisting], out)

                return Ok(out)

        return wrapper

    if f is not None:
        return decorator(f)

    return decorator


__all__ = ["catch"]
