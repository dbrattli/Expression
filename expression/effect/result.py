from typing import Any, Callable, TypeVar

from expression.core import Builder, Ok, Result, pipe, result

_TSource = TypeVar("_TSource")
_TResult = TypeVar("_TResult")
_TError = TypeVar("_TError")


class ResultBuilder(Builder[Result[_TSource, _TError], _TSource]):
    def bind(
        self,
        xs: Result[_TSource, _TError],
        fn: Callable[[_TSource], Result[_TResult, _TError]],
    ) -> Result[_TResult, _TError]:
        return pipe(xs, result.bind(fn))

    def return_(self, x: _TSource) -> Result[_TSource, _TError]:
        return Ok(x)

    def return_from(self, xs: Result[_TSource, _TError]) -> Result[_TSource, _TError]:
        return xs

    def combine(
        self, xs: Result[_TSource, _TError], ys: Result[_TSource, _TError]
    ) -> Result[_TSource, _TError]:
        return xs.bind(lambda _: ys)

    def zero(self) -> Result[_TSource, _TError]:
        raise NotImplementedError


result_effect: ResultBuilder[Any, Any] = ResultBuilder()


__all__ = ["result_effect"]
