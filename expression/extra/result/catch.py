from functools import wraps
from typing import Any, Callable, Optional, Type, TypeVar, Union, cast, overload

from expression.core import Error, Ok, Result

TSource = TypeVar("TSource")
TError = TypeVar("TError", bound=Exception)
TError_ = TypeVar("TError_", bound=Exception)


@overload
def catch(
    exception: Type[TError_],
) -> Callable[
    [Callable[..., Union[TSource, Result[TSource, TError]]]], Callable[..., Result[TSource, Union[TError, TError_]]]
]:
    ...


@overload
def catch(f: Callable[..., TSource], *, exception: Type[TError]) -> Callable[..., Result[TSource, TError]]:
    ...


def catch(  # type: ignore
    f: Optional[Callable[..., TSource]] = None, *, exception: Type[TError]
) -> Callable[[Callable[..., TSource]], Union[Callable[..., Result[TSource, TError]], Result[TSource, TError]]]:
    def decorator(fn: Callable[..., TSource]) -> Callable[..., Result[TSource, TError]]:
        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Result[TSource, TError]:
            try:
                out = fn(*args, **kwargs)
            except exception as exn:
                return Error(cast("TError", exn))
            else:
                if isinstance(out, Result):
                    return cast(Result[TSource, TError], out)

                return Ok(out)

        return wrapper

    if f is not None:
        return decorator(f)

    return decorator


__all__ = ["catch"]
