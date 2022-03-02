from typing import Any, Callable, Iterable, TypeVar

from expression.collections import seq
from expression.core import Builder, identity

_TSource = TypeVar("_TSource")
_TResult = TypeVar("_TResult")


class SeqBuilder(Builder[_TSource, Iterable[Any]]):
    def bind(
        self, xs: Iterable[_TSource], fn: Callable[[_TSource], Iterable[_TResult]]
    ) -> Iterable[_TResult]:
        return list(seq.collect(fn)(xs))

    def return_(self, x: _TSource) -> Iterable[_TSource]:
        return seq.singleton(x)

    def return_from(self, xs: Iterable[_TSource]) -> Iterable[_TSource]:
        return xs

    def combine(
        self, xs: Iterable[_TSource], ys: Iterable[_TSource]
    ) -> Iterable[_TSource]:
        return list(seq.concat(xs, ys))

    def zero(self) -> Iterable[_TSource]:
        return seq.empty


# seq_builder: SeqBuilder[Any] = SeqBuilder()
seq_effect = identity  # For now


__all__ = ["seq"]
