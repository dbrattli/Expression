
from collections.abc import Generator, Iterable
from typing import List, Any

from pytest import raises

from expression import effect
from expression.collections.seq import Seq
from tests.utils import CustomException


def test_seq_builder_evaluation_order():
    """Test that seq builder evaluates computations in the correct order."""
    evaluated: List[int] = []

    @effect.seq[int]()
    def fn() -> Generator[int | None, Any, int | None]: # Updated type hint
        evaluated.append(1)  # First computation
        yield 42 # Yield single value

        evaluated.append(2)  # Second computation
        yield 43 # Yield single value

        evaluated.append(3)  # Final computation
        return sum(evaluated)

    computation = fn()

    assert evaluated == [1, 2, 3]  # All computations ran in order
    assert list(computation) == [42, 43, 6]


def test_seq_builder_empty_sequence():
    """Test that seq builder properly handles empty sequences."""
    evaluated: List[int] = []

    @effect.seq[int]()
    def fn() -> Generator[int, Any, int]:
        evaluated.append(1)  # First computation
        yield 42

        evaluated.append(2)  # This should be executed
        yield from Seq.empty()  # Yield from empty sequence - using Seq.empty()

        evaluated.append(3)  # This should still be executed as no short-circuit
        return sum(evaluated)

    computation = fn()
    assert evaluated == [1, 2, 3]  # Should run to the end, no short-circuit
    assert list(computation) == [42, 6] # Should still produce a value


def test_seq_builder_combine():
    """Test that seq builder properly combines computations."""
    evaluated: List[int] = []

    @effect.seq[int]()
    def fn() -> Generator[int, Any, int]:
        evaluated.append(1)
        yield 42  # First computation

        evaluated.append(2)
        yield from Seq([43, 44]) # Yield from sequence

        evaluated.append(3)
        return sum(evaluated)  # Final result

    computation = fn()

    assert evaluated == [1, 2, 3]  # All computations ran
    assert list(computation) == [42, 43, 44, 6]  # Returns values from sequence


def test_seq_builder_return_from():
    """Test that seq builder properly handles return! (return_from)."""

    @effect.seq[Iterable[int]]()
    def fn() -> Generator[Iterable[int], Any, Iterable[int]]:
        x: Iterable[int] = yield [1, 2, 3]
        return x

    computation = fn()
    assert list(computation) == [[1, 2, 3], [1, 2, 3]]  # Should return the same sequence


def test_seq_builder_zero():
    """Test that seq builder properly handles empty computations."""

    @effect.seq[int]()
    def fn() -> Generator[int, Any, None]:
        if False:
            yield 42
        # No return or yield, should use zero()

    computation = fn()
    assert list(computation) == []


def test_seq_builder_yield_from_sequence():
    """Test that seq builder properly handles yield from a sequence."""

    @effect.seq[int]()
    def fn() -> Generator[int, Any, int]:
        current_sum = 0
        for x in [42, 43]:
            current_sum += x
            yield x # yield individual values from sequence
        return current_sum

    computation = fn()
    assert list(computation) == [42, 43, 85]
    assert sum(computation) == 170  # 42 + 43 + 85


def test_seq_builder_multiple_operations():
    """Test that seq builder properly handles multiple operations."""

    @effect.seq[int]()
    def fn() -> Generator[int, Any, int]:
        current_sum = 0
        current_sum += 42
        yield 42
        for x in [43, 44]:
            current_sum += x
            yield x

        current_sum += 45
        yield 45
        return current_sum

    computation = fn()
    assert list(computation) == [42, 43, 44, 45, 174]


def test_seq_builder_nested():
    """Test that seq builder properly handles nested computations."""

    @effect.seq[int]()
    def inner(x: int) -> Generator[int, Any, int]:
        yield x
        return x + 1

    @effect.seq[int]()
    def outer() -> Generator[int, Any, int]:
        yield 42
        yield from inner(42+1)  # Nested computation
        return 45

    computation = outer()
    assert list(computation) == [42, 43, 44, 45]


def test_seq_builder_throws():
    """Test that seq builder properly handles exceptions."""
    error = "test error"

    @effect.seq[int]()
    def fn() -> Generator[int, Any, int]:
        raise CustomException(error)
        yield 42  # Should not reach here

    with raises(CustomException) as ex_info:
        fn()
    assert ex_info.value.message == error  # CustomException has message attribute



def test_seq_builder_yield_sequence_wrapped():
    """Test that seq builder properly handles yielding a sequence directly."""

    @effect.seq[Iterable[int]]()
    def fn() -> Generator[Iterable[int], Any, Iterable[int]]:
        x: Iterable[int] = yield [1, 2, 3]  # Yield sequence directly
        return x  # Return the wrapped value

    computation = fn()
    assert list(computation) == [[1, 2, 3], [1, 2, 3]]  # Should return the same sequence


def test_seq_builder_return_empty_sequence():
    """Test that seq builder properly handles returning empty sequence directly."""

    @effect.seq[Iterable[int]]()
    def fn() -> Generator[Iterable[int], Any, Iterable[int]]:
        return []
        yield  # Should not reach here

    computation = fn()
    assert list(computation) == [[]]


def test_seq_builder_yield_value_async():
    """Test that seq builder properly handles async-style yields."""

    @effect.seq[int]()
    def fn() -> Generator[int, Any, None]:
        yield 42

    computation = fn()
    assert list(computation) == [42]


def test_seq_builder_while():
    """Test that seq builder properly handles while loops."""
    evaluated: List[int] = []

    @effect.seq[int]()
    def fn() -> Generator[int, Any, int]:
        i = 0
        while i < 3:
            evaluated.append(i)
            yield i  # Using _ for unused variable
            i += 1
        return sum(evaluated)

    computation = fn()
    assert evaluated == [0, 1, 2]  # All computations ran
    assert list(computation) == [0, 1, 2, 3]


def test_seq_builder_projection_int_str():
    """Test that seq builder properly handles type projections."""

    @effect.seq[str]()
    def fn() -> Generator[str, Any, str]:
        z: str = "Not found"
        for x in [42.0]:
            for y in [int(x)]:
                yield from Seq([str(y)]) # yield from string sequence
                z = "42" # update z

        return z

    computation = fn()
    assert list(computation) == ["42", "42"]  # Should return the same sequence


def test_seq_builder_yield_from_empty_sequence_short_circuit():
    """Test that yield from empty sequence does not short circuit, but yields empty sequence."""

    @effect.seq[int]()
    def fn() -> Generator[int, Any, int]:
        current_sum = 0
        yield from Seq.empty()  # Should not short circuit, just no values - using Seq.empty()

        # The rest should execute, but with empty x
        for y in [43, 44]:
            current_sum += y
            yield y
        return current_sum # returns sum of [43, 44]

    computation = fn()
    assert list(computation) == [43, 44, 87]
