from collections.abc import Callable, Generator
from typing import Any, TypeVar

from typing_extensions import ParamSpec

from expression.core import Builder, Ok, Result, pipe, result


_TSource = TypeVar("_TSource")
_TResult = TypeVar("_TResult")
_TError = TypeVar("_TError")
_P = ParamSpec("_P")


class ResultBuilder(Builder[_TSource, Result[Any, _TError]]):
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

    def combine(self, xs: Result[_TSource, _TError], ys: Result[_TSource, _TError]) -> Result[_TSource, _TError]:
        return xs.bind(lambda _: ys)

    def zero(self) -> Result[_TSource, _TError]:
        raise NotImplementedError

    def __call__(
        self,  # Ignored self parameter
        fn: Callable[
            _P,
            Generator[_TSource | None, _TSource, _TSource | None] | Generator[_TSource | None, None, _TSource | None],
        ],
    ) -> Callable[_P, Result[_TSource, _TError]]:
        return super().__call__(fn)


class TryBuilder(ResultBuilder[_TSource, Exception]): ...


__all__ = ["ResultBuilder", "TryBuilder"]
