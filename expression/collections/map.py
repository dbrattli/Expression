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

from collections.abc import Callable, ItemsView, Iterable, Iterator, Mapping
from typing import Any, TypeVar, cast

from expression.core import Option, PipeMixin, SupportsLessThan, curry_flip, pipe

from . import maptree, seq
from .block import Block
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


class Map(Mapping[Key, Value], PipeMixin):
    """The immutable map class."""

    def __init__(self, __tree: MapTree[Key, Value] | None = None) -> None:
        self._tree: MapTree[Key, Value] = __tree if __tree else maptree.empty

    def add(self, key: Key, value: Value) -> Map[Key, Value]:
        return Map(maptree.add(key, value, self._tree))

    @staticmethod
    def create(ie: Iterable[tuple[Key, Value]]) -> Map[Key, Value]:
        return create(ie)

    def contains_key(self, key: Key) -> bool:
        return maptree.mem(key, self._tree)

    def change(
        self, key: Key, f: Callable[[Option[Value]], Option[Value]]
    ) -> Map[Key, Value]:
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
        """Test all elements in map.

        Returns true if the given predicate returns true for all of
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

    def fold(
        self, folder: Callable[[Result, tuple[Key, Value]], Result], state: Result
    ) -> Result:
        return maptree.fold(folder, state, self._tree)

    def fold_back(
        self, folder: Callable[[tuple[Key, Value], Result], Result], state: Result
    ) -> Result:
        return maptree.fold_back(folder, self._tree, state)

    def map(self, mapping: Callable[[Key, Value], Result]) -> Map[Key, Result]:
        """Map the mapping.

        Builds a new collection whose elements are the results of
        applying the given function to each of the elements of the
        collection. The key passed to the function indicates the key of
        element being transformed.

        Args:
            mapping: The function to transform the key/value pairs

        Returns:
            The resulting map of keys and transformed values.
        """
        return Map(maptree.map(mapping, self._tree))

    def partition(
        self, predicate: Callable[[Key, Value], bool]
    ) -> tuple[Map[Key, Value], Map[Key, Value]]:
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

    def items(self) -> ItemsView[Key, Value]:
        items = maptree.to_seq(self._tree)
        return ItemsView(dict(items))

    def remove(self, key: Key) -> Map[Key, Value]:
        return Map(maptree.remove(key, self._tree))

    def to_list(self) -> Block[tuple[Key, Value]]:
        return maptree.to_list(self._tree)

    def to_seq(self) -> Iterable[tuple[Key, Value]]:
        """Convert to sequence.

        Returns:
            Sequence of key, value tuples.
        """
        return maptree.to_seq(self._tree)

    def try_get_value(self, key: Key, value: list[Value]):
        for v in maptree.try_find(key, self._tree).to_list():
            value.append(v)
            return True
        else:
            return False

    def try_find(self, key: Key) -> Option[Value]:
        return maptree.try_find(key, self._tree)

    def try_pick(
        self, chooser: Callable[[Key, Value], Option[Result]]
    ) -> Option[Result]:
        return maptree.try_pick(chooser, self._tree)

    @staticmethod
    def of(**args: Value) -> Map[str, Value]:
        return Map(maptree.of_seq(args.items()))

    @staticmethod
    def of_block(lst: Block[tuple[Key, Value]]) -> Map[Key, Value]:
        """Generate map from list.

        Returns:
            The new map.
        """
        return of_block(lst)

    @staticmethod
    def of_list(lst: list[tuple[Key, Value]]) -> Map[Key, Value]:
        """Generate map from list.

        Returns:
            The new map.
        """
        return of_list(lst)

    @staticmethod
    def of_seq(sequence: Iterable[tuple[Key, Value]]) -> Map[Key, Value]:
        """Generate map from sequence.

        Generates a new map from an iterable of key/value tuples. This
        is an alias for `Map.create`.

        Returns:
            The new map.
        """
        return of_seq(sequence)

    def __hash__(self) -> int:  # type: ignore
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
        iterator: Iterator[tuple[Any, Any]] = iter(other.to_seq())

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
        def to_str(item: tuple[Key, Value]) -> str:
            key, value = item
            if isinstance(key, str):
                return f'("{key}", {value})'
            return f"({key}, {value})"

        items = pipe(self.to_seq(), seq.map(to_str))
        return f"map [{'; '.join(items)}]"

    def __repr__(self) -> str:
        return str(self)


@curry_flip(1)
def add(table: Map[Key, Value], key: Key, value: Value) -> Map[Key, Value]:
    """Add key with value to map.

    Returns a new map with the binding added to the given map. If a
    binding with the given key already exists in the input map, the
    existing binding is replaced by the new binding in the result
    map.

    Args:
        table: The input map.
        key: The input key.
        value: The input value.

    Returns:
        A partially applied add function that takes the input map and returns
        the output map.
    """
    return table.add(key, value)


@curry_flip(1)
def change(
    table: Map[Key, Value], key: Key, fn: Callable[[Option[Value]], Option[Value]]
) -> Map[Key, Value]:
    """Change element in map.

    Returns a new map with the value stored under key changed
    according to f.

    Args:
        key: The input key.
        fn: The change function.
        table: The input table.

    Returns:
        The input key.
    """
    return table.change(key, fn)


@curry_flip(1)
def contains_key(table: Map[Key, Any], key: Key) -> bool:
    return table.contains_key(key)


def count(table: Map[Any, Any]) -> int:
    """Return the number of bindings in the map."""
    return len(table)


def create(ie: Iterable[tuple[Key, Value]]) -> Map[Key, Value]:
    return Map(maptree.of_seq(ie))


@curry_flip(1)
def find(table: Map[Key, Value], key: Key) -> Value:
    """Find element with key in map.

    Lookup an element in the map, raising KeyNotFoundException if no
    binding exists in the map.

    Args:
        key: The key to find.
        table: The map to find the key in.

    """
    return table[key]


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


@curry_flip(1)
def try_pick(
    table: Map[Key, Value], chooser: Callable[[Key, Value], Option[Result]]
) -> Option[Result]:
    """Pick element in map.

    Searches the map looking for the first element where the given
    function returns a Some value.

    Args:
        table: The input map.
        chooser: The function to generate options from the key/value
            pairs.

    Returns:
        Partially applied `try_pick` function that takes the input map
        and returns the first result.
    """
    return table.try_pick(chooser)


@curry_flip(1)
def pick(
    table: Map[Key, Value], chooser: Callable[[Key, Value], Option[Result]]
) -> Result:
    for res in table.try_pick(chooser):
        return res
    else:
        raise KeyError()


@curry_flip(1)
def exists(table: Map[Key, Value], predicate: Callable[[Key, Value], bool]) -> bool:
    """Test if element exists in map.

    Returns true if the given predicate returns true for one of the
    bindings in the map.

    Args:
        table: The input map.
        predicate: The function to test the input elements.

    Returns:
        Partially applied function that takes a map table and returns
        true if the predicate returns true for one of the key/value
        pairs.
    """
    return table.exists(predicate)


@curry_flip(1)
def filter(
    table: Map[Key, Value], predicate: Callable[[Key, Value], bool]
) -> Map[Key, Value]:
    return table.filter(predicate)


@curry_flip(1)
def for_all(table: Map[Key, Value], predicate: Callable[[Key, Value], bool]) -> bool:
    return table.for_all(predicate)


@curry_flip(1)
def map(
    table: Map[Key, Value], mapping: Callable[[Key, Value], Result]
) -> Map[Key, Result]:
    return table.map(mapping)


@curry_flip(1)
def fold(
    table: Map[Key, Value],
    folder: Callable[[Result, tuple[Key, Value]], Result],
    state: Result,
) -> Result:
    return table.fold(folder, state)


@curry_flip(1)
def fold_back(
    state: Result,
    folder: Callable[[tuple[Key, Value], Result], Result],
    table: Map[Key, Value],
) -> Result:
    return table.fold_back(folder, state)


@curry_flip(1)
def partition(
    table: Map[Key, Value], predicate: Callable[[Key, Value], bool]
) -> tuple[Map[Key, Value], Map[Key, Value]]:
    return table.partition(predicate)


@curry_flip(1)
def remove(table: Map[Key, Value], key: Key) -> Map[Key, Value]:
    """Remove element from map.

    Removes an element from the domain of the map. No exception is
    raised if the element is not present.

    Args:
        key: The key to remove.
        table: The table to remove the key from.

    Returns:
        The resulting map.
    """
    return table.remove(key)


def of(**args: Value) -> Map[str, Value]:
    """Create map from arguments."""
    return Map(maptree.of_seq(args.items()))


def of_block(elements: Block[tuple[Key, Value]]) -> Map[Key, Value]:
    return Map(maptree.of_list(elements))


def of_list(elements: list[tuple[Key, Value]]) -> Map[Key, Value]:
    return Map(maptree.of_list(Block(elements)))


def of_seq(elements: Iterable[tuple[Key, Value]]) -> Map[Key, Value]:
    return Map(maptree.of_seq(elements))


def to_list(table: Map[Key, Value]) -> Block[tuple[Key, Value]]:
    return table.to_list()


def to_seq(table: Map[Key, Value]) -> Iterable[tuple[Key, Value]]:
    return table.to_seq()


@curry_flip(1)
def try_find(table: Map[Key, Value], key: Key) -> Option[Value]:
    """Try to find element with key in map.

    Lookup an element in the map, returning a `Some` value if the
    element is in the domain of the map and `Nothing` if not.

    Args:
        table: The input map.
        key: The input key.

    Returns:
        A partially applied `try_find` function that takes a map
        instance and returns the result.
    """
    return table.try_find(key)


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
    "of_block",
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
