from typing import Any, Callable, TypeVar

from expression.core import Builder, Ok, Result, pipe, result

TSource = TypeVar("TSource")
TResult = TypeVar("TResult")
TError = TypeVar("TError")


class ResultBuilder(Builder[Result[TSource, TError], TSource]):
    def bind(self, xs: TSource, fn: Callable[[TSource], Result[TResult, TError]]) -> Result[TResult, TError]:
        return result.bind(fn)(xs)

    def return_(self, x: TSource) -> Result[TSource, TError]:
        return Ok(x)

    def return_from(self, xs: Result[TSource, TError]) -> Result[TSource, TError]:
        return xs

    def combine(self, xs: Result[TSource, TError], ys: Result[TSource, TError]) -> Result[TSource, TError]:
        binder: Callable[[Any], Result[TSource, TError]] = lambda _: ys
        return pipe(xs, result.bind(binder))


result_effect: ResultBuilder[Any, Any] = ResultBuilder()


__all__ = ["result_effect"]
