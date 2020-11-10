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

from typing import Any, Callable, Generic, Iterable, Iterator, List, Optional, Tuple, TypeVar, Union, cast, overload

from expression.core import Option, pipe

from . import maptree, seq
from .frozenlist import FrozenList
from .maptree import MapTree

Key = TypeVar("Key")
Value = TypeVar("Value")
Result = TypeVar("Result")

T1 = TypeVar("T1")
T2 = TypeVar("T2")
T3 = TypeVar("T3")
T4 = TypeVar("T4")
T5 = TypeVar("T5")
T6 = TypeVar("T6")


class Map(Generic[Key, Value]):
    """The immutable map class."""

    def __init__(self, __tree: Optional[MapTree[Key, Value]] = None, **kw: Value) -> None:
        tree: MapTree[str, Value] = maptree.of_seq(kw.items())
        self._tree = __tree if __tree is not None else tree

    @overload
    def pipe(self, __fn1: Callable[["Map[Key, Value]"], Result]) -> Result:
        ...

    @overload
    def pipe(self, __fn1: Callable[["Map[Key, Value]"], T1], __fn2: Callable[[T1], T2]) -> T2:
        ...

    @overload
    def pipe(
        self, __fn1: Callable[["Map[Key, Value]"], T1], __fn2: Callable[[T1], T2], __fn3: Callable[[T2], T3]
    ) -> T3:
        ...

    @overload
    def pipe(
        self,
        __fn1: Callable[["Map[Key, Value]"], T1],
        __fn2: Callable[[T1], T2],
        __fn3: Callable[[T2], T3],
        __fn4: Callable[[T3], T4],
    ) -> T4:
        ...

    @overload
    def pipe(
        self,
        __fn1: Callable[["Map[Key, Value]"], T1],
        __fn2: Callable[[T1], T2],
        __fn3: Callable[[T2], T3],
        __fn4: Callable[[T3], T4],
        __fn5: Callable[[T4], T5],
    ) -> T5:
        ...

    @overload
    def pipe(
        self,
        __fn1: Callable[["Map[Key, Value]"], T1],
        __fn2: Callable[[T1], T2],
        __fn3: Callable[[T2], T3],
        __fn4: Callable[[T3], T4],
        __fn5: Callable[[T4], T5],
        __fn6: Callable[[T5], T6],
    ) -> T6:
        ...

    def pipe(self, *args: Any) -> Any:
        """Pipe map through the given functions."""
        return pipe(self, *args)

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

    def try_pick(self, chooser: Callable[[Key, Value], Option[Result]]) -> Option[Result]:
        return maptree.try_pick(chooser, self._tree)

    def exists(self, predicate: Callable[[Key, Value], bool]) -> bool:
        return maptree.exists(predicate, self._tree)

    def filter(self, predicate: Callable[[Key, Value], bool]) -> "Map[Key, Value]":
        return Map(maptree.filter(predicate, self._tree))

    def for_all(self, predicate: Callable[[Key, Value], bool]) -> bool:
        """Returns true if the given predicate returns true for all of
        the bindings in the map.

        Args:
            predicate: The function to test the input elements.

        Returns:
            True if the predicate evaluates to true for all of the
            bindings in the map.
        """
        return maptree.forall(predicate, self._tree)

    def iterate(self, f: Callable[[Key, Value], None]) -> None:
        return maptree.iter(f, self._tree)

    #     def MapRange (f:'Value->'Result) =
    #         return Map<'Key, 'Result>(comparer, maptree.map f tree)

    def fold(self, folder: Callable[[Result, Tuple[Key, Value]], Result], state: Result) -> Result:
        return maptree.fold(folder, state, self._tree)

    def map(self, mapping: Callable[[Value], Result]) -> "Map[Key, Result]":
        """Builds a new collection whose elements are the results of
        applying the given function to each of the elements of the
        collection. The key passed to the function indicates the key of
        element being transformed.

        Args:
            mapping: The function to transform the key/value pairs

        Returns:
            The resulting map of keys and transformed values.
        """
        return Map(maptree.map(mapping, self._tree))

    def partition(self, predicate: Callable[[Key, Value], bool]) -> "Tuple[Map[Key, Value], Map[Key, Value]]":
        r1, r2 = maptree.partition(predicate, self._tree)
        return Map(r1), Map(r2)

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
        """Convert to sequence.

        Returns:
            Sequenc of key, value tuples.
        """
        return maptree.to_seq(self._tree)

    @overload
    def of_list(lst: FrozenList[Tuple[Key, Value]]) -> "Map[Key, Value]":
        ...

    @overload
    def of_list(lst: List[Tuple[Key, Value]]) -> "Map[Key, Value]":
        ...

    @staticmethod
    def of_list(lst: Union[List[Tuple[Key, Value]], FrozenList[Tuple[Key, Value]]]) -> "Map[Key, Value]":
        """Generate map from list.

        Returns:
            New map.
        """
        return Map(maptree.of_list(FrozenList(lst)))

    def __hash__(self) -> int:
        def combine_hash(x: int, y: int) -> int:
            return (x << 1) + y + 631

        res = 0
        for x, y in self:
            res = combine_hash(res, hash(x))
            res = combine_hash(res, hash(y))
        return res

    def __getitem__(self, key: Value) -> Value:
        return maptree.find(key, self._tree)

    def __iter__(self) -> Iterator[Tuple[Key, Value]]:
        return maptree.mk_iterator(self._tree)

    def __len__(self) -> int:
        """Return the number of bindings in the map."""
        return maptree.size(self._tree)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Map):
            return False

        other = cast(Map[Any, Any], other)
        iterator: Iterator[Tuple[Any, Any]] = iter(other.to_seq())

        for kv in self.to_seq():
            try:
                kv_other = next(iterator)
            except StopIteration:
                return False
            else:
                if kv != kv_other:
                    return False
        return True

    def __bool__(self) -> bool:
        return not maptree.is_empty(self._tree)

    def __str__(self) -> str:
        def to_str(item: Tuple[Key, Value]) -> str:
            key, value = item
            key = f'"{key}"' if isinstance(key, str) else key
            return f"({key}, {value})"

        items = pipe(self, Map.to_seq, seq.map(to_str))
        return f"map [{'; '.join(items)}]"

    def __repr__(self) -> str:
        return str(self)


def add(key: Key, value: Value) -> Callable[[Map[Key, Value]], Map[Key, Value]]:
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

    def _add(table: Map[Key, Value]) -> Map[Key, Value]:
        return table.add(key, value)

    return _add


def change(key: Key, fn: Callable[[Option[Value]], Option[Value]]) -> Callable[[Map[Key, Value]], Map[Key, Value]]:
    """Returns a new map with the value stored under key changed
    according to f.

    Args:
        key: The input key.
        fn: The change function.
        table: The input table.

    Returns:
        The input key.
    """

    def _change(table: Map[Key, Value]) -> Map[Key, Value]:
        return table.change(key, fn)

    return _change


def count(table: Map[Key, Value]) -> int:
    """Return the number of bindings in the map."""
    return len(table)


def find(key: Key) -> Callable[[Map[Key, Value]], Value]:
    """Lookup an element in the map, raising KeyNotFoundException if no
    binding exists in the map

    Args:
        key: The key to find.
        table: The map to find the key in.

    """

    def _find(table: Map[Key, Value]) -> Value:
        return table[key]

    return _find


def is_empty(table: Map[Key, Value]) -> bool:
    """Is the map empty?

    Args:
        table: The input map.

    Returns:
        True if the map is empty.
    """
    return table.is_empty()


def contains_key(key: Key) -> Callable[[Map[Key, Value]], bool]:
    def _contains_key(table: Map[Key, Value]) -> bool:
        return table.contains_key(key)

    return _contains_key


def iterate(action: Callable[[Key, Value], None]) -> Callable[[Map[Key, Value]], None]:
    def _iterate(table: Map[Key, Value]) -> None:
        return table.iterate(action)

    return _iterate


def try_pick(chooser: Callable[[Key, Value], Option[Result]]) -> Callable[[Map[Key, Value]], Option[Result]]:
    """Searches the map looking for the first element where the given
    function returns a Some value.

    Args:
        chooser: The function to generate options from the key/value
            pairs.
    Returns:
        Partially applied `try_pick` function that takes the input map
        and returns the first result.
    """

    def _try_pick(table: Map[Key, Value]) -> Option[Result]:
        return table.try_pick(chooser)

    return _try_pick


def pick(chooser: Callable[[Key, Value], Option[Result]]) -> Callable[[Map[Key, Value]], Option[Result]]:
    def _try_pick(table: Map[Key, Value]) -> Option[Result]:
        for res in table.try_pick(chooser):
            return res
        else:
            raise KeyError()

    return _try_pick


def exists(predicate: Callable[[Key, Value], bool]) -> Callable[[Map[Key, Value]], bool]:
    """Returns true if the given predicate returns true for one of the bindings in the map.

    Args:
        predicate: The function to test the input elements.

    Returns:
        Partially applied function that takes a map table and returns
        true if the predicate returns true for one of the key/value
        pairs.
    """

    def _exists(table: Map[Key, Value]) -> bool:
        return table.exists(predicate)

    return _exists


def filter(predicate: Callable[[Key, Value], bool]) -> Callable[[Map[Key, Value]], Map[Key, Value]]:
    def _filter(table: Map[Key, Value]) -> Map[Key, Value]:
        return table.filter(predicate)

    return _filter


def for_all(predicate: Callable[[Key, Value], bool]) -> Callable[[Map[Key, Value]], bool]:
    def _for_all(table: Map[Key, Value]) -> bool:
        return table.for_all(predicate)

    return _for_all


def map(mapping: Callable[[Value], Result]) -> Callable[[Map[Key, Value]], Map[Key, Result]]:
    def _map(table: Map[Key, Value]) -> Map[Key, Result]:
        return table.map(mapping)

    return _map


def fold(folder: Callable[[Result, Tuple[Key, Value]], Result], state: Result) -> Callable[[Map[Key, Value]], Result]:
    def _fold(table: Map[Key, Value]) -> Result:
        return table.fold(folder, state)

    return _fold


# // [<CompiledName("FoldBack")>]
# let foldBack<'Key, 'T, 'State  when 'Key : comparison> folder (table: Map<'Key, 'T>) (state:'State) =
#     maptree.foldBack folder table.Tree state


def partition(
    predicate: Callable[[Key, Value], bool]
) -> Callable[[Map[Key, Value]], Tuple[Map[Key, Value], Map[Key, Value]]]:
    def _partition(table: Map[Key, Value]) -> Tuple[Map[Key, Value], Map[Key, Value]]:
        return table.partition(predicate)

    return _partition


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


def try_find(key: Key) -> Callable[[Map[Key, Value]], Option[Value]]:
    """Lookup an element in the map, returning a `Some` value if the
    element is in the domain of the map and `Nothing` if not.

    Args:
        key: The input key.

    Returns:
        A partially applied `try_find` function that takes a map
        instance and returns the result.
    """

    def _try_find(table: Map[Key, Value]):
        """Lookup an element in the map, returning a `Some` value if the
        element is in the domain of the map and `Nothing` if not.

        Args:
            key: The input key.

        Returns:
            The found `Some` value or `Nothing`.
        """
        return table.try_find(key)

    return _try_find


empty: Map[Any, Any] = Map.empty()

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


__all__ = [
    "Map",
    "add",
    "change",
    "contains_key",
    "count",
    "empty",
    "exists",
    "filter",
    "find",
    "fold",
    "for_all",
    "is_empty",
    "iterate",
    "map",
    "of_list",
    "partition",
    "pick",
    "remove",
    "to_list",
    "to_seq",
    "try_find",
    "try_pick",
]
