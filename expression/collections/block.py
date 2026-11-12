"""A frozen immutable list module.

This module provides an immutable list type `Block` and  a set of
useful methods and functions for working with the list.

Named "Block" to avoid conflicts with the builtin Python List type.

A Block is actually backed by a Python tuple. Tuples in Python are
immutable and gives us a high performant implementation of immutable
lists.

Example:
    >>> xs = block.of_list([1, 2, 3, 4, 5])
    >>> ys = block.empty.cons(1).cons(2).cons(3).cons(4).cons(5)
    >>> zs = pipe(
    ...     xs,
    ...     block.filter(lambda x: x<10)
    ... )
"""

from __future__ import annotations

import builtins
import functools
import itertools
from collections.abc import Callable, Collection, Iterable, Iterator, Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal, TypeVar, Unpack, get_args, overload


if TYPE_CHECKING:
    from pydantic import GetCoreSchemaHandler
    from pydantic_core import CoreSchema

from expression.core import (
    NOTHING,
    Option,
    PipeMixin,
    Some,
    SupportsLessThan,
    SupportsSum,
    curry_flip,
    pipe,
)

from . import seq


_TSource = TypeVar("_TSource")


# Keep implicit generics here: early Python 3.12 dataclasses lose the weakref
# slot when PEP 695 adds typing.Generic as a direct base.
@dataclass(frozen=True, slots=True, weakref_slot=True, init=False, eq=False, repr=False)
class Block(Collection[_TSource], PipeMixin):
    """Immutable list type.

    Is faster than `List` for prepending, but slower for
    appending.

    Count: 200K::

        | Operation | Block      | List   |
        |-----------|------------|--------|
        | Append    | 3.29 s     | 0.02 s |
        | Prepend   | 0.05 s     | 7.02 s |

    Example:
        >>> xs = Cons(5, Cons(4, Cons(3, Cons(2, Cons(1, Nil)))))
        >>> ys = empty.cons(1).cons(2).cons(3).cons(4).cons(5)
    """

    __match_args__ = ("_value",)

    _value: tuple[_TSource, ...]

    def __init__(self, value: Iterable[_TSource] = ()) -> None:
        # Use composition instead of inheritance since generic tuples
        # are not suppored by mypy.
        object.__setattr__(self, "_value", tuple(value) if value else tuple())

    def append(self, other: Block[_TSource]) -> Block[_TSource]:
        """Append other block to end of the block."""
        return Block(self._value + other._value)

    def choose[TResult](self, chooser: Callable[[_TSource], Option[TResult]]) -> Block[TResult]:
        """Choose items from the list.

        Applies the given function to each element of the list. Returns
        the list comprised of the results x for each element where the
        function returns `Some(x)`.

        Args:
            chooser: The function to generate options from the elements.

        Returns:
            The list comprising the values selected from the chooser
            function.
        """

        def mapper(x: _TSource) -> Block[TResult]:
            return Block(chooser(x).to_seq())

        return self.collect(mapper)

    def collect[TResult](self, mapping: Callable[[_TSource], Block[TResult]]) -> Block[TResult]:
        """Collect items from the list.

        Applies the given function to each element of the list and concatenates all the
        resulting sequences. This function is known as `bind` or `flat_map` in other
        languages.

        Args:
            mapping: The function to generate sequences from the elements.

        Returns:
            A list comprising the concatenated values from the mapping
            function.
        """
        mapped = builtins.map(mapping, self._value)
        xs = (y for x in mapped for y in x)
        return Block(xs)

    def cons(self, element: _TSource) -> Block[_TSource]:
        """Add element to front of list."""
        return Block((element, *self._value))  # NOTE: Faster than (element, *self)

    @staticmethod
    def empty() -> Block[Any]:
        """Returns empty list."""
        return Block()

    def filter(self, predicate: Callable[[_TSource], bool]) -> Block[_TSource]:
        """Filter list.

        Returns a new collection containing only the elements of the
        collection for which the given predicate returns `True`.

        Args:
            predicate: The function to test the input elements.

        Returns:
            A list containing only the elements that satisfy the
            predicate.
        """
        return Block(builtins.filter(predicate, self._value))

    def fold[TState](self, folder: Callable[[TState, _TSource], TState], state: TState) -> TState:
        """Fold block.

        Applies a function to each element of the collection,
        threading an accumulator argument through the computation. Take
        the second argument, and apply the function to it and the first
        element of the list. Then feed this result into the function
        along with the second element and so on. Return the final
        result. If the input function is f and the elements are i0...iN
        then computes f (... (f s i0) i1 ...) iN.

        Args:
            folder: The function to update the state given the input
                elements.

            state: The initial state.

        Returns:
            Partially applied fold function that takes the source list
            and returns the final state value.
        """
        return functools.reduce(folder, self, state)

    def forall(self, predicate: Callable[[_TSource], bool]) -> bool:
        """For all elements in block.

        Tests if all elements of the collection satisfy the given
        predicate.

        Args:
            predicate: The function to test the input elements.

        Returns:
            True if all of the elements satisfy the predicate.
        """
        return all(predicate(x) for x in self)

    def head(self) -> _TSource:
        """Returns the first element of the list.

        Args:
            source: The input list.

        Returns:
            The first element of the list.

        Raises:
            ValueError: Thrown when the list is empty.
        """
        head, *_ = self
        return head

    def indexed(self, start: int = 0) -> Block[tuple[int, _TSource]]:
        """Index elements in block.

        Returns a new list whose elements are the corresponding
        elements of the input list paired with the index (from `start`)
        of each element.

        Args:
            start: Optional index to start from. Defaults to 0.

        Returns:
            The list of indexed elements.
        """
        return of_seq(enumerate(self))

    def item(self, index: int) -> _TSource:
        """Indexes into the list. The first element has index 0.

        Args:
            index: The index to retrieve.

        Returns:
            The value at the given index.
        """
        return self[index]

    def is_empty(self) -> bool:
        """Return `True` if list is empty."""
        return not bool(self)

    def map[TResult](self, mapping: Callable[[_TSource], TResult]) -> Block[TResult]:
        """Map list.

        Builds a new collection whose elements are the results of
        applying the given function to each of the elements of the
        collection.

        Args:
            mapping: The function to transform elements from the input
                list.

        Returns:
            The list of transformed elements.
        """
        return Block((*builtins.map(mapping, self),))

    def starmap[*P, TResult](self: Block[tuple[*P]], mapping: Callable[[Unpack[P]], TResult]) -> Block[TResult]:
        """Starmap source sequence.

        Unpack arguments grouped as tuple elements. Builds a new collection
        whose elements are the results of applying the given function to the
        unpacked arguments to each of the elements of the collection.

        Args:
            mapping: A function to transform items from the input sequence.

        Returns:
            Partially applied map function.
        """
        return Block(starmap(mapping)(self))

    def sum[TSourceSum: SupportsSum](self: Block[TSourceSum | Literal[0]]) -> TSourceSum | Literal[0]:
        return builtins.sum(self._value)

    def sum_by[TSourceSum: SupportsSum, TResult](
        self: Block[TSourceSum], projection: Callable[[TSourceSum], TResult]
    ) -> TResult:
        return pipe(self, sum_by(projection))

    def mapi[TResult](self, mapping: Callable[[int, _TSource], TResult]) -> Block[TResult]:
        """Map list with index.

        Builds a new collection whose elements are the results of
        applying the given function to each of the elements of the
        collection. The integer index passed to the function indicates
        the index (from 0) of element being transformed.

        Args:
            mapping: The function to transform elements and their
                indices.

        Returns:
            The list of transformed elements.
        """
        return Block((*itertools.starmap(mapping, enumerate(self)),))

    @staticmethod
    def of[TResult](*args: TResult) -> Block[TResult]:
        """Create list from a number of arguments."""
        return Block((*args,))

    @staticmethod
    def of_seq[TResult](xs: Iterable[TResult]) -> Block[TResult]:
        """Create list from iterable sequence."""
        return Block((*xs,))

    @staticmethod
    def of_option[TResult](option: Option[TResult]) -> Block[TResult]:
        return of_option(option)

    def partition(self, predicate: Callable[[_TSource], bool]) -> tuple[Block[_TSource], Block[_TSource]]:
        """Partition block.

        Splits the collection into two collections, containing the
        elements for which the given predicate returns True and False
        respectively. Element order is preserved in both of the created
        lists.

        Args:
            predicate: The function to test the input elements.

        Returns:
            A list containing the elements for which the predicate
            evaluated to true and a list containing the elements for
            which the predicate evaluated to false.
        """
        list1: list[_TSource] = []
        list2: list[_TSource] = []

        for item in self._value:
            if predicate(item):
                list1.append(item)
            else:
                list2.append(item)
        return (Block(list1), Block(list2))

    @overload
    @staticmethod
    def range(stop: int) -> Block[int]: ...

    @overload
    @staticmethod
    def range(start: int, stop: int) -> Block[int]: ...

    @overload
    @staticmethod
    def range(start: int, stop: int, step: int) -> Block[int]: ...

    @staticmethod
    def range(*args: int, **kw: int) -> Block[int]:
        return range(*args, **kw)

    def reduce(
        self,
        reduction: Callable[[_TSource, _TSource], _TSource],
    ) -> _TSource:
        """Reduce block.

        Apply a function to each element of the collection, threading an
        accumulator argument through the computation. Apply the function to
        the first two elements of the list. Then feed this result into the
        function along with the third element and so on. Return the final
        result. If the input function is f and the elements are i0...iN then
        computes f (... (f i0 i1) i2 ...) iN.

        Args:
            reduction: The function to reduce two list elements to a
            single element.

        Returns:
            Returns the final state value.
        """
        return reduce(reduction)(self)

    @staticmethod
    def singleton[TResult](item: TResult) -> Block[TResult]:
        return singleton(item)

    def skip(self, count: int) -> Block[_TSource]:
        """Returns the list after removing the first N elements.

        Args:
            count: The number of elements to skip.

        Returns:
            The list after removing the first N elements.
        """
        return Block(self._value[count:])

    def skip_last(self, count: int) -> Block[_TSource]:
        return Block(self._value[:-count] if count != 0 else self._value)

    def tail(self) -> Block[_TSource]:
        """Return tail of List."""
        _, *tail = self._value
        return Block(tail)

    def sort[TSourceSortable: SupportsLessThan](
        self: Block[TSourceSortable], reverse: bool = False
    ) -> Block[TSourceSortable]:
        """Sort list directly.

        Returns a new sorted collection.

        Args:
            reverse: Sort in reversed order.

        Returns:
            A sorted list.
        """
        return Block(builtins.sorted(self._value, reverse=reverse))

    def sort_with(self, func: Callable[[_TSource], Any], reverse: bool = False) -> Block[_TSource]:
        """Sort list with supplied function.

        Returns a new sorted collection.

        Args:
            func: The function to extract a comparison key from each element in list.
            reverse: Sort in reversed order.

        Returns:
            A sorted list.
        """
        return Block(builtins.sorted(self._value, key=func, reverse=reverse))

    def take(self, count: int) -> Block[_TSource]:
        """Returns the first N elements of the list.

        Args:
            count: The number of items to take.

        Returns:
            The result list.
        """
        return Block(self._value[:count])

    def take_last(self, count: int) -> Block[_TSource]:
        """Take last elements from block.

        Returns a specified number of contiguous elements from the
        end of the list.

        Args:
            count: The number of items to take.

        Returns:
            The result list.
        """
        return Block(self._value[-count:] if count != 0 else ())

    def dict(self) -> list[_TSource]:
        """Returns a json serializable representation of the list."""

        def to_obj(value: Any) -> Any:
            attr = getattr(value, "model_dump", None) or getattr(value, "dict", None)
            if attr and callable(attr):
                value = attr()
            return value

        return [to_obj(value) for value in self._value]

    def try_head(self) -> Option[_TSource]:
        """Try to get head of block.

        Returns the first element of the list, or None if the list is
        empty.
        """
        if self._value:
            value = self._value[0]
            return Some(value)

        return NOTHING

    @staticmethod
    def unfold[TResult, TState](
        generator: Callable[[TState], Option[tuple[TResult, TState]]], state: TState
    ) -> Block[TResult]:
        """Unfold block.

        Returns a list that contains the elements generated by the
        given computation. The given initial state argument is passed to
        the element generator.

        Args:
            generator: A function that takes in the current state and
                returns an option tuple of the next element of the list
                and the next state value.
            state: The initial state.

        Returns:
            The result list.
        """
        return pipe(state, unfold(generator))

    def zip[TResult](self, other: Block[TResult]) -> Block[tuple[_TSource, TResult]]:
        """Zip block.

        Combines the two lists into a list of pairs. The two lists
        must have equal lengths. .

        Args:
            other: The second input list.

        Returns:
            A single list containing pairs of matching elements from the
            input lists.
        """
        return of_seq(builtins.zip(self._value, other._value))

    def __add__(self, other: Block[_TSource]) -> Block[_TSource]:
        return Block(self._value + other._value)

    def __contains__(self, value: Any) -> bool:
        for v in self:
            if v is value or v == value:
                return True
        return False

    @overload
    def __getitem__(self, key: slice) -> Block[_TSource]: ...

    @overload
    def __getitem__(self, key: int) -> _TSource: ...

    def __getitem__(self, key: slice | int) -> Block[_TSource] | _TSource:
        if isinstance(key, slice):
            return Block(self._value[key])
        return self._value[key]

    def __iter__(self) -> Iterator[_TSource]:
        return iter(self._value)

    def __eq__(self, o: Any) -> bool:
        return self._value == o

    def __len__(self) -> int:
        return len(self._value)

    def __str__(self) -> str:
        return f"[{', '.join(self.map(str))}]"

    def __repr__(self) -> str:
        return str(self)

    @classmethod
    def __get_pydantic_core_schema__(cls, source: Any, handler: GetCoreSchemaHandler) -> CoreSchema:
        from pydantic_core import core_schema

        instance_schema = core_schema.is_instance_schema(cls)

        args = get_args(source)
        if args:
            # replace the type and rely on Pydantic to generate the right schema
            # for `Sequence`
            sequence_t_schema = handler.generate_schema(Sequence[args[0]])  # type: ignore
        else:
            sequence_t_schema = handler.generate_schema(Sequence)

        non_instance_schema = core_schema.no_info_after_validator_function(Block, sequence_t_schema)
        python_schema = core_schema.union_schema([instance_schema, non_instance_schema])
        return core_schema.json_or_python_schema(
            json_schema=non_instance_schema,
            python_schema=python_schema,
            serialization=core_schema.plain_serializer_function_ser_schema(lambda instance: instance.dict()),
        )


@curry_flip(1)
def append[TSource](source: Block[TSource], other: Block[TSource]) -> Block[TSource]:
    return source.append(other)


@curry_flip(1)
def choose[TSource, TResult](source: Block[TSource], chooser: Callable[[TSource], Option[TResult]]) -> Block[TResult]:
    return source.choose(chooser)


@curry_flip(1)
def collect[TSource, TResult](source: Block[TSource], mapping: Callable[[TSource], Block[TResult]]) -> Block[TResult]:
    """Collect items from the list.

    Applies the given function to each element of the list and
    concatenates all the resulting sequences. This function is known as
    `bind` or `flat_map` in other languages.

    Args:
        source: The input list (curried flipped).
        mapping: The function to generate sequences from the elements.

    Returns:
        A sequence comprising the concatenated values from the mapping
        function.
    """
    return source.collect(mapping)


def concat[TSource](sources: Iterable[Block[TSource]]) -> Block[TSource]:
    """Concatenate sequence of Block's."""

    def reducer(t: Block[TSource], s: Block[TSource]) -> Block[TSource]:
        return t.append(s)

    return pipe(sources, seq.fold(reducer, empty))


def cons[TSource](head: TSource, tail: Block[TSource]) -> Block[TSource]:
    return Block((head, *tail))


nil: Block[Any] = Block()
empty: Block[Any] = nil
"""The empty list."""


@curry_flip(1)
def filter[TSource](source: Block[TSource], predicate: Callable[[TSource], bool]) -> Block[TSource]:
    """Filter elements in block.

    Returns a new collection containing only the elements of the
    collection for which the given predicate returns `True`.

    Args:
        source: The input block to filter.
        predicate: The function to test the input elements.

    Returns:
        Partially applied filter function.
    """
    return source.filter(predicate)


@curry_flip(1)
def fold[TSource, TState](
    source: Block[TSource],
    folder: Callable[[TState, TSource], TState],
    state: TState,
) -> TState:
    """Fold elements in block.

    Applies a function to each element of the collection, threading
    an accumulator argument through the computation. Take the second
    argument, and apply the function to it and the first element of the
    list. Then feed this result into the function along with the second
    element and so on. Return the final result. If the input function is
    f and the elements are i0...iN then computes f (... (f s i0) i1 ...)
    iN.

    Args:
        source: The input block to fold.
        folder: The function to update the state given the input
            elements.

        state: The initial state.

    Returns:
        Partially applied fold function that takes the source list
        and returns the final state value.
    """
    return source.fold(folder, state)


@curry_flip(1)
def forall[TSource](source: Block[TSource], predicate: Callable[[TSource], bool]) -> bool:
    """For all elements in block.

    Tests if all elements of the collection satisfy the given
    predicate.

    Args:
        source: The input block to test.
        predicate: The function to test the input elements.

    Returns:
        True if all of the elements satisfy the predicate.
    """
    return source.forall(predicate)


def head[TSource](source: Block[TSource]) -> TSource:
    """Returns the first element of the list.

    Args:
        source: The input list.

    Returns:
        The first element of the list.

    Raises:
         ValueError: Thrown when the list is empty.
    """
    return source.head()


def indexed[TSource](source: Block[TSource]) -> Block[tuple[int, TSource]]:
    """Index elements in block.

    Returns a new list whose elements are the corresponding
    elements of the input list paired with the index (from 0)
    of each element.

    Returns:
        The list of indexed elements.
    """
    return source.indexed()


@curry_flip(1)
def item[TSource](source: Block[TSource], index: int) -> TSource:
    """Indexes into the list. The first element has index 0.

    Args:
        source: The input block list.
        index: The index to retrieve.

    Returns:
        The value at the given index.
    """
    return source.item(index)


def is_empty(source: Block[Any]) -> bool:
    """Returns `True` if the list is empty, `False` otherwise."""
    return source.is_empty()


@curry_flip(1)
def map[TSource, TResult](source: Block[TSource], mapper: Callable[[TSource], TResult]) -> Block[TResult]:
    """Map list.

    Builds a new collection whose elements are the results of applying
    the given function to each of the elements of the collection.

    Args:
        source: The input list (curried flipped).
        mapper: The function to transform elements from the input list.

    Returns:
        The list of transformed elements.
    """
    return source.map(mapper)


@curry_flip(1)
def reduce[TSource](
    source: Block[TSource],
    reduction: Callable[[TSource, TSource], TSource],
) -> TSource:
    """Reduce elements in block.

    Apply a function to each element of the collection, threading an
    accumulator argument through the computation. Apply the function to
    the first two elements of the list. Then feed this result into the
    function along with the third element and so on. Return the final
    result. If the input function is f and the elements are i0...iN then
    computes f (... (f i0 i1) i2 ...) iN.

    Args:
        source: The input block (curried flipped)
        reduction: The function to reduce two list elements to a single
            element.

    Returns:
        Partially applied reduce function that takes the source block
        and returns the final state value.
    """
    if source.is_empty():
        raise ValueError("Collection was empty")

    return source.tail().fold(reduction, source.head())


def starmap[TResult, *P](mapper: Callable[[Unpack[P]], TResult]) -> Callable[[Block[tuple[*P]]], Block[TResult]]:
    """Starmap source sequence.

    Unpack arguments grouped as tuple elements. Builds a new collection
    whose elements are the results of applying the given function to the
    unpacked arguments to each of the elements of the collection.

    Args:
        mapper: A function to transform items from the input sequence.

    Returns:
        Partially applied map function.
    """

    def mapper_(args: tuple[*P]) -> TResult:
        return mapper(*args)

    return map(mapper_)


def map2[TResult, T1, T2](
    mapper: Callable[[T1, T2], TResult],
) -> Callable[[Block[tuple[T1, T2]]], Block[TResult]]:
    return starmap(mapper)


def map3[TResult, T1, T2, T3](
    mapper: Callable[[T1, T2, T3], TResult],
) -> Callable[[Block[tuple[T1, T2, T3]]], Block[TResult]]:
    return starmap(mapper)


@curry_flip(1)
def mapi[TSource, TResult](source: Block[TSource], mapper: Callable[[int, TSource], TResult]) -> Block[TResult]:
    """Map list with index.

    Builds a new collection whose elements are the results of
    applying the given function to each of the elements of the
    collection. The integer index passed to the function indicates
    the index (from 0) of element being transformed.

    Args:
        source: The source block to map
        mapper: The function to transform elements and their
            indices.

    Returns:
        The list of transformed elements.
    """
    return source.mapi(mapper)


def of[TSource](*args: TSource) -> Block[TSource]:
    """Create list from a number of arguments."""
    return Block((*args,))


def of_seq[TSource](xs: Iterable[TSource]) -> Block[TSource]:
    """Create list from iterable sequence."""
    return Block((*xs,))


def of_option[TSource](option: Option[TSource]) -> Block[TSource]:
    match option:
        case Some(value):
            return singleton(value)
        case _:
            return empty


@curry_flip(1)
def partition[TSource](
    source: Block[TSource], predicate: Callable[[TSource], bool]
) -> tuple[Block[TSource], Block[TSource]]:
    """Partition block.

    Splits the collection into two collections, containing the
    elements for which the given predicate returns True and False
    respectively. Element order is preserved in both of the created
    lists.

    Args:
        source: The source block to partition (curried flipped)
        predicate: The function to test the input elements.

    Returns:
        A list containing the elements for which the predicate
        evaluated to true and a list containing the elements for
        which the predicate evaluated to false.
    """
    return source.partition(predicate)


@overload
def range(stop: int) -> Block[int]: ...


@overload
def range(start: int, stop: int) -> Block[int]: ...


@overload
def range(start: int, stop: int, step: int) -> Block[int]: ...


def range(*args: int, **kw: int) -> Block[int]:
    return Block((*builtins.range(*args, **kw),))


def singleton[TSource](value: TSource) -> Block[TSource]:
    return Block((value,))


@curry_flip(1)
def skip[TSource](source: Block[TSource], count: int) -> Block[TSource]:
    """Returns the list after removing the first N elements.

    Args:
        source: Source block to skip elements from.
        count: The number of elements to skip.

    Returns:
        The list after removing the first N elements.
    """
    return source.skip(count)


@curry_flip(1)
def skip_last[TSource](source: Block[TSource], count: int) -> Block[TSource]:
    """Returns the list after removing the last N elements.

    Args:
        source: The source block to skip from.
        count: The number of elements to skip.

    Returns:
        The list after removing the last N elements.
    """
    return source.skip_last(count)


@curry_flip(1)
def sort[TSourceSortable: SupportsLessThan](
    source: Block[TSourceSortable],
    reverse: bool = False,
) -> Block[TSourceSortable]:
    """Returns a new sorted collection.

    Args:
        source: The source block to sort.
        reverse: Sort in reversed order.

    Returns:
        Partially applied sort function.
    """
    return source.sort(reverse)


@curry_flip(1)
def sort_with[TSource](source: Block[TSource], func: Callable[[TSource], Any], reverse: bool = False) -> Block[TSource]:
    """Returns a new collection sorted using "func" key function.

    Args:
        source: The source block to sort.
        func: The function to extract a comparison key from each element in list.
        reverse: Sort in reversed order.

    Returns:
        Partially applied sort function.
    """
    return source.sort_with(func, reverse)


def sum[TSourceSum: SupportsSum](source: Block[TSourceSum | Literal[0]]) -> TSourceSum | Literal[0]:
    return builtins.sum(source)


@curry_flip(1)
def sum_by[TSourceSum: SupportsSum, TResult](
    source: Block[TSourceSum], projection: Callable[[TSourceSum], TResult]
) -> TResult:
    xs = source.map(projection)
    return builtins.sum(xs)  # type: ignore


def tail[TSource](source: Block[TSource]) -> Block[TSource]:
    return source.tail()


@curry_flip(1)
def take[TSource](source: Block[TSource], count: int) -> Block[TSource]:
    """Returns the first N elements of the list.

    Args:
        source: The input blcok to take elements from.
        count: The number of items to take.

    Returns:
        The result list.
    """
    return source.take(count)


@curry_flip(1)
def take_last[TSource](source: Block[TSource], count: int) -> Block[TSource]:
    """Take last elements from block.

    Returns a specified number of contiguous elements from the end of
    the list.

    Args:
        source: The input block to take elements from.
        count: The number of items to take.

    Returns:
        The result list.
    """
    return source.take_last(count)


def dict[TSource](source: Block[TSource]) -> list[TSource]:
    return source.dict()


def try_head[TSource](source: Block[TSource]) -> Option[TSource]:
    """Try to get the first element from the list.

    Returns the first element of the list, or None if the list is empty.

    Args:
        source: The input list.

    Returns:
        The first element of the list or `Nothing()`.
    """
    return source.try_head()


@curry_flip(1)
def unfold[TState, TSource](
    state: TState, generator: Callable[[TState], Option[tuple[TSource, TState]]]
) -> Block[TSource]:
    """Unfold block.

    Returns a list that contains the elements generated by the
    given computation. The given initial state argument is passed to
    the element generator.

    Args:
        generator: A function that takes in the current state and
            returns an option tuple of the next element of the list
            and the next state value.
        state: The initial state.

    Returns:
        The result list.
    """
    xs = pipe(state, seq.unfold(generator))
    return Block(xs)


@curry_flip(1)
def zip[TSource, TResult](
    source: Block[TSource],
    other: Block[TResult],
) -> Block[tuple[TSource, TResult]]:
    """Zip block with other.

    Combines the two lists into a list of pairs. The two lists
    must have equal lengths.

    Args:
        source: The input block to zip with other.
        other: The second input list.

    Returns:
        Paritally applied zip function that takes the source list and
        returns s single list containing pairs of matching elements from
        the input lists.
    """
    return source.zip(other)


__all__ = [
    "Block",
    "append",
    "choose",
    "collect",
    "concat",
    "dict",
    "empty",
    "filter",
    "fold",
    "head",
    "indexed",
    "is_empty",
    "item",
    "map",
    "mapi",
    "of_option",
    "of_seq",
    "partition",
    "singleton",
    "skip",
    "skip_last",
    "sort",
    "sort_with",
    "tail",
    "take",
    "take_last",
    "try_head",
    "unfold",
    "zip",
]
