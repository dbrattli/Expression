from typing import TypeVar, Any
from fslash.core import Option, Nothing, Some, Option_
from .builder import Builder

TSource = TypeVar("TSource")


class OptionBuilder(Builder[Option_[TSource], TSource]):
    def bind(self, xs, fn):
        return Option.bind(fn)(xs)

    def return_(self, x):
        return Some(x)

    def return_from(self, xs):
        return xs

    def combine(self, xs, ys):
        return Option.bind(lambda _: ys)(xs)

    def zero(self):
        return Nothing


option: OptionBuilder[Any] = OptionBuilder()

__all__ = ["option"]
