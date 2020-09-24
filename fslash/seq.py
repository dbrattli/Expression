from typing import Generic, TypeVar, Callable, Iterable, Iterator, Generator, List, Union
import types

TSource = TypeVar("TSource")
TResult = TypeVar("TResult")


class SeqModule(Generic[TSource]):
    """Sequence module.

    Contains a collection of static methods (functions) for operating on
    sequences. All functions takes the source as the last curried
    argument, i.e all functions returns a function that takes the source
    sequence as the only argument.

    Example:
        >>> xs = Seq([1, 2, 3])
        >>> ys = pipe(
            xs,
            Seq.map(lambda x: x + 1),
            Seq.filter(lambda x: x < 3)
        )
    """

    @staticmethod
    def filter(predicate: Callable[[TSource], bool]) -> Callable[[Iterable[TSource]], Iterable[TSource]]:
        """Filter sequence.

        Filters the sequence to a new sequence containing only the
        elements of the sequence for which the given predicate returns
        `True`.

        Args:
            predicate: A function to test whether each item in the
                input sequence should be included in the output.
            source: (curried) The input sequence to to filter.

        Returns:
            A partially applied filter function.
        """
        def _filter(source: Iterable[TSource]) -> Iterable[TSource]:
            """Filter sequence (partially applied).

            Args:
                source: The input sequence to to filter.

            Returns:
                Returns a new collection containing only the elements
                of the collection for which the given predicate returns
                `True`.
            """
            return filter(predicate, source)
        return _filter

    @staticmethod
    def head() -> Callable[[Iterable[TSource]], TSource]:
        """Return the first element of the sequence.

        Returns:
            A partially applied head function.

        Raises:
            Raises `ValueError` if the source sequence is empty.
        """

        def _head(source: Iterable[TSource]) -> TSource:
            """A function that takes the source as input.

            Args:
                source: The input sequence.

            Returns:
                The first element of the sequence.

            Raises:
                `ValueError` if the source sequence is empty.
            """
            for value in source:
                return value
            else:
                raise ValueError("Sequence contains no elements")

        return _head

    @staticmethod
    def iter(action: Callable[[TSource], None]) -> Callable[[Iterable[TSource]], None]:
        """Applies the given function to each element of the collection.

        Args:
            action: A function to apply to each element of the sequence.

        Returns:
            A partially applied iter function.
        """

        def _iter(source: Iterable[TSource]) -> None:
            """A partially applied iter function.

            Note that this function is a pure side effect and returns nothing.

            Args:
                source: The input sequence to apply action to.

            Returns:
                None
            """
            for x in source:
                action(x)
        return _iter

    @staticmethod
    def map(mapper: Callable[[TSource], TResult]) -> Callable[[Iterable[TSource]], Iterable[TResult]]:
        """Map source sequence.

        Builds a new collection whose elements are the results of
        applying the given function to each of the elements of the
        collection.
        """
        def _map(source: Iterable[TSource]) -> Seq[TResult]:
            return seq(mapper(x) for x in source)
        return _map

    @staticmethod
    def max() -> Callable[[Iterable[TSource]], TSource]:
        """Returns the greatest of all elements of the sequence,
        compared via `max()`."""

        def _map(source: Iterable[TSource]) -> TSource:
            return max(source)
        return _map

    @staticmethod
    def max_by(projection: Callable[[TSource], TResult]) -> Callable[[Iterable[TSource]], TResult]:
        def _max_by(source: Iterable[TSource]) -> TResult:
            return max(projection(x) for x in source)
        return _max_by

    @staticmethod
    def min() -> Callable[[Iterable[TSource]], TSource]:
        """Returns the smallest of all elements of the sequence,
        compared via `max()`."""

        def _min(source: Iterable[TSource]) -> TSource:
            return min(source)
        return _min

    @staticmethod
    def min_by(projection: Callable[[TSource], TResult]) -> Callable[[Iterable[TSource]], TResult]:
        def _min_by(source: Iterable[TSource]) -> TResult:
            return min(projection(x) for x in source)
        return _min_by

    @classmethod
    def of_list(cls, list: List[TSource]):
        return Seq(list)


class Seq(Iterable[TSource]):
    """Sequence type.

    Contains instance methods for dot-chaining operators methods on
    sequences.

    Example:
        >>> xs = Seq([1, 2, 3])
        >>> ys = xs.map(lambda x: x + 1).filter(lambda x: x < 3)
    """

    def __init__(self, iterable=[]) -> None:
        self._value = iterable

    def filter(self, predicate: Callable[[TSource], bool]) -> 'Seq[TSource]':
        return Seq(SeqModule.filter(predicate)(self))

    def head(self) -> TSource:
        """Returns the first element of the sequence."""

        return SeqModule.head()(self)

    def map(self, mapper: Callable[[TSource], TResult]) -> 'Seq[TResult]':
        return Seq(SeqModule.map(mapper)(self))

    def __iter__(self) -> Iterator[TSource]:
        return iter(self._value)


def seq(
    fn: Union[
        Callable[[], Generator[TSource, None, None]],
        Generator[TSource, None, None],
    ]
) -> Seq[TSource]:
    """Option builder.

    Enables the use of sequences as computational expressions using
    coroutines. Note that this is exactly the same as just using
    generators. But we define it for completeness.
    """

    if isinstance(fn, types.GeneratorType):
        return Seq(fn)

    if callable(fn):
        return Seq(fn())

    return Seq()


__all__ = ["SeqModule", "Seq", "seq"]
