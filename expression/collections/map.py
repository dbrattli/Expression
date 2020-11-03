# Copyright (c) Microsoft Corporation.  All Rights Reserved.  See
# License.txt in the project root for license information.

from typing import Callable, Generic, Iterable, List, Tuple, TypeVar

from expression.core import Option

from . import maptree as maptree
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

    #     def Exists predicate =
    #         maptree.exists predicate tree

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
        for v in maptree.try_find(key, self._tree):
            value.append(v)
            return True
        else:
            return False

    def try_find(self, key: Key) -> Option[Value]:
        return maptree.try_find(key, self._tree)


#     def ToList() =
#         maptree.toList tree

#     def ToArray() =
#         maptree.toArray tree

#     static member ofList l : Map[Key, Value]:
#        let comparer = LanguagePrimitives.FastGenericComparer<'Key>
#        return Map<_, _>(comparer, maptree.ofList comparer l)

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

#     interface ICollection<KeyValuePair<'Key, 'Value>> with
#         def Add x = ignore x; raise (System.NotSupportedException("Map cannot be mutated"))
#         def Clear() = raise (System.NotSupportedException("Map cannot be mutated"))
#         def Remove x = ignore x; raise (System.NotSupportedException("Map cannot be mutated"))
#         def Contains x = m.ContainsKey x.Key && Unchecked.equals m.[x.Key] x.Value
#         def CopyTo(arr, i) = maptree.copyToArray tree arr i
#         def IsReadOnly = true
#         def Count = m.Count

#     interface IReadOnlyCollection<KeyValuePair<'Key, 'Value>> with
#         def Count = m.Count

#     // interface IReadOnlyDictionary<'Key, 'Value> with
#     //     def Item with get key = m.[key]
#     //     def Keys = seq { for kvp in m -> kvp.Key }
#     //     def TryGetValue(key, value: byref<'Value>) = m.TryGetValue(key, &value)
#     //     def Values = seq { for kvp in m -> kvp.Value }
#     //     def ContainsKey key = m.ContainsKey key

#     interface Fable.Core.JS.Map<'Key,'Value> with
#         def size = m.Count
#         def clear() = failwith "Map cannot be mutated"; ()
#         def delete(_) = failwith "Map cannot be mutated"; false
#         def entries() = m |> Seq.map (fun p -> p.Key, p.Value)
#         def get(k) = m.Item(k)
#         def has(k) = m.ContainsKey(k)
#         def keys() = m |> Seq.map (fun p -> p.Key)
#         def set(k, v) = failwith "Map cannot be mutated"; m :> Fable.Core.JS.Map<'Key,'Value>
#         def values() = m |> Seq.map (fun p -> p.Value)
#         def forEach(f, ?thisArg) = m |> Seq.iter (fun p -> f p.Value p.Key m)

#     override this.ToString() =
#         let inline toStr (kv: KeyValuePair<'Key,'Value>) = System.String.Format("({0}, {1})", kv.Key, kv.Value)
#         let str = this |> Seq.map toStr |> String.concat "; "
#         "map [" + str + "]"

# // [<CompilationRepresentation(CompilationRepresentationFlags.ModuleSuffix)>]
# // [<RequireQualifiedAccess>]
# // module Map =

# // [<CompiledName("is_empty")>]
# let is_empty (table: Map<_, _>) =
#     table.is_empty

# // [<CompiledName("Add")>]
# let add key value (table: Map<_, _>) =
#     table.Add (key, value)

# // [<CompiledName("Change")>]
# let change key f (table: Map<_, _>) =
#     table.Change (key, f)

# // [<CompiledName("Find")>]
# let find key (table: Map<_, _>) =
#     table.[key]

# // [<CompiledName("TryFind")>]
# let tryFind key (table: Map<_, _>) =
#     table.TryFind key


def remove(key: Key) -> Callable[[Map[Key, Value]], Map[Key, Value]]:
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

# // [<CompiledName("Exists")>]
# let exists predicate (table: Map<_, _>) =
#     table.Exists predicate

# // [<CompiledName("Filter")>]
# let filter predicate (table: Map<_, _>) =
#     table.Filter predicate

# // [<CompiledName("Partition")>]
# let partition predicate (table: Map<_, _>) =
#     table.Partition predicate

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

# // [<CompiledName("ToSeq")>]
# let toSeq (table: Map<_, _>) =
#     table |> Seq.map (fun kvp -> kvp.Key, kvp.Value)

# // [<CompiledName("FindKey")>]
# let findKey predicate (table : Map<_, _>) =
#     table |> Seq.pick (fun kvp -> let k = kvp.Key in if predicate k kvp.Value then Some k else None)

# // [<CompiledName("TryFindKey")>]
# let tryFindKey predicate (table : Map<_, _>) =
#     table |> Seq.tryPick (fun kvp -> let k = kvp.Key in if predicate k kvp.Value then Some k else None)

# // [<CompiledName("OfList")>]
# let ofList (elements: ('Key * 'Value) list) =
#     Map<_, _>.ofList elements


def of_seq(elements: Iterable[Tuple[Key, Value]]) -> Map[Key, Value]:
    return Map.create(elements)


# // [<CompiledName("OfArray")>]
# let ofArray (elements: ('Key * 'Value) array) =
#    let comparer = LanguagePrimitives.FastGenericComparer<'Key>
#    new Map<_, _>(comparer, maptree.ofArray comparer elements)

# // [<CompiledName("ToList")>]
# let toList (table: Map<_, _>) =
#     table.ToList()

# // [<CompiledName("ToArray")>]
# let toArray (table: Map<_, _>) =
#     table.ToArray()

# // [<CompiledName("Empty")>]
# let empty<'Key, 'Value  when 'Key : comparison> =
#     Map[Key, Value].Empty

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

# // [<CompiledName("Count")>]
# let count (table: Map<_, _>) =
#     table.Count
