from typing import Any, Callable, TypeVar

from expression.core import Builder, Ok, Result, pipe, result

TSource = TypeVar("TSource")
TResult = TypeVar("TResult")
TError = TypeVar("TError")


class ResultBuilder(Builder[Result[TSource, TError], TSource]):
    def bind(
        self, xs: Result[TSource, TError], fn: Callable[[TSource], Result[TResult, TError]]
    ) -> Result[TResult, TError]:
        return pipe(xs, result.bind(fn))

    def return_(self, x: TSource) -> Result[TSource, TError]:
        return Ok(x)

    def return_from(self, xs: Result[TSource, TError]) -> Result[TSource, TError]:
        return xs

    def combine(self, xs: Result[TSource, TError], ys: Result[TSource, TError]) -> Result[TSource, TError]:
        return xs.bind(lambda _: ys)

    def zero(self) -> Result[TSource, TError]:
        raise NotImplementedError


result_effect: ResultBuilder[Any, Any] = ResultBuilder()


__all__ = ["result_effect"]
