from typing import Any, Callable, TypeVar

from expression.core import Builder, Nothing, Option, Some, option

_TSource = TypeVar("_TSource")
_TResult = TypeVar("_TResult")


class OptionBuilder(Builder[Option[_TSource], _TSource]):
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


option_effect: OptionBuilder[Any] = OptionBuilder()

__all__ = ["option_effect"]
