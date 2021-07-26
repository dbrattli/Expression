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
from __future__ import annotations

from typing import Any, Callable, Iterable, Iterator, List, Mapping, Optional, Set, Tuple, TypeVar, cast, overload

from expression.core import Option, SupportsLessThan, pipe

from . import maptree, seq
from .frozenlist import FrozenList
from .maptree import MapTree

Key = TypeVar("Key", bound=SupportsLessThan)
Value = TypeVar("Value")
Result = TypeVar("Result")

T1 = TypeVar("T1")
T2 = TypeVar("T2")
T3 = TypeVar("T3")
T4 = TypeVar("T4")
T5 = TypeVar("T5")
T6 = TypeVar("T6")


class Map(Mapping[Key, Value]):
    """The immutable map class."""

    def __init__(self, __tree: Optional[MapTree[Key, Value]] = None) -> None:
        self._tree: MapTree[Key, Value] = __tree if __tree else maptree.empty

    def add(self, key: Key, value: Value) -> Map[Key, Value]:
        return Map(maptree.add(key, value, self._tree))

    @overload
    def pipe(self, __fn1: Callable[[Map[Key, Value]], Result]) -> Result:
        ...

    @overload
    def pipe(self, __fn1: Callable[[Map[Key, Value]], T1], __fn2: Callable[[T1], T2]) -> T2:
        ...

    @overload
    def pipe(self, __fn1: Callable[[Map[Key, Value]], T1], __fn2: Callable[[T1], T2], __fn3: Callable[[T2], T3]) -> T3:
        ...

    @overload
    def pipe(
        self,
        __fn1: Callable[[Map[Key, Value]], T1],
        __fn2: Callable[[T1], T2],
        __fn3: Callable[[T2], T3],
        __fn4: Callable[[T3], T4],
    ) -> T4:
        ...

    @overload
    def pipe(
        self,
        __fn1: Callable[[Map[Key, Value]], T1],
        __fn2: Callable[[T1], T2],
        __fn3: Callable[[T2], T3],
        __fn4: Callable[[T3], T4],
        __fn5: Callable[[T4], T5],
    ) -> T5:
        ...

    @overload
    def pipe(
        self,
        __fn1: Callable[[Map[Key, Value]], T1],
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
    def create(ie: Iterable[Tuple[Key, Value]]) -> Map[Key, Value]:
        return create(ie)

    def contains_key(self, key: Key) -> bool:
        return maptree.mem(key, self._tree)

    def change(self, key: Key, f: Callable[[Option[Value]], Option[Value]]) -> Map[Key, Value]:
        return Map(maptree.change(key, f, self._tree))

    @staticmethod
    def empty() -> Map[Key, Value]:
        return Map(maptree.empty)

    def is_empty(self) -> bool:
        return maptree.is_empty(self._tree)

    def exists(self, predicate: Callable[[Key, Value], bool]) -> bool:
        return maptree.exists(predicate, self._tree)

    def filter(self, predicate: Callable[[Key, Value], bool]) -> Map[Key, Value]:
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

    def fold_back(self, folder: Callable[[Tuple[Key, Value], Result], Result], state: Result) -> Result:
        return maptree.fold_back(folder, self._tree, state)

    def map(self, mapping: Callable[[Key, Value], Result]) -> Map[Key, Result]:
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

    def partition(self, predicate: Callable[[Key, Value], bool]) -> Tuple[Map[Key, Value], Map[Key, Value]]:
        r1, r2 = maptree.partition(predicate, self._tree)
        return Map(r1), Map(r2)

    # @overload
    # def get(self, key: Key) -> Optional[Value]:
    #    ...

    # @overload
    # def get(self, key: Key, default: Value) -> Value:
    #    ...

    # def get(self, key: Key, default: Union[Value, _T]) -> Union[Value, _T]:
    #    for value in self.try_find(key):
    #        return value

    #   return default

    def items(self) -> Set[Tuple[Key, Value]]:
        return set(maptree.to_seq(self._tree))

    def remove(self, key: Key) -> Map[Key, Value]:
        return Map(maptree.remove(key, self._tree))

    def to_list(self) -> FrozenList[Tuple[Key, Value]]:
        return maptree.to_list(self._tree)

    def to_seq(self) -> Iterable[Tuple[Key, Value]]:
        """Convert to sequence.

        Returns:
            Sequence of key, value tuples.
        """
        return maptree.to_seq(self._tree)

    def try_get_value(self, key: Key, value: List[Value]):
        for v in maptree.try_find(key, self._tree).to_list():
            value.append(v)
            return True
        else:
            return False

    def try_find(self, key: Key) -> Option[Value]:
        return maptree.try_find(key, self._tree)

    def try_pick(self, chooser: Callable[[Key, Value], Option[Result]]) -> Option[Result]:
        return maptree.try_pick(chooser, self._tree)

    @staticmethod
    def of(**args: Value) -> Map[str, Value]:
        return Map(maptree.of_seq(args.items()))

    @staticmethod
    def of_frozenlist(lst: FrozenList[Tuple[Key, Value]]) -> Map[Key, Value]:
        """Generate map from list.

        Returns:
            The new map.
        """
        return of_frozenlist((lst))

    @staticmethod
    def of_list(lst: List[Tuple[Key, Value]]) -> Map[Key, Value]:
        """Generate map from list.

        Returns:
            The new map.
        """
        return of_list((lst))

    @staticmethod
    def of_seq(sequence: Iterable[Tuple[Key, Value]]) -> Map[Key, Value]:
        """Generate map from sequence.

        Generates a new map from an iterable of key/value tuples. This
        is an alias for `Map.create`.

        Returns:
            The new map.
        """
        return of_seq(sequence)

    def __hash__(self) -> int:
        def combine_hash(x: int, y: int) -> int:
            return (x << 1) + y + 631

        res = 0
        for x, y in maptree.mk_iterator(self._tree):
            res = combine_hash(res, hash(x))
            res = combine_hash(res, hash(y))
        return res

    def __getitem__(self, k: Key) -> Value:
        return maptree.find(k, self._tree)

    def __iter__(self) -> Iterator[Key]:
        xs = maptree.mk_iterator(self._tree)
        return (k for (k, _) in xs)

    def __len__(self) -> int:
        """Return the number of bindings in the map."""
        return maptree.size(self._tree)

    def __contains__(self, o: Any) -> bool:
        return self.contains_key(o)

    def __eq__(self, o: Any) -> bool:
        if not isinstance(o, Map):
            return False

        other = cast(Map[Any, Any], o)
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
            if isinstance(key, str):
                return f'("{key}", {value})'
            return f"({key}, {value})"

        items = pipe(self.to_seq(), seq.map(to_str))
        return f"map [{'; '.join(items)}]"

    def __repr__(self) -> str:
        return str(self)


def add(key: Key, value: Value) -> Callable[[Map[Key, Value]], Map[Key, Value]]:
    """Add key with value to map.

    Returns a new map with the binding added to the given map. If a
    binding with the given key already exists in the input map, the
    existing binding is replaced by the new binding in the result
    map.

    Args:
        key: The input key.
        value: The input value.

    Returns:
        A partially applied add function that takes the input map and returns
        the output map.
    """

    def _add(table: Map[Key, Value]) -> Map[Key, Value]:
        """Add the partially applied key with value to map.

        Returns a new map with the binding added to the given map. If a
        binding with the given key already exists in the input map, the
        existing binding is replaced by the new binding in the result
        map.

        Args:
            table: The input table.

        Returns:
            The resulting map.
        """
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


def contains_key(key: Key) -> Callable[[Map[Key, Any]], bool]:
    def _contains_key(table: Map[Key, Any]) -> bool:
        return table.contains_key(key)

    return _contains_key


def count(table: Map[Any, Any]) -> int:
    """Return the number of bindings in the map."""
    return len(table)


def create(ie: Iterable[Tuple[Key, Value]]) -> Map[Key, Value]:
    return Map(maptree.of_seq(ie))


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


def is_empty(table: Map[Any, Any]) -> bool:
    """Is the map empty?

    Args:
        table: The input map.

    Returns:
        True if the map is empty.
    """
    return table.is_empty()


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


def pick(chooser: Callable[[Key, Value], Option[Result]]) -> Callable[[Map[Key, Value]], Result]:
    def _try_pick(table: Map[Key, Value]) -> Result:
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


def map(mapping: Callable[[Key, Value], Result]) -> Callable[[Map[Key, Value]], Map[Key, Result]]:
    def _map(table: Map[Key, Value]) -> Map[Key, Result]:
        return table.map(mapping)

    return _map


def fold(folder: Callable[[Result, Tuple[Key, Value]], Result], state: Result) -> Callable[[Map[Key, Value]], Result]:
    def _fold(table: Map[Key, Value]) -> Result:
        return table.fold(folder, state)

    return _fold


def fold_back(
    folder: Callable[[Tuple[Key, Value], Result], Result], table: Map[Key, Value]
) -> Callable[[Result], Result]:
    def _fold_back(state: Result) -> Result:
        return table.fold_back(folder, state)

    return _fold_back


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


# // [<CompiledName("FindKey")>]
# let findKey predicate (table : Map<_, _>) =
#     table |> Seq.pick (fun kvp -> let k = kvp.Key in if predicate k kvp.Value then Some k else None)

# // [<CompiledName("TryFindKey")>]
# let tryFindKey predicate (table : Map<_, _>) =
#     table |> Seq.tryPick (fun kvp -> let k = kvp.Key in if predicate k kvp.Value then Some k else None)


def of(**args: Value) -> Map[str, Value]:
    """Create map from arguments."""
    return Map(maptree.of_seq(args.items()))


def of_frozenlist(elements: FrozenList[Tuple[Key, Value]]) -> Map[Key, Value]:
    return Map(maptree.of_list(elements))


def of_list(elements: List[Tuple[Key, Value]]) -> Map[Key, Value]:
    return Map(maptree.of_list(FrozenList(elements)))


def of_seq(elements: Iterable[Tuple[Key, Value]]) -> Map[Key, Value]:
    return Map(maptree.of_seq(elements))


def to_list(table: Map[Key, Value]) -> FrozenList[Tuple[Key, Value]]:
    return table.to_list()


def to_seq(table: Map[Key, Value]) -> Iterable[Tuple[Key, Value]]:
    return table.to_seq()


def try_find(key: Key) -> Callable[[Map[Key, Value]], Option[Value]]:
    """Lookup an element in the map, returning a `Some` value if the
    element is in the domain of the map and `Nothing` if not.

    Args:
        key: The input key.

    Returns:
        A partially applied `try_find` function that takes a map
        instance and returns the result.
    """

    def _try_find(table: Map[Key, Value]) -> Option[Value]:
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

__all__ = [
    "Map",
    "add",
    "change",
    "create",
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
    "of",
    "of_frozenlist",
    "of_list",
    "of_seq",
    "partition",
    "pick",
    "remove",
    "to_list",
    "to_seq",
    "try_find",
    "try_pick",
]
