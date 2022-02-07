from typing import Any, Callable, TypeVar

from expression.core import Builder, Nothing, Option, Some, option

TSource = TypeVar("TSource")
TResult = TypeVar("TResult")


class OptionBuilder(Builder[Option[TSource], TSource]):
    def bind(
        self, xs: Option[TSource], fn: Callable[[TSource], Option[TResult]]
    ) -> Option[TResult]:
        return option.bind(fn)(xs)

    def return_(self, x: TSource) -> Option[TSource]:
        return Some(x)

    def return_from(self, xs: Option[TSource]) -> Option[TSource]:
        return xs

    def combine(self, xs: Option[TSource], ys: Option[TSource]) -> Option[TSource]:
        return xs.bind(lambda _: ys)

    def zero(self) -> Option[TSource]:
        return Nothing


option_effect: OptionBuilder[Any] = OptionBuilder()

__all__ = ["option_effect"]
