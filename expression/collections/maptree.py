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

"""The maptree module.

Contains the internal tree implementation of the `map`.

Do not use directly. Use the `map` module instead.
"""

import builtins
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

from expression.core import Nothing, Option, Some, SupportsLessThan, failwith, pipe

from . import block, seq
from .block import Block


Key = TypeVar("Key", bound=SupportsLessThan)
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


def is_empty(m: MapTree[Any, Any]):
    return m.is_none()


def size_aux(acc: int, m: MapTree[Key, Value]) -> int:
    match m:
        case Option(tag="some", some=MapTreeNode(left=left, right=right)):
            return size_aux(size_aux(acc + 1, left), right)
        case Option(tag="some", some=MapTreeLeaf()):
            return acc + 1
        case _:
            return acc


def size(x: MapTree[Any, Any]):
    return size_aux(0, x)


def height(m: MapTree[Key, Value]) -> int:
    match m:
        case Option(tag="some", some=MapTreeNode(height=height)):
            return height
        case Option(tag="some", some=MapTreeLeaf()):
            return 1
        case _:
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
            t2_ = t2.value
            # One of the nodes must have height > height t1 + 1
            if height(t2_.left) > t1h + 1:  # balance left: combination
                if isinstance(t2_.left.value, MapTreeNode):
                    t2l = t2_.left.value
                    return mk(
                        mk(t1, k, v, t2l.left),
                        t2l.key,
                        t2l.value,
                        mk(t2l.right, t2_.key, t2_.value, t2_.right),
                    )
                else:
                    failwith("internal error: Map.rebalance")
            else:  # Rotate left
                return mk(mk(t1, k, v, t2_.left), t2_.key, t2_.value, t2_.right)
        else:
            failwith("internal error: Map.rebalance")
    else:
        if t1h > t2h + TOLERANCE:  # left is heavier than right
            if isinstance(t1.value, MapTreeNode):
                t1_ = t1.value
                # One of the nodes must have height > height t2 + 1
                if height(t1_.right) > t2h + 1:  # balance right: combination
                    if isinstance(t1_.right.value, MapTreeNode):
                        t1r = t1_.right.value
                        return mk(
                            mk(t1_.left, t1_.key, t1_.value, t1r.left),
                            t1r.key,
                            t1r.value,
                            mk(t1r.right, k, v, t2),
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
    match m:
        case Option(tag="some", some=MapTreeNode(key=key, value=value, left=left, right=right, height=height)):
            if k < key:
                return rebalance(add(k, v, left), key, value, right)
            elif k == key:
                return Some(MapTreeNode(k, v, left, right, height))
            else:
                return rebalance(left, key, value, add(k, v, right))
        case Option(tag="some", some=MapTreeLeaf(key=key, value=value)):
            if k < key:
                node = MapTreeNode(k, v, empty, m, 2)
                return Some(node)
            elif k == key:
                return Some(MapTreeLeaf(k, v))
            else:
                return Some(MapTreeNode(k, v, m, empty, 2))
        case _:
            return Some(MapTreeLeaf(k, v))


def try_find(k: Key, m: MapTree[Key, Value]) -> Option[Value]:
    for m2 in m.to_list():
        if k == m2.key:
            return Some(m2.value)
        else:
            if isinstance(m2, MapTreeNode):
                mn = m2
                return try_find(k, mn.left if k < mn.key else mn.right)
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
    predicate: Callable[[Key, Value], bool],
    k: Key,
    v: Value,
    acc: tuple[MapTree[Key, Value], MapTree[Key, Value]],
) -> tuple[MapTree[Key, Value], MapTree[Key, Value]]:
    acc1, acc2 = acc
    if predicate(k, v):
        a: MapTree[Key, Value] = add(k, v, acc1)
        return a, acc2
    else:
        return acc1, add(k, v, acc2)


def partition_aux(
    predicate: Callable[[Key, Value], bool],
    m: MapTree[Key, Value],
    acc: tuple[MapTree[Key, Value], MapTree[Key, Value]],
) -> tuple[MapTree[Key, Value], MapTree[Key, Value]]:
    match m:
        case Option(tag="some", some=MapTreeNode(key=key, value=value, left=left, right=right)):
            acc = partition_aux(predicate, right, acc)
            acc = partition1(predicate, key, value, acc)
            return partition_aux(predicate, left, acc)
        case Option(tag="some", some=MapTreeLeaf(key=key, value=value)):
            return partition1(predicate, key, value, acc)
        case _:
            return acc


def partition(
    predicate: Callable[[Key, Value], bool], m: MapTree[Key, Value]
) -> tuple[MapTree[Key, Value], MapTree[Key, Value]]:
    return partition_aux(predicate, m, (empty, empty))


def filter1(predicate: Callable[[Key, Value], bool], k: Key, v: Value, acc: MapTree[Key, Value]) -> MapTree[Key, Value]:
    if predicate(k, v):
        return add(k, v, acc)
    else:
        return acc


def filter_aux(
    predicate: Callable[[Key, Value], bool],
    m: MapTree[Key, Value],
    acc: MapTree[Key, Value],
) -> MapTree[Key, Value]:
    match m:
        case Option(tag="some", some=MapTreeNode(key=key, value=value, left=left, right=right)):
            acc = filter_aux(predicate, left, acc)
            acc = filter1(predicate, key, value, acc)
            return filter_aux(predicate, right, acc)
        case Option(tag="some", some=MapTreeLeaf(key=key, value=value)):
            return filter1(predicate, key, value, acc)
        case _:
            return acc


def filter(f: Callable[[Key, Value], bool], m: MapTree[Key, Value]) -> MapTree[Key, Value]:
    return filter_aux(f, m, empty)


def splice_out_successor(m: MapTree[Key, Value]) -> tuple[Key, Value, Option[MapTreeLeaf[Key, Value]]]:
    match m:
        case Option(tag="some", some=MapTreeNode(key=key, value=value, left=left, right=right)):
            if is_empty(left):
                return key, value, right
            else:
                k3, v3, l_ = splice_out_successor(left)
                return k3, v3, mk(l_, key, value, right)
        case Option(tag="some", some=MapTreeLeaf(key=key, value=value)):
            return key, value, empty
        case _:
            failwith("internal error: Map.splice_out_successor")


def remove(k: Key, m: MapTree[Key, Value]) -> Option[MapTreeLeaf[Key, Value]]:
    match m:
        case Option(tag="some", some=MapTreeNode(key=key, value=value, left=left, right=right)):
            if k < key:
                return rebalance(remove(k, left), key, value, right)
            elif k == key:
                if is_empty(left):
                    return right
                elif is_empty(right):
                    return left
                else:
                    sk, sv, r_ = splice_out_successor(right)
                    return mk(left, sk, sv, r_)
            else:
                return rebalance(left, key, value, remove(k, right))
        case Option(tag="some", some=MapTreeLeaf(key=key, value=value)):
            if k == key:
                return empty
            else:
                return m
        case _:
            return empty


def change(k: Key, u: Callable[[Option[Value]], Option[Value]], m: MapTree[Key, Value]) -> MapTree[Key, Value]:
    match m:
        case Option(tag="some", some=MapTreeNode(key=key, value=value, left=left, right=right, height=height)):
            if k < key:
                return rebalance(change(k, u, left), key, value, right)
            elif k == key:
                for v in u(Some(value)).to_list():
                    return Some(MapTreeNode(k, v, left, right, height))
                else:
                    if is_empty(left):
                        return right
                    elif is_empty(right):
                        return left
                    else:
                        sk, sv, r_ = splice_out_successor(right)
                        return mk(left, sk, sv, r_)
            else:
                return rebalance(left, key, value, change(k, u, right))
        case Option(tag="some", some=MapTreeLeaf(key=key, value=value)):
            if k < key:
                for v in u(Nothing).to_list():
                    return Some(MapTreeNode(k, v, empty, m, 2))
                else:
                    return m
            elif k == key:
                for v in u(Some(value)).to_list():
                    return Some(MapTreeLeaf(k, v))
                else:
                    return empty
            else:
                for v in u(Nothing).to_list():
                    return Some(MapTreeNode(k, v, m, empty, 2))
                else:
                    return m

        case _:
            for v in u(Nothing):
                return Some(MapTreeLeaf(k, v))
            else:
                return m


def mem(k: Key, m: MapTree[Key, Value]) -> bool:
    match m:
        case Option(tag="some", some=MapTreeNode(key=key, left=left, right=right)):
            if k < key:
                return mem(k, left)
            else:
                return k == key or mem(k, right)
        case Option(tag="some", some=MapTreeLeaf(key=key)):
            return k == key
        case _:
            return False


def iter(fn: Callable[[Key, Value], None], m: MapTree[Key, Value]) -> None:
    """Iterate maptree."""
    match m:
        case Option(tag="some", some=MapTreeNode(left=left, right=right, key=key, value=value)):
            iter(fn, left)
            fn(key, value)
            iter(fn, right)
        case Option(tag="some", some=MapTreeLeaf(key=key, value=value)):
            fn(key, value)
        case _:
            pass


def try_pick(f: Callable[[Key, Value], Option[Result]], m: MapTree[Key, Value]) -> Option[Result]:
    match m:
        case Option(tag="some", some=MapTreeNode(left=left, right=right, key=key, value=value)):
            res = try_pick(f, left)
            if res.is_some():
                return res
            else:
                res = f(key, value)
                if res.is_some():
                    return res
                else:
                    return try_pick(f, right)
        case Option(tag="some", some=MapTreeLeaf(key=key, value=value)):
            return f(key, value)
        case _:
            return Nothing


def exists(f: Callable[[Key, Value], bool], m: MapTree[Key, Value]) -> bool:
    match m:
        case Option(tag="some", some=MapTreeNode(left=left, right=right, key=key, value=value)):
            return exists(f, left) or f(key, value) or exists(f, right)
        case Option(tag="some", some=MapTreeLeaf(key=key, value=value)):
            return f(key, value)
        case _:
            return False


def forall(f: Callable[[Key, Value], bool], m: MapTree[Key, Value]) -> bool:
    match m:
        case Option(tag="some", some=MapTreeNode(left=left, right=right, key=key, value=value)):
            return forall(f, left) and f(key, value) and forall(f, right)
        case Option(tag="some", some=MapTreeLeaf(key=key, value=value)):
            return f(key, value)
        case _:
            return True


def map(f: Callable[[Key, Value], Result], m: MapTree[Key, Value]) -> MapTree[Key, Result]:
    match m:
        case Option(tag="some", some=MapTreeNode(left=left, right=right, key=key, value=value, height=height)):
            l2 = map(f, left)
            v2 = f(key, value)
            r2 = map(f, right)
            return Some(MapTreeNode(key, v2, l2, r2, height))
        case Option(tag="some", some=MapTreeLeaf(key=key, value=value)):
            return Some(MapTreeLeaf(key, f(key, value)))
        case _:
            return empty


def fold_back(f: Callable[[tuple[Key, Value], Result], Result], m: MapTree[Key, Value], x: Result) -> Result:
    match m:
        case Option(tag="some", some=MapTreeNode(left=left, right=right, key=key, value=value)):
            x = fold_back(f, right, x)
            x = f((key, value), x)
            return fold_back(f, left, x)
        case Option(tag="some", some=MapTreeLeaf(key=key, value=value)):
            return f((key, value), x)
        case _:
            return x


def fold(f: Callable[[Result, tuple[Key, Value]], Result], x: Result, m: MapTree[Key, Value]) -> Result:
    match m:
        case Option(tag="some", some=MapTreeNode(left=left, right=right, key=key, value=value)):
            x = fold(f, x, left)
            x = f(x, (key, value))
            return fold(f, x, right)
        case Option(tag="some", some=MapTreeLeaf(key=key, value=value)):
            return f(x, (key, value))
        case _:
            return x


def to_list(m: MapTree[Key, Value]) -> Block[tuple[Key, Value]]:
    def loop(m: MapTree[Key, Value], acc: Block[tuple[Key, Value]]) -> Block[tuple[Key, Value]]:
        match m:
            case Option(tag="some", some=MapTreeNode(left=left, right=right, key=key, value=value)):
                return loop(left, loop(right, acc).cons((key, value)))
            case Option(tag="some", some=MapTreeLeaf(key=key, value=value)):
                return acc.cons((key, value))
            case _:
                return acc

    return loop(m, block.empty)


def of_list(xs: Block[tuple[Key, Value]]) -> MapTree[Key, Value]:
    def folder(acc: MapTree[Key, Value], kv: tuple[Key, Value]):
        k, v = kv
        return add(k, v, acc)

    return xs.fold(folder, empty)


def mk_from_iterator(acc: MapTree[Key, Value], e: Iterator[tuple[Key, Value]]) -> MapTree[Key, Value]:
    try:
        (x, y) = next(e)
    except StopIteration:
        return acc
    else:
        return mk_from_iterator(add(x, y, acc), e)


def of_seq(xs: Iterable[tuple[Key, Value]]) -> MapTree[Key, Value]:
    ie = builtins.iter(xs)
    return mk_from_iterator(empty, ie)


# Imperative left-to-right iterators.


# collapseLHS:
# a) Always returns either [] or a list starting with MapOne.
# b) The "fringe" of the set stack is unchanged.
def collapseLHS(stack: Block[MapTree[Key, Value]]) -> Block[MapTree[Key, Value]]:
    if stack.is_empty():
        return block.empty
    m, rest = stack.head(), stack.tail()
    match m:
        case Option(tag="some", some=MapTreeNode(left=left, right=right, key=key, value=value)):
            tree = Some(MapTreeLeaf(key, value))
            return collapseLHS(rest.cons(right).cons(tree).cons(left))
        case Option(tag="some", some=MapTreeLeaf(key=key, value=value)):
            return stack
        case _:
            return collapseLHS(rest)


class MkIterator(Iterator[tuple[Key, Value]]):
    def __init__(self, m: MapTree[Key, Value]) -> None:
        self.stack = collapseLHS(block.singleton(m))

    def __next__(self) -> tuple[Key, Value]:
        if not self.stack:
            raise StopIteration

        rest = self.stack.tail()
        match self.stack.head():
            case Option(tag="some", some=MapTreeNode()):
                failwith("Please report error: Map iterator, unexpected stack for next()")
            case Option(tag="some", some=MapTreeLeaf(key=key, value=value)):
                self.stack = collapseLHS(rest)
                return key, value
            case _:
                failwith("Please report error: Map iterator, unexpected stack for next()")


def not_started() -> None:
    failwith("enumeration not started")


def already_finished():
    failwith("enumeration already finished")


def mk_iterator(m: MapTree[Key, Value]) -> Iterator[tuple[Key, Value]]:
    return MkIterator(m)


def to_seq(s: MapTree[Key, Value]) -> Iterable[tuple[Key, Value]]:
    it = mk_iterator(s)

    def folder(it: Iterator[tuple[Key, Value]]):
        try:
            current = next(it)
        except StopIteration:
            return Nothing
        else:
            return Some((current, it))

    return pipe(it, seq.unfold(folder))
