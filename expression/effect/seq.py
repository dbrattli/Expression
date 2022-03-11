from typing import Any, Callable, Iterable, TypeVar

from expression.collections import seq
from expression.core import Builder

_TSource = TypeVar("_TSource")
_TResult = TypeVar("_TResult")


class SeqBuilder(Builder[_TSource, Iterable[Any]]):
    def bind(
        self, xs: Iterable[_TSource], fn: Callable[[_TSource], Iterable[_TResult]]
    ) -> Iterable[_TResult]:
        for x in xs:
            return fn(x)
        return []

    def return_(self, x: _TSource) -> Iterable[_TSource]:
        return seq.singleton(x)

    def return_from(self, xs: Iterable[_TSource]) -> Iterable[_TSource]:
        return xs

    def combine(
        self, xs: Iterable[_TSource], ys: Iterable[_TSource]
    ) -> Iterable[_TSource]:
        ret = seq.concat(xs, ys)
        return ret

    def zero(self) -> Iterable[_TSource]:
        return seq.empty


__all__ = ["SeqBuilder"]
