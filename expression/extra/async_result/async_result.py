from typing import Callable, Coroutine, Any, TypeVar
from expression import Result
from expression.effect.async_result import async_result

_TSource = TypeVar("_TSource")
_TResult = TypeVar("_TResult")
_TError = TypeVar("_TError")


def bind(
    mapper: Callable[[_TSource], Coroutine[Any, Any, Result[_TResult, Any]]],
) -> Callable[[Result[_TSource, _TError]], Coroutine[Any, Any, Result[_TResult, _TError]]]:
    async def wrapped(result: Result[_TSource, _TError]) -> Result[_TResult, _TError]:
        return await async_result.bind(result, mapper)

    return wrapped


__all__ = ["bind"]
