from typing import TypeVar, Iterable, Callable
from fslash.core import Builder, identity

from fslash.collections import Seq

TSource = TypeVar("TSource")
TResult = TypeVar("TResult")
TState = TypeVar("TState")


class SeqBuilder(Builder[Iterable[TSource], TSource]):
    def bind(self, xs: Iterable[TSource], fn: Callable[[TSource], Iterable[TResult]]) -> Iterable[TResult]:
        return list(Seq.collect(fn)(xs))

    def return_(self, x: TSource) -> Iterable[TSource]:
        return Seq.singleton(x)

    def return_from(self, xs: Iterable[TSource]) -> Iterable[TSource]:
        return xs

    def combine(self, xs: Iterable[TSource], ys: Iterable[TSource]) -> Iterable[TSource]:
        return list(Seq.concat(xs, ys))

    def zero(self) -> Iterable[TSource]:
        return Seq.empty


# seq: SeqBuilder[Any] = SeqBuilder()
seq = identity


__all__ = ["seq"]
