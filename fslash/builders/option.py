from typing import Any, Callable, TypeVar

from fslash.core import Builder, Nothing, Option, Option_, Some

TSource = TypeVar("TSource")
TResult = TypeVar("TResult")


class OptionBuilder(Builder[Option_[TSource], TSource]):
    def bind(self, xs: Option_[TSource], fn: Callable[[TSource], Option_[TResult]]):
        return Option.bind(fn)(xs)

    def return_(self, x: TSource) -> Option_[TSource]:
        return Some(x)

    def return_from(self, xs: Option_[TSource]) -> Option_[TSource]:
        return xs

    def combine(self, xs: Option_[TSource], ys: Option_[TSource]) -> Option_[TSource]:
        binder: Callable[[Any], Option_[TSource]] = lambda _: ys
        return Option.bind(binder)(xs)

    def zero(self):
        return Nothing


option: OptionBuilder[Any] = OptionBuilder()

__all__ = ["option"]
