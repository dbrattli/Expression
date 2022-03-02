from typing import Any, Callable, Generator, Optional, TypeVar, Union

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

    def combine(
        self, xs: Result[_TSource, _TError], ys: Result[_TSource, _TError]
    ) -> Result[_TSource, _TError]:
        return xs.bind(lambda _: ys)

    def zero(self) -> Result[_TSource, _TError]:
        raise NotImplementedError

    def __call__(
        self,  # Ignored self parameter
        fn: Callable[
            _P,
            Union[
                Generator[Optional[_TSource], _TSource, Optional[_TSource]],
                Generator[Optional[_TSource], None, Optional[_TSource]],
            ],
        ],
    ) -> Callable[_P, Result[_TSource, _TError]]:
        return super().__call__(fn)


class TryBuilder(ResultBuilder[_TSource, Exception]):
    ...


__all__ = ["ResultBuilder", "TryBuilder"]
