from typing import Any, Callable, Iterable, TypeVar

from expression.collections import seq
from expression.core import Builder, identity

TSource = TypeVar("TSource")
TResult = TypeVar("TResult")
TState = TypeVar("TState")


class SeqBuilder(Builder[Iterable[TSource], TSource]):
    def bind(self, xs: Iterable[TSource], fn: Callable[[TSource], Iterable[TResult]]) -> Iterable[TResult]:
        return list(seq.collect(fn)(xs))

    def return_(self, x: TSource) -> Iterable[TSource]:
        return seq.singleton(x)

    def return_from(self, xs: Iterable[TSource]) -> Iterable[TSource]:
        return xs

    def combine(self, xs: Iterable[TSource], ys: Iterable[TSource]) -> Iterable[TSource]:
        return list(seq.concat(xs, ys))

    def zero(self) -> Iterable[TSource]:
        return seq.empty


# seq_builder: SeqBuilder[Any] = SeqBuilder()
seq_effect = identity  # For now


__all__ = ["seq"]
