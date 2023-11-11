"""A frozen immutable list module.

This module provides an immutable list type `NonEmptyBlock` and  a set of
useful methods and functions for working with the list. `NonEmptyBlock`s
are always guarenteed to have at least one element.

A NonEmptyBlock is backed by a Block.

Example:
    >>> xs = NonEmptyBlock.of(1, 2, 3)
    >>> ys_opt = NonEmptyBlock.of_seq(())
    >>> zs = NonEmptyBlock.of_init_last([], 4)
"""
from __future__ import annotations

import builtins
import functools
import itertools
from collections.abc import Callable, Collection, Iterable, Iterator
from typing import Any, ClassVar, Literal, TypeVar, cast, overload

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
from expression.core.typing import GenericValidator, ModelField, SupportsValidation

from . import seq, Block

_TSource = TypeVar("_TSource")
_TSourceSortable = TypeVar("_TSourceSortable", bound=SupportsLessThan)
_TSourceSum = TypeVar("_TSourceSum", bound=SupportsSum)
_TResult = TypeVar("_TResult")
_TState = TypeVar("_TState")

_T1 = TypeVar("_T1")
_T2 = TypeVar("_T2")
_T3 = TypeVar("_T3")
_T4 = TypeVar("_T4")


def _validate(value: Any, field: ModelField) -> NonEmptyBlock[Any]:
    if isinstance(value, NonEmptyBlock):
        return cast(NonEmptyBlock[Any], value)

    if not isinstance(value, list):
        raise ValueError("not a list")

    value_ = cast(list[Any], value)

    if field.sub_fields:
        sub_field = field.sub_fields[0]

        value__: list[Any] = []
        for item in value_:
            val, error = sub_field.validate(item, {}, loc="NonEmptyBlock")
            if error:
                raise ValueError(str(error))
            value__.append(val)
        value_ = value__

    return NonEmptyBlock(value_)


class NonEmptyBlock(
    Collection[_TSource],  # Sequence breaks pydantic
    PipeMixin,
    SupportsValidation["NonEmptyBlock[_TSource]"],
):
    """ Immutable list type guaranteed to have at least one element. """

    __match_args__ = ("_head", "_tail")

    __validators__: ClassVar = [_validate]

    def __init__(self, head: _TSource, tail: Iterable[_TSource] = ()) -> None:
        self._head = head
        self._tail = Block(tail)
        self._value = Block(itertools.chain([head], self._tail))

    def append(self, other: Iterable[_TSource]) -> NonEmptyBlock[_TSource]:
        """Append other block to end of the block."""
        return NonEmptyBlock(self._head, iter(itertools.chain(self._tail, other)))

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
        return self._value.choose(chooser)

    def collect(self, mapping: Callable[[_TSource], NonEmptyBlock[_TResult]]) -> NonEmptyBlock[_TResult]:
        mapped_head = mapping(self._head)
        mapped_tail = builtins.map(mapping, self._tail)
        xs = (y for x in mapped_tail for y in x)
        return NonEmptyBlock(mapped_head.head(), itertools.chain(mapped_head.tail(), xs))

    def cons(self, element: _TSource) -> NonEmptyBlock[_TSource]:
        """Add element to front of list."""
        return NonEmptyBlock(element, self)

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
        return self._value.filter(predicate)

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

        The is always guaranteed to return a value as the list
        cannot be empty.

        Returns:
            The first element of the list.
        """
        return self._head

    def indexed(self, start: int = 0) -> NonEmptyBlock[tuple[int, _TSource]]:
        """Index elements in block.

        Returns a new list whose elements are the corresponding
        elements of the input list paired with the index of each
        element.

        Args:
            start: Optional index to start from. Defaults to 0.

        Returns:
            The list of indexed elements.
        """
        return NonEmptyBlock((start, self._head), enumerate(self._tail, start=1+start))

    def item(self, index: int) -> Option[_TSource]:
        """Indexes into the list. The first element has index 0.

        Args:
            index: The index to retrieve.

        Returns:
            If the index exists, the value at the given index wrapped
            in a `Some`. Otherwise, `Nothing`
        """
        try:
            return Some(self[index])
        except IndexError:
            return Nothing

    def map(self, mapping: Callable[[_TSource], _TResult]) -> NonEmptyBlock[_TResult]:
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
        return NonEmptyBlock(mapping(self._head), self._tail.map(mapping))

    @overload
    def starmap(self: NonEmptyBlock[tuple[_T1, _T2]], mapping: Callable[[_T1, _T2], _TResult]) -> NonEmptyBlock[_TResult]:
        ...

    @overload
    def starmap(
        self: NonEmptyBlock[tuple[_T1, _T2, _T3]],
        mapping: Callable[[_T1, _T2, _T3], _TResult],
    ) -> NonEmptyBlock[_TResult]:
        ...

    @overload
    def starmap(
        self: NonEmptyBlock[tuple[_T1, _T2, _T3, _T4]],
        mapping: Callable[[_T1, _T2, _T3, _T4], _TResult],
    ) -> NonEmptyBlock[_TResult]:
        ...

    def starmap(self: NonEmptyBlock[Any], mapping: Callable[..., Any]) -> NonEmptyBlock[Any]:
        """Starmap source sequence.

        Unpack arguments grouped as tuple elements. Builds a new collection
        whose elements are the results of applying the given function to the
        unpacked arguments to each of the elements of the collection.

        Args:
            mapping: A function to transform items from the input sequence.

        Returns:
            Partially applied map function.
        """
        return starmap(mapping)(self)

    def sum(self: NonEmptyBlock[_TSourceSum | Literal[0]]) -> _TSourceSum | Literal[0]:
        return self._value.sum()

    def sum_by(self: NonEmptyBlock[_TSourceSum], projection: Callable[[_TSourceSum], _TResult]) -> _TResult:
        return pipe(self, sum_by(projection))

    def mapi(self, mapping: Callable[[int, _TSource], _TResult]) -> NonEmptyBlock[_TResult]:
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
        return self.indexed().starmap(mapping)

    @staticmethod
    def of(head: _TSource, *args: _TSource) -> NonEmptyBlock[_TSource]:
        """Create list from a number of arguments."""
        return NonEmptyBlock(head, args)

    @staticmethod
    def of_seq(xs: Iterable[_TSource]) -> Option[NonEmptyBlock[_TSource]]:
        """Create list from iterable sequence."""
        xs_gen = (x for x in xs)
        try:
            head = next(xs_gen)
        except StopIteration:
            return Nothing
        else:
            return Some(NonEmptyBlock(head, xs_gen))

    @staticmethod
    def of_init_last(xs: Iterable[_TSource], last: _TSource) -> NonEmptyBlock[_TSource]:
        xs_gen = itertools.chain((x for x in xs), [last])
        head = next(xs_gen)
        return NonEmptyBlock(head, xs_gen)

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
    def range(stop: int) -> Option[NonEmptyBlock[int]]:
        ...

    @overload
    @staticmethod
    def range(start: int, stop: int) -> Option[NonEmptyBlock[int]]:
        ...

    @overload
    @staticmethod
    def range(start: int, stop: int, step: int) -> Option[NonEmptyBlock[int]]:
        ...

    @staticmethod
    def range(*args: int, **kw: int) -> Option[NonEmptyBlock[int]]:
        range_ = builtins.range(*args, **kw)
        if len(range_):
            return Some(NonEmptyBlock(range_.start, range_[1:]))
        else:
            return Nothing

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
        return functools.reduce(reduction, self._tail, self._head)

    @staticmethod
    def singleton(item: _TSource) -> NonEmptyBlock[_TSource]:
        return singleton(item)

    def skip(self, count: int) -> Option[NonEmptyBlock[_TSource]]:
        """Returns the list after removing the first N elements.

        Args:
            count: The number of elements to skip.

        Returns:
            The list after removing the first N elements.
        """
        if len(self._value) > count:
            return Some(NonEmptyBlock(self._value[count], self._value[count+1:]))
        else:
            return Nothing

    def skip_last(self, count: int) -> Option[NonEmptyBlock[_TSource]]:
        if len(self._value) > count:
            return Some(NonEmptyBlock(self.head(), self._tail[:-count]))
        else:
            return Nothing

    def tail(self) -> Block[_TSource]:
        """Return tail of List."""
        return self._tail

    def sort(self: NonEmptyBlock[_TSourceSortable], reverse: bool = False) -> NonEmptyBlock[_TSourceSortable]:
        """Sort list directly.

        Returns a new sorted collection.

        Args:
            reverse: Sort in reversed order.

        Returns:
            A sorted list.
        """
        sorted_value = builtins.sorted(self._value, reverse=reverse)
        return NonEmptyBlock(sorted_value[0], sorted_value[1:])

    def sort_with(self, func: Callable[[_TSource], Any], reverse: bool = False) -> NonEmptyBlock[_TSource]:
        """Sort list with supplied function.

        Returns a new sorted collection.

        Args:
            func: The function to extract a comparison key from each element in list.
            reverse: Sort in reversed order.

        Returns:
            A sorted list.
        """
        sorted_value = builtins.sorted(self._value, key=func, reverse=reverse)
        return NonEmptyBlock(sorted_value[0], sorted_value[1:])

    def take(self, count: int) -> NonEmptyBlock[_TSource]:
        """Returns the first N elements of the list.

        Args:
            count: The number of items to take.

        Returns:
            The result list.
        """
        return NonEmptyBlock(self.head(), self._tail[:count-1])

    def take_last(self, count: int) -> NonEmptyBlock[_TSource]:
        """Take last elements from block.

        Returns a specified number of contiguous elements from the
        end of the list.

        Args:
            count: The number of items to take.

        Returns:
            The result list.
        """
        last_elements = self._value[-count:]
        return NonEmptyBlock(last_elements[0], last_elements[1:])

    def dict(self) -> list[_TSource]:
        """Returns a json serializable representation of the list."""
        return self._value.dict()

    def zip(self, other: NonEmptyBlock[_TResult]) -> NonEmptyBlock[tuple[_TSource, _TResult]]:
        """Zip block.

        Combines the two lists into a list of pairs. The two lists
        must have equal lengths.

        Args:
            other: The second input list.

        Returns:
            A single list containing pairs of matching elements from the
            input lists.
        """
        return NonEmptyBlock[_TSource, _TResult]((self.head(), other.head()), self._tail.zip(other._tail))

    def __add__(self, other: NonEmptyBlock[_TSource]) -> NonEmptyBlock[_TSource]:
        return self.append(other)

    def __contains__(self, value: Any) -> bool:
        return self._value.__contains__(value)

    @overload
    def __getitem__(self, key: slice) -> NonEmptyBlock[_TSource]:
        ...

    @overload
    def __getitem__(self, key: int) -> _TSource:
        ...

    def __getitem__(self, key: Any) -> Any:
        ret: Any = list(itertools.chain([self._head], self._tail))[key]
        return ret

    def __iter__(self) -> Iterator[_TSource]:
        return iter(self._value)

    def __eq__(self, o: Any) -> bool:
        return self._value == o

    def __len__(self) -> int:
        return 1 + len(self._tail)

    def __str__(self) -> str:
        return f"[{', '.join(itertools.chain([str(self._head)], self._tail.map(str)))}]"

    def __repr__(self) -> str:
        return str(self)

    @classmethod
    def __get_validators__(cls) -> Iterator[GenericValidator[NonEmptyBlock[_TSource]]]:
        yield from cls.__validators__


@curry_flip(1)
def append(source: NonEmptyBlock[_TSource], other: NonEmptyBlock[_TSource]) -> NonEmptyBlock[_TSource]:
    return source.append(other)


@curry_flip(1)
def choose(source: NonEmptyBlock[_TSource], chooser: Callable[[_TSource], Option[_TResult]]) -> Block[_TResult]:
    return source.choose(chooser)


@curry_flip(1)
def collect(source: NonEmptyBlock[_TSource], mapping: Callable[[_TSource], NonEmptyBlock[_TResult]]) -> NonEmptyBlock[_TResult]:
    """Collect block.

    For each element of the list, applies the given function.
    Concatenates all the results and return the combined list.

    Args:
        source: The input list (curried flipped).
        mapping: The function to transform each input element into
        a sublist to be concatenated.

    Returns:
        A partially applied collect function that takes the source
        list and returns the concatenation of the transformed sublists.
    """
    return source.collect(mapping)


def concat(sources: NonEmptyBlock[NonEmptyBlock[_TSource]]) -> NonEmptyBlock[_TSource]:
    """Concatenate NonEmptyBlock of NonEmptyBlock's."""

    def reducer(t: NonEmptyBlock[_TSource], s: NonEmptyBlock[_TSource]) -> NonEmptyBlock[_TSource]:
        return t.append(s)

    return sources.reduce(reducer)


def cons(head: _TSource, tail: NonEmptyBlock[_TSource]) -> NonEmptyBlock[_TSource]:
    return NonEmptyBlock(head, tail)


@curry_flip(1)
def filter(source: NonEmptyBlock[_TSource], predicate: Callable[[_TSource], bool]) -> Block[_TSource]:
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
    source: NonEmptyBlock[_TSource],
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
def forall(source: NonEmptyBlock[_TSource], predicate: Callable[[_TSource], bool]) -> bool:
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


def head(source: NonEmptyBlock[_TSource]) -> _TSource:
    """Returns the first element of the list.

    The is always guaranteed to return a value as the list
    cannot be empty.

    Args:
        source: The input list.

    Returns:
        The first element of the list.
    """
    return source.head()


def indexed(source: NonEmptyBlock[_TSource]) -> NonEmptyBlock[tuple[int, _TSource]]:
    """Index elements in block.

    Returns a new list whose elements are the corresponding
    elements of the input list paired with the index (from 0)
    of each element.

    Returns:
        The list of indexed elements.
    """
    return source.indexed()


@curry_flip(1)
def item(source: NonEmptyBlock[_TSource], index: int) -> _TSource:
    """Indexes into the list. The first element has index 0.

    Args:
        source: The input block list.
        index: The index to retrieve.

    Returns:
        The value at the given index.
    """
    return source.item(index)


@curry_flip(1)
def map(source: NonEmptyBlock[_TSource], mapper: Callable[[_TSource], _TResult]) -> NonEmptyBlock[_TResult]:
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
    source: NonEmptyBlock[_TSource],
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
        Partially applied reduction function that takes the source block
        and returns the final state value.
    """
    return source.reduce(reduction)


@overload
def starmap(mapper: Callable[[_T1, _T2], _TResult]) -> Callable[[NonEmptyBlock[tuple[_T1, _T2]]], NonEmptyBlock[_TResult]]:
    ...


@overload
def starmap(mapper: Callable[[_T1, _T2, _T3], _TResult]) -> Callable[[NonEmptyBlock[tuple[_T1, _T2, _T3]]], NonEmptyBlock[_TResult]]:
    ...


@overload
def starmap(
    mapper: Callable[[_T1, _T2, _T3, _T4], _TResult]
) -> Callable[[NonEmptyBlock[tuple[_T1, _T2, _T3, _T4]]], NonEmptyBlock[_TResult]]:
    ...


def starmap(mapper: Callable[..., Any]) -> Callable[[NonEmptyBlock[Any]], NonEmptyBlock[Any]]:
    """Starmap source sequence.

    Unpack arguments grouped as tuple elements. Builds a new collection
    whose elements are the results of applying the given function to the
    unpacked arguments to each of the elements of the collection.

    Args:
        mapper: A function to transform items from the input sequence.

    Returns:
        Partially applied map function.
    """

    def mapper_(args: tuple[Any, ...]) -> Any:
        return mapper(*args)

    return map(mapper_)


def map2(mapper: Callable[[_T1, _T2], _TResult]) -> Callable[[NonEmptyBlock[tuple[_T1, _T2]]], NonEmptyBlock[_TResult]]:
    return starmap(mapper)


def map3(mapper: Callable[[_T1, _T2, _T3], _TResult]) -> Callable[[NonEmptyBlock[tuple[_T1, _T2, _T3]]], NonEmptyBlock[_TResult]]:
    return starmap(mapper)


@curry_flip(1)
def mapi(source: NonEmptyBlock[_TSource], mapper: Callable[[int, _TSource], _TResult]) -> NonEmptyBlock[_TResult]:
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


def of(*args: _TSource) -> NonEmptyBlock[_TSource]:
    """Create list from a number of arguments."""
    return NonEmptyBlock.of(*args)


def of_seq(xs: Iterable[_TSource]) -> Option[NonEmptyBlock[_TSource]]:
    """Create list from iterable sequence."""
    return NonEmptyBlock.of_seq(xs)


@curry_flip(1)
def partition(
    source: NonEmptyBlock[_TSource], predicate: Callable[[_TSource], bool]
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
def range(stop: int) -> Option[NonEmptyBlock[int]]:
    ...


@overload
def range(start: int, stop: int) -> Option[NonEmptyBlock[int]]:
    ...


@overload
def range(start: int, stop: int, step: int) -> Option[NonEmptyBlock[int]]:
    ...


def range(*args: int, **kw: int) -> Option[NonEmptyBlock[int]]:
    return NonEmptyBlock.range(*args, **kw)


def singleton(value: _TSource) -> NonEmptyBlock[_TSource]:
    return NonEmptyBlock(value)


@curry_flip(1)
def skip(source: NonEmptyBlock[_TSource], count: int) -> Option[NonEmptyBlock[_TSource]]:
    """Returns the list after removing the first N elements.

    Args:
        source: Source block to skip elements from.
        count: The number of elements to skip.

    Returns:
        The list after removing the first N elements.
    """
    return source.skip(count)


@curry_flip(1)
def skip_last(source: NonEmptyBlock[_TSource], count: int) -> Option[NonEmptyBlock[_TSource]]:
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
    source: NonEmptyBlock[_TSourceSortable],
    reverse: bool = False,
) -> NonEmptyBlock[_TSourceSortable]:
    """Returns a new sorted collection.

    Args:
        source: The source block to sort.
        reverse: Sort in reversed order.

    Returns:
        Partially applied sort function.
    """
    return source.sort(reverse)


@curry_flip(1)
def sort_with(source: NonEmptyBlock[_TSource], func: Callable[[_TSource], Any], reverse: bool = False) -> NonEmptyBlock[_TSource]:
    """Returns a new collection sorted using "func" key function.

    Args:
        source: The source block to sort.
        func: The function to extract a comparison key from each element in list.
        reverse: Sort in reversed order.

    Returns:
        Partially applied sort function.
    """
    return source.sort_with(func, reverse)


def sum(source: NonEmptyBlock[_TSourceSum | Literal[0]]) -> _TSourceSum | Literal[0]:
    return builtins.sum(source)


@curry_flip(1)
def sum_by(source: NonEmptyBlock[_TSourceSum], projection: Callable[[_TSourceSum], _TResult]) -> _TResult:
    xs = source.map(projection)
    return builtins.sum(xs)  # type: ignore


def tail(source: NonEmptyBlock[_TSource]) -> Block[_TSource]:
    return source.tail()


@curry_flip(1)
def take(source: NonEmptyBlock[_TSource], count: int) -> NonEmptyBlock[_TSource]:
    """Returns the first N elements of the list.

    Args:
        source: The input blcok to take elements from.
        count: The number of items to take.

    Returns:
        The result list.
    """
    return source.take(count)


@curry_flip(1)
def take_last(source: NonEmptyBlock[_TSource], count: int) -> NonEmptyBlock[_TSource]:
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


def dict(source: NonEmptyBlock[_TSource]) -> list[_TSource]:
    return source.dict()


@curry_flip(1)
def unfold(state: _TState, generator: Callable[[_TState], Option[tuple[_TSource, _TState]]]) -> NonEmptyBlock[_TSource]:
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
    return NonEmptyBlock(xs)


@curry_flip(1)
def zip(
    source: NonEmptyBlock[_TSource],
    other: NonEmptyBlock[_TResult],
) -> NonEmptyBlock[tuple[_TSource, _TResult]]:
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
    "NonEmptyBlock",
    "append",
    "choose",
    "collect",
    "concat",
    "dict",
    "filter",
    "fold",
    "head",
    "indexed",
    "item",
    "map",
    "mapi",
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
    "unfold",
    "zip",
]
