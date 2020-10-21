from typing import TypeVar, Any, Callable

from fslash.core import Result, Ok, Result_, Builder

TSource = TypeVar("TSource")
TResult = TypeVar("TResult")
TError = TypeVar("TError")


class ResultBuilder(Builder[Result_[TSource, TError], TSource]):
    def bind(self, xs: TSource, fn: Callable[[TSource], Result_[TResult, TError]]):
        return Result.bind(fn)(xs)

    def return_(self, x: TSource) -> Result_[TSource, TError]:
        return Ok(x)

    def return_from(self, xs: Result_[TSource, TError]) -> Result_[TSource, TError]:
        return xs

    def combine(self, xs: Result_[TSource, TError], ys: Result_[TSource, TError]) -> Result_[TSource, TError]:
        binder: Callable[[Any], Result_[TSource, TError]] = lambda _: ys
        return Result.bind(binder)(xs)


result: ResultBuilder[Any, Any] = ResultBuilder()


__all__ = ["result"]
