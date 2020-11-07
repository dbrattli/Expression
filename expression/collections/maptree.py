# Attribution to original authors of this code
# --------------------------------------------
# This code has been originally been ported from the Fable project which
# was originally ported from the FSharp project.
#
# Fable:
#   https://fable.io
# - Copyright (c) Alfonso Garcia-Caro and contributors.
# - MIT License
# - https://github.com/fable-compiler/Fable/blob/nagareyama/src/fable-library/Map.fs
#
# F#
# - https://github.com/dotnet/fsharp
# - Copyright (c) Microsoft Corporation. All Rights Reserved.
# - MIT License
# - https://github.com/fsharp/fsharp/blob/master/src/fsharp/FSharp.Core/map.fs

"""
The maptree module.

Contains the internal tree implementation of the `map`.

Do not use directly. Use the `map` module instead.
"""
import builtins
from dataclasses import dataclass
from typing import Any, Callable, Generic, Iterable, Iterator, Tuple, TypeVar, cast

from expression.core import Nothing, Option, Some, failwith, pipe

from . import frozenlist, seq
from .frozenlist import FrozenList

Key = TypeVar("Key")
Value = TypeVar("Value")
Result = TypeVar("Result")


@dataclass
class MapTreeLeaf(Generic[Key, Value]):
    key: Key
    value: Value


MapTree = Option[MapTreeLeaf[Key, Value]]


@dataclass
class MapTreeNode(MapTreeLeaf[Key, Value]):
    left: MapTree[Key, Value]
    right: MapTree[Key, Value]

    height: int


empty: MapTree[Any, Any] = Nothing


def is_empty(m: MapTree[Key, Value]):
    return m.is_none()


def size_aux(acc: int, m: MapTree[Key, Value]) -> int:
    for m2 in m.to_list():
        if isinstance(m2, MapTreeNode):
            mn = cast(MapTreeNode[Key, Value], m2)
            return size_aux(size_aux(acc + 1, mn.left), mn.right)
        else:
            return acc + 1
    else:
        return acc


def size(x: MapTree[Key, Value]):
    return size_aux(0, x)


def height(m: MapTree[Key, Value]) -> int:
    for m2 in m.to_list():
        if isinstance(m2, MapTreeNode):
            mn = cast(MapTreeNode[Key, Value], m2)
            return mn.height
        else:
            return 1
    else:
        return 0


TOLERANCE = 2


def mk(left: MapTree[Key, Value], key: Key, value: Value, right: MapTree[Key, Value]) -> MapTree[Key, Value]:
    hl = height(left)
    hr = height(right)
    m = hr if hl < hr else hl
    if m == 0:  # m=0 ~ is_empty(l) and is_empty(r)
        return Some(MapTreeLeaf(key, value))
    else:
        return Some(MapTreeNode(key, value, left, right, m + 1))  # new map is higher by 1 than the highest


def rebalance(t1: MapTree[Key, Value], k: Key, v: Value, t2: MapTree[Key, Value]) -> MapTree[Key, Value]:
    t1h = height(t1)
    t2h = height(t2)
    if t2h > t1h + TOLERANCE:  # right is heavier than left
        if isinstance(t2.value, MapTreeNode):
            t2_ = cast(MapTreeNode[Key, Value], t2.value)
            # One of the nodes must have height > height t1 + 1
            if height(t2_.left) > t1h + 1:  # balance left: combination
                if isinstance(t2_.left.value, MapTreeNode):
                    t2l = cast(MapTreeNode[Key, Value], t2_.left.value)

                    return mk(mk(t1, k, v, t2l.left), t2l.key, t2l.value, mk(t2l.right, t2_.key, t2_.value, t2_.right))
                else:
                    failwith("internal error: Map.rebalance")
            else:  # Rotate left
                return mk(mk(t1, k, v, t2_.left), t2_.key, t2_.value, t2_.right)
        else:
            failwith("internal error: Map.rebalance")
    else:
        if t1h > t2h + TOLERANCE:  # left is heavier than right
            if isinstance(t1.value, MapTreeNode):
                t1_ = cast(MapTreeNode[Key, Value], t1.value)
                # One of the nodes must have height > height t2 + 1
                if height(t1_.right) > t2h + 1:  # balance right: combination
                    if isinstance(t1_.right.value, MapTreeNode):
                        t1r = cast(MapTreeNode[Key, Value], t1_.right.value)
                        return mk(
                            mk(t1_.left, t1_.key, t1_.value, t1r.left), t1r.key, t1r.value, mk(t1r.right, k, v, t2)
                        )
                    else:
                        failwith("internal error: Map.rebalance")
                else:
                    return mk(t1_.left, t1_.key, t1_.value, mk(t1_.right, k, v, t2))
            else:
                failwith("internal error: Map.rebalance")
        else:
            return mk(t1, k, v, t2)


def add(k: Key, v: Value, m: MapTree[Key, Value]) -> MapTree[Key, Value]:
    for m2 in m.to_list():
        if isinstance(m2, MapTreeNode):
            mn = cast(MapTreeNode[Key, Value], m2)
            if k < mn.key:
                return rebalance(add(k, v, mn.left), mn.key, mn.value, mn.right)
            elif k == mn.key:
                return Some(MapTreeNode(k, v, mn.left, mn.right, mn.height))
            else:
                return rebalance(mn.left, mn.key, mn.value, add(k, v, mn.right))
        else:
            if k < m2.key:
                return Some(MapTreeNode(k, v, empty, m, 2))
            elif k == m2:
                return Some(MapTreeLeaf(k, v))
            else:
                return Some(MapTreeNode(k, v, m, empty, 2))
    else:
        return Some(MapTreeLeaf(k, v))


def try_find(k: Key, m: MapTree[Key, Value]) -> Option[Value]:
    for m2 in m.to_list():
        if k == m2.key:
            return Some(m2.value)
        else:
            if isinstance(m2, MapTreeNode):
                mn = cast(MapTreeNode[Key, Value], m2)
                return try_find(k, mn.left if k < m2 else mn.right)
            else:
                return Nothing
    else:  # Nothing
        return Nothing


def find(k: Key, m: MapTree[Key, Value]) -> Value:
    for v in try_find(k, m).to_list():
        return v
    else:
        raise KeyError("Key not found")


def partition1(
    predicate: Callable[[Key, Value], bool], k: Key, v: Value, acc: Tuple[MapTree[Key, Value], MapTree[Key, Value]]
) -> Tuple[MapTree[Key, Value], MapTree[Key, Value]]:
    (acc1, acc2) = acc
    if predicate(k, v):
        return (add(k, v, acc1), acc2)
    else:
        return (acc1, add(k, v, acc2))


def partition_aux(
    predicate: Callable[[Key, Value], bool],
    m: MapTree[Key, Value],
    acc: Tuple[MapTree[Key, Value], MapTree[Key, Value]],
) -> Tuple[MapTree[Key, Value], MapTree[Key, Value]]:
    for m2 in m:
        if isinstance(m2, MapTreeNode):
            mn = cast(MapTreeNode[Key, Value], m2)
            acc = partition_aux(predicate, mn.right, acc)
            acc = partition1(predicate, mn.key, mn.value, acc)
            return partition_aux(predicate, mn.left, acc)
        else:
            return partition1(predicate, m2.key, m2.value, acc)
    else:  # Nothing
        return acc


def partition(
    predicate: Callable[[Key, Value], bool], m: MapTree[Key, Value]
) -> Tuple[MapTree[Key, Value], MapTree[Key, Value]]:
    return partition_aux(predicate, m, (empty, empty))


def filter1(predicate: Callable[[Key, Value], bool], k: Key, v: Value, acc: MapTree[Key, Value]) -> MapTree[Key, Value]:
    if predicate(k, v):
        return add(k, v, acc)
    else:
        return acc


def filter_aux(
    predicate: Callable[[Key, Value], bool], m: MapTree[Key, Value], acc: MapTree[Key, Value]
) -> MapTree[Key, Value]:
    for m2 in m.to_list():
        if isinstance(m2, MapTreeNode):
            mn = cast(MapTreeNode[Key, Value], m2)
            acc = filter_aux(predicate, mn.left, acc)
            acc = filter1(predicate, mn.key, mn.value, acc)
            return filter_aux(predicate, mn.right, acc)
        else:
            return filter1(predicate, m2.key, m2.value, acc)
    else:  # Nothing
        return acc


def filter(f: Callable[[Key, Value], bool], m: MapTree[Key, Value]) -> MapTree[Key, Value]:
    return filter_aux(f, m, empty)


def splice_out_successor(m: MapTree[Key, Value]) -> Tuple[Key, Value, Option[MapTreeLeaf[Key, Value]]]:
    for m2 in m.to_list():
        if isinstance(m2, MapTreeNode):
            mn = cast(MapTreeNode[Key, Value], m2)
            if is_empty(mn.left):
                return (mn.key, mn.value, mn.right)
            else:
                k3, v3, l_ = splice_out_successor(mn.left)
                return (k3, v3, mk(l_, mn.key, mn.value, mn.right))
        else:
            return (m2.key, m2.value, empty)
    else:  # Nothing
        failwith("internal error: Map.splice_out_successor")


def remove(k: Key, m: MapTree[Key, Value]) -> Option[MapTreeLeaf[Key, Value]]:
    for m2 in m.to_list():
        if isinstance(m2, MapTreeNode):
            mn = cast(MapTreeNode[Key, Value], m2)
            if k < mn.key:
                return rebalance(remove(k, mn.left), mn.key, mn.value, mn.right)
            elif k == mn.key:
                if is_empty(mn.left):
                    return mn.right
                elif is_empty(mn.right):
                    return mn.left
                else:
                    sk, sv, r_ = splice_out_successor(mn.right)
                    return mk(mn.left, sk, sv, r_)
            else:
                return rebalance(mn.left, mn.key, mn.value, remove(k, mn.right))
        else:
            if k == m2.key:
                return empty
            else:
                return m
    else:  # Nothing
        return empty


def change(k: Key, u: Callable[[Option[Value]], Option[Value]], m: MapTree[Key, Value]) -> MapTree[Key, Value]:
    for m2 in m.to_list():
        if isinstance(m2, MapTreeNode):
            mn = cast(MapTreeNode[Key, Value], m2)
            if k < mn.key:
                rebalance(change(k, u, mn.left), mn.key, mn.value, mn.right)
            elif k == mn.key:
                for v in u(Some(mn.value)).to_list():
                    return Some(MapTreeNode(k, v, mn.left, mn.right, mn.height))
                else:
                    if is_empty(mn.left):
                        return mn.right
                    elif is_empty(mn.right):
                        return mn.left
                    else:
                        sk, sv, r_ = splice_out_successor(mn.right)
                        return mk(mn.left, sk, sv, r_)
            else:
                rebalance(mn.left, mn.key, mn.value, change(k, u, mn.right))
        else:
            if k < m2.key:
                for v in u(Nothing).to_list():
                    return Some(MapTreeNode(k, v, empty, m, 2))
                else:
                    return m
            elif k == m2.key:
                for v in u(Some(m2.value)).to_list():
                    return Some(MapTreeLeaf(k, v))
                else:
                    return empty
            else:
                for v in u(Nothing).to_list():
                    return Some(MapTreeNode(k, v, m, empty, 2))
                else:
                    return m

    else:
        for v in u(Nothing):
            return Some(MapTreeLeaf(k, v))
        else:
            return m


def mem(k: Key, m: MapTree[Key, Value]) -> bool:
    for m2 in m.to_list():
        if isinstance(m2, MapTreeNode):
            mn = cast(MapTreeNode[Key, Value], m2)
            if k < mn.key:
                return mem(k, mn.left)
            else:
                return k == mn.key or mem(k, mn.right)
        else:
            return k == m2.key
    else:
        return False


def iter(fn: Callable[[Key, Value], None], m: MapTree[Key, Value]) -> None:
    """Iterate maptree."""
    for m2 in m.to_list():
        if isinstance(m2, MapTreeNode):
            mn = cast(MapTreeNode[Key, Value], m2)
            iter(fn, mn.left)
            fn(mn.key, mn.value)
            iter(fn, mn.right)
        else:
            fn(m2.key, m2.value)


def try_pick(f: Callable[[Key, Value], Option[Result]], m: MapTree[Key, Value]) -> Option[Result]:
    for m2 in m.to_list():
        if isinstance(m2, MapTreeNode):
            mn = cast(MapTreeNode[Key, Value], m2)
            for res in try_pick(f, mn.left).to_list():
                return res
            else:
                for res in f(mn.key, mn.value):
                    return res
                else:
                    return try_pick(f, mn.right)
        else:
            return f(m2.key, m2.value)
    else:
        return Nothing


def exists(f: Callable[[Key, Value], bool], m: MapTree[Key, Value]) -> bool:
    for m2 in m.to_list():
        if isinstance(m2, MapTreeNode):
            mn = cast(MapTreeNode[Key, Value], m2)
            return exists(f, mn.left) or f(mn.key, mn.value) or exists(f, mn.right)
        else:
            return f(m2.key, m2.value)
    else:
        return False


def forall(f: Callable[[Key, Value], bool], m: MapTree[Key, Value]) -> bool:
    for m2 in m.to_list():
        if isinstance(m2, MapTreeNode):
            mn = cast(MapTreeNode[Key, Value], m2)
            return forall(f, mn.left) and f(mn.key, mn.value) and forall(f, mn.right)
        else:
            return f(m2.key, m2.value)
    else:
        return True


def map(f: Callable[[Value], Result], m: MapTree[Key, Value]) -> MapTree[Key, Result]:
    for m2 in m.to_list():
        if isinstance(m2, MapTreeNode):
            mn = cast(MapTreeNode[Key, Value], m2)
            l2 = map(f, mn.left)
            v2 = f(mn.value)
            r2 = map(f, mn.right)
            return Some(MapTreeNode(mn.key, v2, l2, r2, mn.height))
        else:
            return Some(MapTreeLeaf(m2.key, f(m2.value)))
    else:
        return empty


def mapi(f: Callable[[Tuple[Key, Value]], Result], m: MapTree[Key, Value]) -> MapTree[Key, Value]:
    for m2 in m.to_list():
        if isinstance(m2, MapTreeNode):
            mn = cast(MapTreeNode[Key, Value], m2)
            l2 = mapi(f, mn.left)
            v2 = f((mn.key, mn.value))
            r2 = mapi(f, mn.right)
            return Some(MapTreeNode(mn.key, v2, l2, r2, mn.height))
        else:
            return Some(MapTreeLeaf(m2.key, f((m2.key, m2.value))))
    else:
        return empty


def fold_back(f: Callable[[Tuple[Key, Value], Result], Result], m: MapTree[Key, Value], x: Result) -> Result:
    for m2 in m.to_list():
        if isinstance(m2, MapTreeNode):
            mn = cast(MapTreeNode[Key, Value], m2)
            x = fold_back(f, mn.right, x)
            x = f((mn.key, mn.value), x)
            return fold_back(f, mn.left, x)
        else:
            return f((m2.key, m2.value), x)
    else:
        return x


def fold(f: Callable[[Result, Tuple[Key, Value]], Result], x: Result, m: MapTree[Key, Value]) -> Result:
    for m2 in m.to_list():
        if isinstance(m2, MapTreeNode):
            mn = cast(MapTreeNode[Key, Value], m2)
            x = fold(f, x, mn.left)
            x = f(x, (mn.key, mn.value))
            return fold(f, x, mn.right)
        else:
            return f(x, (m2.key, m2.value))
    else:
        return x


def to_list(m: MapTree[Key, Value]) -> FrozenList[Tuple[Key, Value]]:
    def loop(m: MapTree[Key, Value], acc: FrozenList[Tuple[Key, Value]]) -> FrozenList[Tuple[Key, Value]]:
        for m2 in m.to_list():
            if isinstance(m2, MapTreeNode):
                mn = cast(MapTreeNode[Key, Value], m2)
                return loop(mn.left, loop(mn.right, acc).cons((mn.key, mn.value)))
            else:
                return acc.cons((m2.key, m2.value))
        else:
            return acc

    return loop(m, frozenlist.empty)


def of_list(xs: FrozenList[Tuple[Key, Value]]) -> MapTree[Key, Value]:
    def folder(acc: MapTree[Key, Value], kv: Tuple[Key, Value]):
        k, v = kv
        return add(k, v, acc)

    return xs.fold(folder, empty)


def mk_from_iterator(acc: MapTree[Key, Value], e: Iterator[Tuple[Key, Value]]) -> MapTree[Key, Value]:
    try:
        (x, y) = next(e)
    except StopIteration:
        return acc
    else:
        return mk_from_iterator(add(x, y, acc), e)


def of_seq(xs: Iterable[Tuple[Key, Value]]) -> MapTree[Key, Value]:
    if isinstance(xs, FrozenList):
        xs = cast(FrozenList[Tuple[Key, Value]], xs)
        return of_list(xs)
    else:
        ie = builtins.iter(xs)
        return mk_from_iterator(empty, ie)


# Imperative left-to-right iterators.

# collapseLHS:
# a) Always returns either [] or a list starting with MapOne.
# b) The "fringe" of the set stack is unchanged.
def collapseLHS(stack: FrozenList[MapTree[Key, Value]]) -> FrozenList[MapTree[Key, Value]]:
    if stack.is_empty():
        return frozenlist.empty
    m, rest = stack.head(), stack.tail()
    for m2 in m.to_list():
        if isinstance(m2, MapTreeNode):
            mn = cast(MapTreeNode[Key, Value], m2)
            tree = Some(MapTreeLeaf(mn.key, mn.value))
            return collapseLHS(rest.cons(mn.right).cons(tree).cons(mn.left))
        else:
            return stack
    else:
        return collapseLHS(rest)


class MkIterator(Iterator[Tuple[Key, Value]]):
    def __init__(self, m: MapTree[Key, Value]) -> None:
        self.stack = collapseLHS(frozenlist.singleton(m))

    def __next__(self) -> Tuple[Key, Value]:
        if not self.stack:
            raise StopIteration

        rest = self.stack.tail()
        for m in self.stack.head():
            if isinstance(m, MapTreeNode):
                failwith("Please report error: Map iterator, unexpected stack for next()")
            else:
                self.stack = collapseLHS(rest)
                return m.key, m.value
        else:
            failwith("Please report error: Map iterator, unexpected stack for next()")


def not_started() -> None:
    failwith("enumeration not started")


def already_finished():
    failwith("enumeration already finished")


def mk_iterator(m: MapTree[Key, Value]) -> Iterator[Tuple[Key, Value]]:
    return MkIterator(m)


def to_seq(s: MapTree[Key, Value]) -> Iterable[Tuple[Key, Value]]:
    it = mk_iterator(s)

    def folder(it: Iterator[Tuple[Key, Value]]):
        try:
            current = next(it)
        except StopIteration:
            return Nothing
        else:
            return Some((current, it))

    return pipe(it, seq.unfold(folder))
