from typing import Any, Callable, TypeVar

from expression.core import Builder, Nothing, Option, Some, option

TSource = TypeVar("TSource")
TResult = TypeVar("TResult")


class OptionBuilder(Builder[Option[TSource], TSource]):
    def bind(self, xs: Option[TSource], fn: Callable[[TSource], Option[TResult]]):
        return option.bind(fn)(xs)

    def return_(self, x: TSource) -> Option[TSource]:
        return Some(x)

    def return_from(self, xs: Option[TSource]) -> Option[TSource]:
        return xs

    def combine(self, xs: Option[TSource], ys: Option[TSource]) -> Option[TSource]:
        binder: Callable[[Any], Option[TSource]] = lambda _: ys
        return option.bind(binder)(xs)

    def zero(self):
        return Nothing


option_effect: OptionBuilder[Any] = OptionBuilder()

__all__ = ["option_effect"]
