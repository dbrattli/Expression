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
from typing import TYPE_CHECKING, Any, Literal, TypeVar, get_args, overload

from typing_extensions import TypeVarTuple, Unpack


if TYPE_CHECKING:
    from pydantic import GetCoreSchemaHandler
    from pydantic_core import CoreSchema

from expression.core import (
    Nothing,
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
_TSourceSortable = TypeVar("_TSourceSortable", bound=SupportsLessThan)
_TSourceSum = TypeVar("_TSourceSum", bound=SupportsSum)
_TResult = TypeVar("_TResult")
_TState = TypeVar("_TState")

_T1 = TypeVar("_T1")
_T2 = TypeVar("_T2")
_T3 = TypeVar("_T3")
_T4 = TypeVar("_T4")
_P = TypeVarTuple("_P")


class Block(
    Collection[_TSource],  # Sequence breaks pydantic
    PipeMixin,
):
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

    def __init__(self, value: Iterable[_TSource] = ()) -> None:
        # Use composition instead of inheritance since generic tuples
        # are not suppored by mypy.
        self._value: tuple[_TSource, ...] = tuple(value) if value else tuple()

    def append(self, other: Block[_TSource]) -> Block[_TSource]:
        """Append other block to end of the block."""
        return Block(self._value + other._value)

    def choose(self, chooser: Callable[[_TSource], Option[_TResult]]) -> Block[_TResult]:
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

        def mapper(x: _TSource) -> Block[_TResult]:
            return Block(chooser(x).to_seq())

        return self.collect(mapper)

    def collect(self, mapping: Callable[[_TSource], Block[_TResult]]) -> Block[_TResult]:
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

    def fold(self, folder: Callable[[_TState, _TSource], _TState], state: _TState) -> _TState:
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

    def map(self, mapping: Callable[[_TSource], _TResult]) -> Block[_TResult]:
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

    def starmap(self: Block[tuple[Unpack[_P]]], mapping: Callable[[Unpack[_P]], _TResult]) -> Block[_TResult]:
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

    def sum(self: Block[_TSourceSum | Literal[0]]) -> _TSourceSum | Literal[0]:
        return builtins.sum(self._value)

    def sum_by(self: Block[_TSourceSum], projection: Callable[[_TSourceSum], _TResult]) -> _TResult:
        return pipe(self, sum_by(projection))

    def mapi(self, mapping: Callable[[int, _TSource], _TResult]) -> Block[_TResult]:
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
    def of(*args: _TSource) -> Block[_TSource]:
        """Create list from a number of arguments."""
        return Block((*args,))

    @staticmethod
    def of_seq(xs: Iterable[_TResult]) -> Block[_TResult]:
        """Create list from iterable sequence."""
        return Block((*xs,))

    @staticmethod
    def of_option(option: Option[_TSource]) -> Block[_TSource]:
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
    def singleton(item: _TSource) -> Block[_TSource]:
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
        return Block(self._value[:-count])

    def tail(self) -> Block[_TSource]:
        """Return tail of List."""
        _, *tail = self._value
        return Block(tail)

    def sort(self: Block[_TSourceSortable], reverse: bool = False) -> Block[_TSourceSortable]:
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
        return Block(self._value[-count:])

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

        return Nothing

    @staticmethod
    def unfold(generator: Callable[[_TState], Option[tuple[_TSource, _TState]]], state: _TState) -> Block[_TSource]:
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

    def zip(self, other: Block[_TResult]) -> Block[tuple[_TSource, _TResult]]:
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

    def __getitem__(self, key: Any) -> Any:
        ret: Any = self._value[key]
        return ret

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
def append(source: Block[_TSource], other: Block[_TSource]) -> Block[_TSource]:
    return source.append(other)


@curry_flip(1)
def choose(source: Block[_TSource], chooser: Callable[[_TSource], Option[_TResult]]) -> Block[_TResult]:
    return source.choose(chooser)


@curry_flip(1)
def collect(source: Block[_TSource], mapping: Callable[[_TSource], Block[_TResult]]) -> Block[_TResult]:
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


def concat(sources: Iterable[Block[_TSource]]) -> Block[_TSource]:
    """Concatenate sequence of Block's."""

    def reducer(t: Block[_TSource], s: Block[_TSource]) -> Block[_TSource]:
        return t.append(s)

    return pipe(sources, seq.fold(reducer, empty))


def cons(head: _TSource, tail: Block[_TSource]) -> Block[_TSource]:
    return Block((head, *tail))


nil: Block[Any] = Block()
empty: Block[Any] = nil
"""The empty list."""


@curry_flip(1)
def filter(source: Block[_TSource], predicate: Callable[[_TSource], bool]) -> Block[_TSource]:
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
def fold(
    source: Block[_TSource],
    folder: Callable[[_TState, _TSource], _TState],
    state: _TState,
) -> _TState:
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
def forall(source: Block[_TSource], predicate: Callable[[_TSource], bool]) -> bool:
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


def head(source: Block[_TSource]) -> _TSource:
    """Returns the first element of the list.

    Args:
        source: The input list.

    Returns:
        The first element of the list.

    Raises:
         ValueError: Thrown when the list is empty.
    """
    return source.head()


def indexed(source: Block[_TSource]) -> Block[tuple[int, _TSource]]:
    """Index elements in block.

    Returns a new list whose elements are the corresponding
    elements of the input list paired with the index (from 0)
    of each element.

    Returns:
        The list of indexed elements.
    """
    return source.indexed()


@curry_flip(1)
def item(source: Block[_TSource], index: int) -> _TSource:
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
def map(source: Block[_TSource], mapper: Callable[[_TSource], _TResult]) -> Block[_TResult]:
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
def reduce(
    source: Block[_TSource],
    reduction: Callable[[_TSource, _TSource], _TSource],
) -> _TSource:
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


def starmap(mapper: Callable[[Unpack[_P]], _TResult]) -> Callable[[Block[tuple[Unpack[_P]]]], Block[_TResult]]:
    """Starmap source sequence.

    Unpack arguments grouped as tuple elements. Builds a new collection
    whose elements are the results of applying the given function to the
    unpacked arguments to each of the elements of the collection.

    Args:
        mapper: A function to transform items from the input sequence.

    Returns:
        Partially applied map function.
    """

    def mapper_(args: tuple[Unpack[_P]]) -> _TResult:
        return mapper(*args)

    return map(mapper_)


def map2(mapper: Callable[[_T1, _T2], _TResult]) -> Callable[[Block[tuple[_T1, _T2]]], Block[_TResult]]:
    return starmap(mapper)


def map3(mapper: Callable[[_T1, _T2, _T3], _TResult]) -> Callable[[Block[tuple[_T1, _T2, _T3]]], Block[_TResult]]:
    return starmap(mapper)


@curry_flip(1)
def mapi(source: Block[_TSource], mapper: Callable[[int, _TSource], _TResult]) -> Block[_TResult]:
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


def of(*args: _TSource) -> Block[_TSource]:
    """Create list from a number of arguments."""
    return Block((*args,))


def of_seq(xs: Iterable[_TSource]) -> Block[_TSource]:
    """Create list from iterable sequence."""
    return Block((*xs,))


def of_option(option: Option[_TSource]) -> Block[_TSource]:
    match option:
        case Option(tag="some", some=value):
            return singleton(value)
        case _:
            return empty


@curry_flip(1)
def partition(
    source: Block[_TSource], predicate: Callable[[_TSource], bool]
) -> tuple[Block[_TSource], Block[_TSource]]:
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


def singleton(value: _TSource) -> Block[_TSource]:
    return Block((value,))


@curry_flip(1)
def skip(source: Block[_TSource], count: int) -> Block[_TSource]:
    """Returns the list after removing the first N elements.

    Args:
        source: Source block to skip elements from.
        count: The number of elements to skip.

    Returns:
        The list after removing the first N elements.
    """
    return source.skip(count)


@curry_flip(1)
def skip_last(source: Block[_TSource], count: int) -> Block[_TSource]:
    """Returns the list after removing the last N elements.

    Args:
        source: The source block to skip from.
        count: The number of elements to skip.

    Returns:
        The list after removing the last N elements.
    """
    return source.skip_last(count)


@curry_flip(1)
def sort(
    source: Block[_TSourceSortable],
    reverse: bool = False,
) -> Block[_TSourceSortable]:
    """Returns a new sorted collection.

    Args:
        source: The source block to sort.
        reverse: Sort in reversed order.

    Returns:
        Partially applied sort function.
    """
    return source.sort(reverse)


@curry_flip(1)
def sort_with(source: Block[_TSource], func: Callable[[_TSource], Any], reverse: bool = False) -> Block[_TSource]:
    """Returns a new collection sorted using "func" key function.

    Args:
        source: The source block to sort.
        func: The function to extract a comparison key from each element in list.
        reverse: Sort in reversed order.

    Returns:
        Partially applied sort function.
    """
    return source.sort_with(func, reverse)


def sum(source: Block[_TSourceSum | Literal[0]]) -> _TSourceSum | Literal[0]:
    return builtins.sum(source)


@curry_flip(1)
def sum_by(source: Block[_TSourceSum], projection: Callable[[_TSourceSum], _TResult]) -> _TResult:
    xs = source.map(projection)
    return builtins.sum(xs)  # type: ignore


def tail(source: Block[_TSource]) -> Block[_TSource]:
    return source.tail()


@curry_flip(1)
def take(source: Block[_TSource], count: int) -> Block[_TSource]:
    """Returns the first N elements of the list.

    Args:
        source: The input blcok to take elements from.
        count: The number of items to take.

    Returns:
        The result list.
    """
    return source.take(count)


@curry_flip(1)
def take_last(source: Block[_TSource], count: int) -> Block[_TSource]:
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


def dict(source: Block[_TSource]) -> list[_TSource]:
    return source.dict()


def try_head(source: Block[_TSource]) -> Option[_TSource]:
    """Try to get the first element from the list.

    Returns the first element of the list, or None if the list is empty.

    Args:
        source: The input list.

    Returns:
        The first element of the list or `Nothing`.
    """
    return source.try_head()


@curry_flip(1)
def unfold(state: _TState, generator: Callable[[_TState], Option[tuple[_TSource, _TState]]]) -> Block[_TSource]:
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
def zip(
    source: Block[_TSource],
    other: Block[_TResult],
) -> Block[tuple[_TSource, _TResult]]:
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
