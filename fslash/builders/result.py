from typing import TypeVar, Any

from fslash.core import Result, Ok, Result_, Builder

TSource = TypeVar("TSource")
TResult = TypeVar("TResult")
TError = TypeVar("TError")


class ResultBuilder(Builder[Result_[TSource, TError], TSource]):
    def bind(self, xs, fn):
        return Result.bind(fn)(xs)

    def return_(self, x):
        return Ok(x)

    def return_from(self, xs):
        return xs

    def combine(self, xs, ys):
        return Result.bind(lambda _: ys)(xs)


result: ResultBuilder[Any, Any] = ResultBuilder()


__all__ = ["result"]
