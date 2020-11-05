# Attribution to original authors of this code
# --------------------------------------------
# This code has been originally been ported from the Fable project which
# was originally ported from the FSharp project.
#
# Fable (https://fable.io)
# - Copyright (c) Alfonso Garcia-Caro and contributors.
# - MIT License
# - https://github.com/fable-compiler/Fable/blob/nagareyama/src/fable-library/Map.fs
#
# F# (https://github.com/dotnet/fsharp)
# - Copyright (c) Microsoft Corporation. All Rights Reserved.
# - MIT License
# - https://github.com/fsharp/fsharp/blob/master/src/fsharp/FSharp.Core/map.fs

from typing import Callable, Generic, Iterable, List, Tuple, TypeVar, Union, overload

from expression.core import Option, pipe

from . import frozenlist, maptree, seq
from .frozenlist import FrozenList
from .maptree import MapTree

Value = TypeVar("Value")
Key = TypeVar("Key")
Result = TypeVar("Result")


class Map(Generic[Key, Value]):
    def __init__(self, tree: MapTree[Key, Value]) -> None:
        self._tree = tree

    @staticmethod
    def empty() -> "Map[Key, Value]":
        return Map(maptree.empty)

    @staticmethod
    def create(ie: Iterable[Tuple[Key, Value]]) -> "Map[Key, Value]":
        return Map(maptree.of_seq(ie))

    def add(self, key: Key, value: Value) -> "Map[Key, Value]":
        return Map(maptree.add(key, value, self._tree))

    def change(self, key: Key, f: Callable[[Option[Value]], Option[Value]]) -> "Map[Key, Value]":
        return Map(maptree.change(key, f, self._tree))

    def is_empty(self) -> bool:
        return maptree.is_empty(self._tree)

    #     def Item
    #      with get(key : 'Key) =
    #         maptree.find comparer key tree

    #     def TryPick f =
    #         maptree.tryPick f tree

    def exists(self, predicate: Callable[[Key, Value], bool]) -> bool:
        return maptree.exists(predicate, self._tree)

    def filter(self, predicate: Callable[[Key, Value], bool]) -> "Map[Key, Value]":
        return Map(maptree.filter(predicate, self._tree))

    #     def ForAll predicate =
    #         maptree.forall predicate tree

    #     def Fold f acc =
    #         maptree.foldBack f tree acc

    #     def FoldSection (lo:'Key) (hi:'Key) f (acc:'z) =
    #         maptree.foldSection comparer lo hi f tree acc

    #     def Iterate f =
    #         maptree.iter f tree

    #     def MapRange (f:'Value->'Result) =
    #         return Map<'Key, 'Result>(comparer, maptree.map f tree)

    def map(self, f: Callable[[Value], Result]) -> "Map[Key, Result]":
        return Map(maptree.map(f, self._tree))

    def partition(self, predicate: Callable[[Key, Value], bool]) -> "Tuple[Map[Key, Value], Map[Key, Value]]":
        r1, r2 = maptree.partition(predicate, self._tree)
        return Map(r1), Map(r2)

    def count(self):
        return maptree.size(self._tree)

    def contains_key(self, key: Key) -> bool:
        return maptree.mem(key, self._tree)

    def remove(self, key: Key) -> "Map[Key, Value]":
        return Map(maptree.remove(key, self._tree))

    def try_get_value(self, key: Key, value: List[Value]):
        for v in maptree.try_find(key, self._tree).to_list():
            value.append(v)
            return True
        else:
            return False

    def try_find(self, key: Key) -> Option[Value]:
        return maptree.try_find(key, self._tree)

    def to_list(self) -> FrozenList[Tuple[Key, Value]]:
        return maptree.to_list(self._tree)

    def to_seq(self) -> Iterable[Tuple[Key, Value]]:
        return maptree.to_seq(self._tree)

    @overload
    def of_list(lst: FrozenList[Tuple[Key, Value]]) -> "Map[Key, Value]":
        ...

    @overload
    def of_list(lst: List[Tuple[Key, Value]]) -> "Map[Key, Value]":
        ...

    @staticmethod
    def of_list(lst: Union[List[Tuple[Key, Value]], FrozenList[Tuple[Key, Value]]]) -> "Map[Key, Value]":
        return Map(maptree.of_list(FrozenList(lst)))

    #     member this.ComputeHashCode() =
    #         let combineHash x y = (x <<< 1) + y + 631
    #         let mutable res = 0
    #         for (KeyValue(x, y)) in this do
    #             res <- combineHash res (hash x)
    #             res <- combineHash res (Unchecked.hash y)
    #         res

    #     override this.GetHashCode() = this.ComputeHashCode()

    #     override this.Equals that =
    #         match that with
    #         | :? Map[Key, Value] as that ->
    #             use e1 = (this :> seq<_>).GetEnumerator()
    #             use e2 = (that :> seq<_>).GetEnumerator()
    #             let rec loop () =
    #                 let m1 = e1.MoveNext()
    #                 let m2 = e2.MoveNext()
    #                 (m1 = m2) && (not m1 ||
    #                                  (let e1c = e1.Current
    #                                   let e2c = e2.Current
    #                                   ((e1c.Key = e2c.Key) && (Unchecked.equals e1c.Value e2c.Value) && loop())))
    #             loop()
    #         | _ -> false

    #     interface IEnumerable<KeyValuePair<'Key, 'Value>> with
    #         member __.GetEnumerator() = maptree.mkIEnumerator tree

    #     interface System.Collections.IEnumerable with
    #         member __.GetEnumerator() = maptree.mkIEnumerator tree :> System.Collections.IEnumerator

    #     interface System.IComparable with
    #         def CompareTo(obj: obj) =
    #             match obj with
    #             | :? Map[Key, Value]  as m2->
    #                 Seq.compareWith
    #                    (fun (kvp1 : KeyValuePair<_, _>) (kvp2 : KeyValuePair<_, _>)->
    #                        let c = comparer.Compare(kvp1.Key, kvp2.Key) in
    #                        if c <> 0 then c else Unchecked.compare kvp1.Value kvp2.Value)
    #                    m m2
    #             | _ ->
    #                 invalidArg "obj" "not comparable"

    #     // interface IReadOnlyDictionary<'Key, 'Value> with
    #     //     def Item with get key = m.[key]
    #     //     def Keys = seq { for kvp in m -> kvp.Key }
    #     //     def TryGetValue(key, value: byref<'Value>) = m.TryGetValue(key, &value)
    #     //     def Values = seq { for kvp in m -> kvp.Value }
    #     //     def ContainsKey key = m.ContainsKey key

    def __str__(self) -> str:
        def to_str(item: Tuple[Key, Value]) -> str:
            key, value = item
            key = f'"{key}"' if isinstance(key, str) else key
            return f"({key}, {value})"

        items = pipe(self, Map.to_seq, seq.map(to_str))
        return f"map [{'; '.join(items)}]"

    def __repr__(self) -> str:
        return str(self)


def is_empty(table: Map[Key, Value]) -> bool:
    """Is the map empty?

    Args:
        table: The input map.

    Returns:
        True if the map is empty.
    """
    return table.is_empty()


def add(key: Key, value: Value, table: Map[Key, Value]) -> Map[Key, Value]:
    """Returns a new map with the binding added to the given map. If a
    binding with the given key already exists in the input map, the
    existing binding is replaced by the new binding in the result
    map.

    Args:
        key: The input key.
        value: The input value.
        table: The input table.

    Returns:
        The resulting map.
    """
    return table.add(key, value)


def change(key: Key, fn: Callable[[Option[Value]], Option[Value]], table: Map[Key, Value]) -> Map[Key, Value]:
    """Returns a new map with the value stored under key changed
    according to f.

    Args:
        key: The input key.
        fn: The change function.
        table: The input table.

    Returns:
        The input key.
    """
    return table.change(key, fn)


# def find(key: Key, table: Map[Key, Value]) -> Value:
#    table.find(key)

# // [<CompiledName("TryFind")>]
# let tryFind key (table: Map<_, _>) =
#     table.TryFind key


def remove(key: Key) -> Callable[[Map[Key, Value]], Map[Key, Value]]:
    """Removes an element from the domain of the map. No exception is
    raised if the element is not present.

    Args:
        key: The key to remove.
        table: The table to remove the key from.

    Returns:
        The resulting map.
    """

    def _remove(table: Map[Key, Value]) -> Map[Key, Value]:
        return table.remove(key)

    return _remove


# // [<CompiledName("ContainsKey")>]
# let containsKey key (table: Map<_, _>) =
#     table.ContainsKey key

# // [<CompiledName("Iterate")>]
# let iterate action (table: Map<_, _>) =
#     table.Iterate action

# // [<CompiledName("TryPick")>]
# let tryPick chooser (table: Map<_, _>) =
#     table.TryPick chooser

# // [<CompiledName("Pick")>]
# let pick chooser (table: Map<_, _>) =
#     match tryPick chooser table with
#     | None -> raise (KeyNotFoundException())
#     | Some res -> res


def exists(predicate: Callable[[Key, Value], bool], table: Map[Key, Value]) -> bool:
    return table.exists(predicate)


def filter(predicate: Callable[[Key, Value], bool]) -> Callable[[Map[Key, Value]], Map[Key, Value]]:
    def _filter(table: Map[Key, Value]) -> Map[Key, Value]:
        return table.filter(predicate)

    return _filter


def partition(
    predicate: Callable[[Key, Value], bool]
) -> Callable[[Map[Key, Value]], Tuple[Map[Key, Value], Map[Key, Value]]]:
    def _partition(table: Map[Key, Value]) -> Tuple[Map[Key, Value], Map[Key, Value]]:
        return table.partition(predicate)

    return _partition


# // [<CompiledName("ForAll")>]
# let forAll predicate (table: Map<_, _>) =
#     table.ForAll predicate


def map(mapping: Callable[[Value], Result]) -> Callable[[Map[Key, Value]], Map[Key, Result]]:
    def _map(table: Map[Key, Value]) -> Map[Key, Result]:
        return table.map(mapping)

    return _map


# // [<CompiledName("Fold")>]
# let fold<'Key, 'T, 'State when 'Key : comparison> folder (state:'State) (table: Map<'Key, 'T>) =
#     maptree.fold folder state table.Tree

# // [<CompiledName("FoldBack")>]
# let foldBack<'Key, 'T, 'State  when 'Key : comparison> folder (table: Map<'Key, 'T>) (state:'State) =
#     maptree.foldBack folder table.Tree state


def to_seq(table: Map[Key, Value]):
    return Map.to_seq(table)


# // [<CompiledName("FindKey")>]
# let findKey predicate (table : Map<_, _>) =
#     table |> Seq.pick (fun kvp -> let k = kvp.Key in if predicate k kvp.Value then Some k else None)

# // [<CompiledName("TryFindKey")>]
# let tryFindKey predicate (table : Map<_, _>) =
#     table |> Seq.tryPick (fun kvp -> let k = kvp.Key in if predicate k kvp.Value then Some k else None)


@overload
def of_list(elements: FrozenList[Tuple[Key, Value]]) -> Map[Key, Value]:
    ...


@overload
def of_list(elements: List[Tuple[Key, Value]]) -> Map[Key, Value]:
    ...


def of_list(elements: Union[List[Tuple[Key, Value]], FrozenList[Tuple[Key, Value]]]) -> Map[Key, Value]:
    return Map.of_list(FrozenList(elements))


def of_seq(elements: Iterable[Tuple[Key, Value]]) -> Map[Key, Value]:
    return Map.create(elements)


def to_list(table: Map[Key, Value]) -> FrozenList[Tuple[Key, Value]]:
    return table.to_list()


empty = Map.empty


# let createMutable (source: KeyValuePair<'Key, 'Value> seq) ([<Fable.Core.Inject>] comparer: IEqualityComparer<'Key>) =
#     let map = Fable.Collections.MutableMap(source, comparer)
#     map :> Fable.Core.JS.Map<_,_>

# let groupBy (projection: 'T -> 'Key) (xs: 'T seq) ([<Fable.Core.Inject>] comparer: IEqualityComparer<'Key>): ('Key * 'T seq) seq =
#     let dict: Fable.Core.JS.Map<_,ResizeArray<'T>> = createMutable Seq.empty comparer

#     // Build the groupings
#     for v in xs do
#         let key = projection v
#         if dict.has(key) then dict.get(key).Add(v)
#         else dict.set(key, ResizeArray [v]) |> ignore

#     // Mapping shouldn't be necessary because KeyValuePair compiles
#     // as a tuple, but let's do it just in case the implementation changes
#     dict.entries() |> Seq.map (fun (k,v) -> k, upcast v)

# let countBy (projection: 'T -> 'Key) (xs: 'T seq) ([<Fable.Core.Inject>] comparer: IEqualityComparer<'Key>): ('Key * int) seq =
#     let dict = createMutable Seq.empty comparer

#     for value in xs do
#         let key = projection value
#         if dict.has(key) then dict.set(key, dict.get(key) + 1)
#         else dict.set(key, 1)
#         |> ignore

#     dict.entries()


def count(table: Map[Key, Value]) -> int:
    return table.count()
