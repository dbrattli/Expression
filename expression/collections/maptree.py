# Copyright (c) Microsoft Corporation.  All Rights Reserved.
# See License.txt in the project root for license information.

from dataclasses import dataclass
from typing import Any, Callable, Generic, Tuple, TypeVar, cast

from expression.core import Nothing, Option, Some, failwith

Value = TypeVar("Value")
Key = TypeVar("Key")


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


tolerance = 2


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
    if t2h > t1h + tolerance:  # right is heavier than left
        if isinstance(t2.value, MapTreeNode):
            t2_ = cast(MapTreeNode[Key, Value], t2.value)
            # one of the nodes must have height > height t1 + 1
            if height(t2_.left) > t1h + 1:  # balance left: combination
                if isinstance(t2_.left.value, MapTreeNode):
                    t2l = cast(MapTreeNode[Key, Value], t2_.left.value)

                    return mk(mk(t1, k, v, t2l.left), t2l.key, t2l.value, mk(t2l.right, t2_.key, t2_.value, t2_.right))
                else:
                    failwith("internal error: Map.rebalance")
            else:  # rotate left
                return mk(mk(t1, k, v, t2_.left), t2_.key, t2_.value, t2_.right)
        else:
            failwith("internal error: Map.rebalance")
    else:
        if t1h > t2h + tolerance:  # left is heavier than right
            if isinstance(t1.value, MapTreeNode):
                t1_ = cast(MapTreeNode[Key, Value], t1.value)
                # one of the nodes must have height > height t2 + 1
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
                rebalance(mn.left, mn.key, mn.value, add(k, v, mn.right))
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
    f: Callable[[Key, Value], bool], k: Key, v: Value, acc: Tuple[MapTree[Key, Value], MapTree[Key, Value]]
) -> Tuple[MapTree[Key, Value], MapTree[Key, Value]]:
    (acc1, acc2) = acc
    if f(k, v):
        return (add(k, v, acc1), acc2)
    else:
        return (acc1, add(k, v, acc2))


def partition_aux(
    f: Callable[[Key, Value], bool], m: MapTree[Key, Value], acc: Tuple[MapTree[Key, Value], MapTree[Key, Value]]
) -> Tuple[MapTree[Key, Value], MapTree[Key, Value]]:
    for m2 in m:
        if isinstance(m2, MapTreeNode):
            mn = cast(MapTreeNode[Key, Value], m2)
            acc = partition_aux(f, mn.right, acc)
            acc = partition1(f, mn.key, mn.value, acc)
            return partition_aux(f, mn.left, acc)
        else:
            return partition1(f, m2.key, m2.value, acc)
    else:  # Nothing
        return acc


def partition(
    f: Callable[[Key, Value], bool], m: MapTree[Key, Value]
) -> Tuple[MapTree[Key, Value], MapTree[Key, Value]]:
    return partition_aux(f, m, (empty, empty))


def filter1(f: Callable[[Key, Value], bool], k: Key, v: Value, acc: MapTree[Key, Value]) -> MapTree[Key, Value]:
    if f(k, v):
        return add(k, v, acc)
    else:
        return acc


def filter_aux(
    f: Callable[[Key, Value], bool], m: MapTree[Key, Value], acc: MapTree[Key, Value]
) -> MapTree[Key, Value]:
    for m2 in m.to_list():
        if isinstance(m2, MapTreeNode):
            mn = cast(MapTreeNode[Key, Value], m2)
            acc = filter_aux(f, mn.left, acc)
            acc = filter1(f, mn.key, mn.value, acc)
            return filter_aux(f, mn.right, acc)
        else:
            return filter1(f, m2.key, m2.value, acc)
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
    else:
        failwith("internal error: Map.splice_out_successor")


def remove(k: Key, m: MapTree[Key, Value]) -> Option[MapTreeLeaf[Key, Value]]:
    for m2 in m.to_list():
        # let c = comparer.Compare(k, m2.key)
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


# let rec change (comparer: IComparer<Key>) k (u: Value option -> Value option) (m: MapTree[Key, Value]) : MapTree<Key,Value> =
#     match m with
#     | None ->
#         match u None with
#         | None -> m
#         | Some v -> MapTreeLeaf (k, v) |> Some
#     | Some m2 ->
#         match m2 with
#         | :? MapTreeNode[Key, Value] as mn ->
#             let c = comparer.Compare(k, mn.key)
#             if c < 0 then
#                 rebalance (change comparer k u mn.left) mn.key mn.value mn.right
#             elif c = 0 then
#                 match u (Some mn.value) with
#                 | None ->
#                     if is_empty mn.left then mn.right
#                     elif is_empty mn.right then mn.left
#                     else
#                         let sk, sv, r' = splice_out_successor mn.right
#                         mk mn.left sk sv r'
#                 | Some v -> MapTreeNode (k, v, mn.left, mn.right, mn.Height) :> MapTreeLeaf<Key,Value> |> Some
#             else
#                 rebalance mn.left mn.key mn.value (change comparer k u mn.right)
#         | _ ->
#             let c = comparer.Compare(k, m2.key)
#             if c < 0 then
#                 match u None with
#                 | None -> m
#                 | Some v -> MapTreeNode (k, v, empty, m, 2) :> MapTreeLeaf<Key,Value> |> Some
#             elif c = 0 then
#                 match u (Some m2.value) with
#                 | None -> empty
#                 | Some v -> MapTreeLeaf (k, v) |> Some
#             else
#                 match u None with
#                 | None -> m
#                 | Some v -> MapTreeNode (k, v, m, empty, 2) :> MapTreeLeaf<Key,Value> |> Some

# let rec mem (comparer: IComparer<Key>) k (m: MapTree[Key, Value]) =
#     match m with
#     | None -> false
#     | Some m2 ->
#         let c = comparer.Compare(k, m2.key)
#         match m2 with
#         | :? MapTreeNode[Key, Value] as mn ->
#             if c < 0 then mem comparer k mn.left
#             else (c = 0 || mem comparer k mn.right)
#         | _ -> c = 0

# let rec iterOpt (f: OptimizedClosures.FSharpFunc<_, _, _>) (m: MapTree[Key, Value]) =
#     match m with
#     | None -> ()
#     | Some m2 ->
#         match m2 with
#         | :? MapTreeNode[Key, Value] as mn -> iterOpt f mn.left; f.Invoke (mn.key, mn.value); iterOpt f mn.right
#         | _ -> f.Invoke (m2.key, m2.value)

# let iter f m =
#     iterOpt (OptimizedClosures.FSharpFunc<_, _, _>.Adapt f) m

# let rec tryPickOpt (f: OptimizedClosures.FSharpFunc<_, _, _>) (m: MapTree[Key, Value]) =
#     match m with
#     | None -> None
#     | Some m2 ->
#         match m2 with
#         | :? MapTreeNode[Key, Value] as mn ->
#             match tryPickOpt f mn.left with
#             | Some _ as res -> res
#             | None ->
#             match f.Invoke (mn.key, mn.value) with
#             | Some _ as res -> res
#             | None ->
#             tryPickOpt f mn.right
#         | _ -> f.Invoke (m2.key, m2.value)

# let tryPick f m =
#     tryPickOpt (OptimizedClosures.FSharpFunc<_, _, _>.Adapt f) m

# let rec existsOpt (f: OptimizedClosures.FSharpFunc<_, _, _>) (m: MapTree[Key, Value]) =
#     match m with
#     | None -> false
#     | Some m2 ->
#         match m2 with
#         | :? MapTreeNode[Key, Value] as mn -> existsOpt f mn.left || f.Invoke (mn.key, mn.value) || existsOpt f mn.right
#         | _ -> f.Invoke (m2.key, m2.value)

# let exists f m =
#     existsOpt (OptimizedClosures.FSharpFunc<_, _, _>.Adapt f) m

# let rec forallOpt (f: OptimizedClosures.FSharpFunc<_, _, _>) (m: MapTree[Key, Value]) =
#     match m with
#     | None -> true
#     | Some m2 ->
#         match m2 with
#         | :? MapTreeNode[Key, Value] as mn -> forallOpt f mn.left && f.Invoke (mn.key, mn.value) && forallOpt f mn.right
#         | _ -> f.Invoke (m2.key, m2.value)

# let forall f m =
#     forallOpt (OptimizedClosures.FSharpFunc<_, _, _>.Adapt f) m

# let rec map (f:Value -> 'Result) (m: MapTree[Key, Value]) : MapTree<Key, 'Result> =
#     match m with
#     | None -> empty
#     | Some m2 ->
#         match m2 with
#         | :? MapTreeNode[Key, Value] as mn ->
#             let l2 = map f mn.left
#             let v2 = f mn.value
#             let r2 = map f mn.right
#             MapTreeNode (mn.key, v2, l2, r2, mn.Height) :> MapTreeLeaf<Key, 'Result> |> Some
#         | _ -> MapTreeLeaf (m2.key, f m2.value) |> Some

# let rec mapiOpt (f: OptimizedClosures.FSharpFunc<Key, Value, 'Result>) (m: MapTree[Key, Value]) =
#     match m with
#     | None -> empty
#     | Some m2 ->
#         match m2 with
#         | :? MapTreeNode[Key, Value] as mn ->
#             let l2 = mapiOpt f mn.left
#             let v2 = f.Invoke (mn.key, mn.value)
#             let r2 = mapiOpt f mn.right
#             MapTreeNode (mn.key, v2, l2, r2, mn.Height) :> MapTreeLeaf<Key, 'Result> |> Some
#         | _ -> MapTreeLeaf (m2.key, f.Invoke (m2.key, m2.value)) |> Some

# let mapi f m =
#     mapiOpt (OptimizedClosures.FSharpFunc<_, _, _>.Adapt f) m

# let rec foldBackOpt (f: OptimizedClosures.FSharpFunc<_, _, _, _>) (m: MapTree[Key, Value]) x =
#     match m with
#     | None -> x
#     | Some m2 ->
#         match m2 with
#         | :? MapTreeNode[Key, Value] as mn ->
#             let x = foldBackOpt f mn.right x
#             let x = f.Invoke (mn.key, mn.value, x)
#             foldBackOpt f mn.left x
#         | _ -> f.Invoke (m2.key, m2.value, x)

# let foldBack f m x =
#     foldBackOpt (OptimizedClosures.FSharpFunc<_, _, _, _>.Adapt f) m x

# let rec foldOpt (f: OptimizedClosures.FSharpFunc<_, _, _, _>) x (m: MapTree[Key, Value]) =
#     match m with
#     | None -> x
#     | Some m2 ->
#         match m2 with
#         | :? MapTreeNode[Key, Value] as mn ->
#             let x = foldOpt f x mn.left
#             let x = f.Invoke (x, mn.key, mn.value)
#             foldOpt f x mn.right
#         | _ -> f.Invoke (x, m2.key, m2.value)

# let fold f x m =
#     foldOpt (OptimizedClosures.FSharpFunc<_, _, _, _>.Adapt f) x m

# let foldSectionOpt (comparer: IComparer<Key>) lo hi (f: OptimizedClosures.FSharpFunc<_, _, _, _>) (m: MapTree[Key, Value]) x =
#     let rec foldFromTo (f: OptimizedClosures.FSharpFunc<_, _, _, _>) (m: MapTree[Key, Value]) x =
#         match m with
#         | None -> x
#         | Some m2 ->
#             match m2 with
#             | :? MapTreeNode[Key, Value] as mn ->
#                 let cLoKey = comparer.Compare(lo, mn.key)
#                 let cKeyHi = comparer.Compare(mn.key, hi)
#                 let x = if cLoKey < 0 then foldFromTo f mn.left x else x
#                 let x = if cLoKey <= 0 && cKeyHi <= 0 then f.Invoke (mn.key, mn.value, x) else x
#                 let x = if cKeyHi < 0 then foldFromTo f mn.right x else x
#                 x
#             | _ ->
#                 let cLoKey = comparer.Compare(lo, m2.key)
#                 let cKeyHi = comparer.Compare(m2.key, hi)
#                 let x = if cLoKey <= 0 && cKeyHi <= 0 then f.Invoke (m2.key, m2.value, x) else x
#                 x

#     if comparer.Compare(lo, hi) = 1 then x else foldFromTo f m x

# let foldSection (comparer: IComparer<Key>) lo hi f m x =
#     foldSectionOpt comparer lo hi (OptimizedClosures.FSharpFunc<_, _, _, _>.Adapt f) m x

# let toList (m: MapTree[Key, Value]) =
#     let rec loop (m: MapTree[Key, Value]) acc =
#         match m with
#         | None -> acc
#         | Some m2 ->
#             match m2 with
#             | :? MapTreeNode[Key, Value] as mn -> loop mn.left ((mn.key, mn.value) :: loop mn.right acc)
#             | _ -> (m2.key, m2.value) :: acc
#     loop m []

# let toArray (m: MapTree[Key, Value]): (Key * Value)[] =
#     m |> toList |> Array.ofList

# let ofList comparer l =
#     List.fold (fun acc (k, v) -> add comparer k v acc) empty l

# let rec mkFromEnumerator comparer acc (e : IEnumerator<_>) =
#     if e.MoveNext() then
#         let (x, y) = e.Current
#         mkFromEnumerator comparer (add comparer x y acc) e
#     else acc

# let ofArray comparer (arr: array<Key * Value>) =
#     let mutable res = empty
#     for (x, y) in arr do
#         res <- add comparer x y res
#     res

# let ofSeq comparer (c: seq<Key * 'T>) =
#     match c with
#     | :? array<Key * 'T> as xs -> ofArray comparer xs
#     | :? list<Key * 'T> as xs -> ofList comparer xs
#     | _ ->
#         use ie = c.GetEnumerator()
#         mkFromEnumerator comparer empty ie

# let copyToArray m (arr: _[]) i =
#     let mutable j = i
#     m |> iter (fun x y -> arr.[j] <- KeyValuePair(x, y); j <- j + 1)

# /// Imperative left-to-right iterators.
# [<NoEquality; NoComparison>]
# type MapIterator<Key, Value when Key : comparison > =
#         { /// invariant: always collapseLHS result
#         mutable stack: MapTree[Key, Value] list

#         /// true when MoveNext has been called
#         mutable started : bool }

# // collapseLHS:
# // a) Always returns either [] or a list starting with MapOne.
# // b) The "fringe" of the set stack is unchanged.
# let rec collapseLHS (stack: MapTree[Key, Value] list) =
#     match stack with
#     | [] -> []
#     | m :: rest ->
#         match m with
#         | None -> collapseLHS rest
#         | Some m2 ->
#             match m2 with
#             | :? MapTreeNode[Key, Value] as mn ->
#                 collapseLHS (mn.left :: (MapTreeLeaf (mn.key, mn.value) |> Some) :: mn.right :: rest)
#             | _ -> stack

# let mkIterator m =
#     { stack = collapseLHS [m]; started = false }

# let notStarted() = failwith "enumeration not started"

# let alreadyFinished() = failwith "enumeration already finished"

# let current i =
#     if i.started then
#         match i.stack with
#         | []     -> alreadyFinished()
#         | None :: _ ->
#             failwith "Please report error: Map iterator, unexpected stack for current"
#         | Some m :: _ ->
#             match m with
#             | :? MapTreeNode[Key, Value] ->
#                 failwith "Please report error: Map iterator, unexpected stack for current"
#             | _ -> new KeyValuePair<_, _>(m.key, m.value)
#     else
#         notStarted()

# let rec moveNext i =
#     if i.started then
#         match i.stack with
#         | [] -> false
#         | None :: rest ->
#             failwith "Please report error: Map iterator, unexpected stack for moveNext"
#         | Some m :: rest ->
#             match m with
#             | :? MapTreeNode[Key, Value] ->
#                 failwith "Please report error: Map iterator, unexpected stack for moveNext"
#             | _ ->
#                 i.stack <- collapseLHS rest
#                 not i.stack.Is_empty
#     else
#         i.started <- true  // The first call to MoveNext "starts" the enumeration.
#         not i.stack.Is_empty

# let mkIEnumerator m =
#     let mutable i = mkIterator m
#     { new IEnumerator<_> with
#             member __.Current = current i
#         interface System.Collections.IEnumerator with
#             member __.Current = box (current i)
#             member __.MoveNext() = moveNext i
#             member __.Reset() = i <- mkIterator m
#         interface System.IDisposable with
#             member __.Dispose() = ()}

# let toSeq s =
#     let en = mkIEnumerator s
#     en |> Seq.unfold (fun en ->
#         if en.MoveNext()
#         then Some(en.Current, en)
#         else None)
