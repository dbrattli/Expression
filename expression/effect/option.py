from typing import Any, Callable, Generator, Optional, TypeVar, Union

from typing_extensions import ParamSpec

from expression.core import Builder, Nothing, Option, Some, option

_TSource = TypeVar("_TSource")
_TResult = TypeVar("_TResult")
_P = ParamSpec("_P")


class OptionBuilder(Builder[_TSource, Option[Any]]):
    def bind(
        self, xs: Option[_TSource], fn: Callable[[_TSource], Option[_TResult]]
    ) -> Option[_TResult]:
        return option.bind(fn)(xs)

    def return_(self, x: _TSource) -> Option[_TSource]:
        return Some(x)

    def return_from(self, xs: Option[_TSource]) -> Option[_TSource]:
        return xs

    def combine(self, xs: Option[_TSource], ys: Option[_TSource]) -> Option[_TSource]:
        return xs.bind(lambda _: ys)

    def zero(self) -> Option[_TSource]:
        return Nothing

    def __call__(
        self,  # Ignored self parameter
        fn: Callable[
            _P,
            Union[
                Generator[Optional[_TSource], _TSource, Optional[_TSource]],
                Generator[Optional[_TSource], None, Optional[_TSource]],
            ],
        ],
    ) -> Callable[_P, Option[_TSource]]:
        return super().__call__(fn)


__all__ = ["OptionBuilder"]
