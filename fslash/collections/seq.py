from typing import Generic, TypeVar, Callable, Iterable, Iterator, Generator, List, Union, Coroutine, Optional, cast
import functools
import itertools

TSource = TypeVar("TSource")
TResult = TypeVar("TResult")
TState = TypeVar("TState")


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
    def concat(*iterables: Iterable[TSource]) -> Callable[[Iterable[TSource]], Iterable[TSource]]:
        """Combines the given enumeration-of-enumerations as a single
        concatenated enumeration.

        Args:
            iterables: The input enumeration-of-enumerations.

        Returns:
            A partially applied concat function.
        """

        def _concat(*sources: Iterable[TSource]) -> Iterable[TSource]:
            """Partially applied concat function.

            Args:
                sources: The input enumeration-of-enumerations.

            Returns:
                The result sequence.
            """
            return itertools.chain(*iterables, *sources)

        return _concat

    @classmethod
    def empty(cls):
        """Creates an empty sequence.

        Returns:
            An empty sequence.
        """
        return Seq([])

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
    def fold(folder: Callable[[TState, TSource], TState], state: TState) -> Callable[[Iterable[TSource]], TState]:
        """Applies a function to each element of the collection,
        threading an accumulator argument through the computation. If
        the input function is f and the elements are i0...iN then
        computes f (... (f s i0)...) iN

        Args:
            folder: A function that updates the state with each element
                from the sequence.
            state: The initial state.
        Returns:
            Partially applied fold function.
        """
        def _fold(source: Iterable[TSource]) -> TState:
            """Partially applied fold function.
            Returns:
                The state object after the folding function is applied
                to each element of the sequence.
            """
            return functools.reduce(folder, source, state)  # type: ignore

        return _fold

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

        Args:
            mapping: A function to transform items from the input sequence.

        Returns:
            Partially applied map function.
        """

        def _map(source: Iterable[TSource]) -> Iterable[TResult]:
            """Partially applied map function.

            Args:
                source: The input sequence.
            Returns:
                The result sequence.
            """
            return (mapper(x) for x in source)

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

    @staticmethod
    def scan(
        scanner: Callable[[TState, TSource], TState], state: TState
    ) -> Callable[[Iterable[TSource]], Iterable[TState]]:
        """Like fold, but computes on-demand and returns the sequence of
        intermediary and final results.

        Args:
            scanner: A function that updates the state with each element
                from the sequence.
            state: The initial state.
        """
        def _scan(source: Iterable[TSource]) -> Iterable[TState]:
            """Partially applied scan function.
            Args:
                source: The input sequence.
            Returns:
                The resulting sequence of computed states.
            """
            return itertools.accumulate(source, scanner, initial=state)   # type: ignore
        return _scan


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

    def filter(self, predicate: Callable[[TSource], bool]) -> "Seq[TSource]":
        return Seq(SeqModule.filter(predicate)(self))

    def fold(self, folder: Callable[[TState, TSource], TState], state: TState) -> TState:
        """Applies a function to each element of the collection,
        threading an accumulator argument through the computation. If
        the input function is f and the elements are i0...iN then
        computes f (... (f s i0)...) iN

        Args:
            folder: A function that updates the state with each element
                from the sequence.
            state: The initial state.
        Returns:
            The state object after the folding function is applied to
            each element of the sequence.
            """
        return functools.reduce(folder, self, state)  # type: ignore

    def head(self) -> TSource:
        """Returns the first element of the sequence."""

        return SeqModule.head()(self)

    def map(self, mapper: Callable[[TSource], TResult]) -> "Seq[TResult]":
        """Map sequence.

        Builds a new collection whose elements are the results of
        applying the given function to each of the elements of the
        collection.

        Args:
            mapping: A function to transform items from the input sequence.

        Returns:
            The result sequence.
        """

        return Seq(SeqModule.map(mapper)(self))

    def scan(self, scanner: Callable[[TState, TSource], TState], state: TState) -> Iterable[TState]:
        """Like fold, but computes on-demand and returns the sequence of
        intermediary and final results.

        Args:
            scanner: A function that updates the state with each element
                from the sequence.
            state: The initial state.

        Returns:
            The resulting sequence of computed states.
        """
        return Seq(itertools.accumulate(self, scanner, initial=state))   # type: ignore

    def __iter__(self) -> Iterator[TSource]:
        """Return iterator for sequence."""
        return iter(self._value)


def seq(
    fn: Callable[  # Function
        ...,
        Union[
            Coroutine[TSource, Optional[TSource], Optional[Iterable[TSource]]],
            # Generator that yields or returns an option
            Generator[TSource, Optional[TSource], Optional[Iterable[TSource]]],
            # or simply just an Iterable
            Iterable[TSource]
        ]
    ]
) -> Callable[..., Seq[TSource]]:
    """Sequence builder.

    Enables the use of sequences as computational expressions using
    generators and coroutines Note that this is exactly the same as just
    using generators. But we define it for completeness.
    """

    def wrapper(*args, **kw) -> Seq[TSource]:
        return Seq(cast(Callable, fn)(*args, **kw))
    return wrapper


__all__ = ["SeqModule", "Seq", "seq"]
