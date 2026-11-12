"""Tests for option builder implementation."""

from collections.abc import Generator
from typing import List, cast

from pytest import raises

from expression import effect, Some, NOTHING, Option
from expression.core.option import Option
from tests.utils import CustomException


def test_option_builder_evaluation_order():
    """Test that option builder evaluates computations in the correct order."""
    evaluated: List[int] = []

    @effect.option[int]()
    def fn() -> Generator[int, int, int]:
        evaluated.append(1)  # First computation
        x: int = yield 42
        assert x == 42

        evaluated.append(2)  # Second computation
        y: int = yield 43

        evaluated.append(3)  # Final computation
        return x + y

    computation = fn()
    assert evaluated == [1, 2, 3]  # All computations ran in order
    assert computation == Some(85)


def test_option_builder_short_circuit():
    """Test that option builder properly short circuits with NOTHING."""
    evaluated: List[int] = []

    @effect.option[int]()
    def fn() -> Generator[int, int, int]:
        evaluated.append(1)  # First computation
        x: int = yield 42

        evaluated.append(2)  # This should be executed
        y: int = yield from NOTHING  # Short circuits here

        evaluated.append(3)  # This should not be executed
        return x + y

    computation = fn()
    assert evaluated == [1, 2]  # Should run until yield from NOTHING
    assert computation is NOTHING


def test_option_builder_combine():
    """Test that option builder properly combines computations."""
    evaluated: List[int] = []

    @effect.option[int]()
    def fn() -> Generator[int, int, int]:
        evaluated.append(1)
        yield 42  # First computation

        evaluated.append(2)
        yield 43  # Second computation combined with first

        evaluated.append(3)
        return 44  # Final result

    computation = fn()
    assert evaluated == [1, 2, 3]  # All computations ran
    assert computation == Some(44)  # Returns final value


def test_option_builder_return_from():
    """Test that option builder properly handles return! (return_from)."""

    @effect.option[Option[int]]()
    def fn() -> Generator[Option[int], Option[int], Option[int]]:
        x: Option[int] = yield Some(42)
        return x

    computation = fn()
    match computation:
        case Some(value):
            assert value == Some(42)
        case _:
            assert False


def test_option_builder_zero():
    """Test that option builder properly handles empty computations."""

    @effect.option[int]()
    def fn() -> Generator[int, int, None]:
        if False:
            yield 42
        # No return or yield, should use zero()

    computation = fn()
    assert computation is NOTHING


def test_option_builder_yield_from_some():
    """Test that option builder properly handles yield from Some."""

    @effect.option[int]()
    def fn() -> Generator[int, int, int]:
        x: int = yield from Some(42)
        return x + 1

    computation = fn()
    match computation:
        case Some(value):
            assert value == 43
        case _:
            assert False


def test_option_builder_yield_from_none():
    """Test that option builder properly handles yield from NOTHING."""

    @effect.option[int]()
    def fn() -> Generator[int, int, int]:
        x: int = yield from NOTHING
        return x + 1  # Should not reach here

    computation = fn()
    assert computation is NOTHING


def test_option_builder_multiple_operations():
    """Test that option builder properly handles multiple operations."""

    @effect.option[int]()
    def fn() -> Generator[int, int, int]:
        x: int = yield 42
        y: int = yield from Some(43)
        z: int = yield 44
        return x + y + z

    computation = fn()
    match computation:
        case Some(value):
            assert value == 129  # 42 + 43 + 44
        case _:
            assert False


def test_option_builder_nested():
    """Test that option builder properly handles nested computations."""

    @effect.option[int]()
    def inner(x: int) -> Generator[int, int, int]:
        y: int = yield x + 1
        return y + 1

    @effect.option[int]()
    def outer() -> Generator[int, int, int]:
        x: int = yield 42
        # Pyright #11881 loses the return type for a union of iterable cases.
        y = cast(int, (yield from inner(x)))  # Nested computation
        return y + 1

    computation = outer()
    assert computation == Some(45)  # 42 -> 43 -> 44 -> 45


def test_option_builder_throws():
    """Test that option builder properly handles exceptions."""
    error = "test error"

    @effect.option[int]()
    def fn() -> Generator[int, int, int]:
        raise CustomException(error)
        yield 42  # Should not reach here

    with raises(CustomException) as ex_info:
        fn()
    assert ex_info.value.message == error  # CustomException has message attribute


def test_option_builder_return_some():
    """Test that option builder properly handles returning Some."""

    @effect.option[int]()
    def fn() -> Generator[int, int, int]:
        x: int = yield 42
        return x  # Return unwrapped value

    computation = fn()
    match computation:
        case Some(value):
            assert value == 42  # Value should be wrapped in Some
        case _:
            assert False


def test_option_builder_yield_some_wrapped():
    """Test that option builder properly handles yielding Some directly."""

    @effect.option[Option[int]]()
    def fn() -> Generator[Option[int], Option[int], Option[int]]:
        x: Option[int] = yield Some(42)  # Yield Some directly
        return x  # Return the wrapped value

    computation = fn()
    match computation:
        case Some(value):
            assert value == Some(42)  # Value should be wrapped in Some
        case _:
            assert False


def test_option_builder_return_nothing():
    """Test that option builder properly handles returning NOTHING directly."""

    @effect.option[Option[int]]()
    def fn() -> Generator[Option[int], Option[int], Option[int]]:
        return NOTHING
        yield  # Should not reach here

    computation = fn()
    match computation:
        case Some(value):
            assert value is NOTHING
        case _:
            assert False


def test_option_builder_yield_value_async():
    """Test that option builder properly handles async-style yields."""

    @effect.option[int]()
    def fn() -> Generator[int, None, None]:
        yield 42

    computation = fn()
    match computation:
        case Some(value):
            assert value == 42
        case _:
            assert False


def test_option_builder_while():
    """Test that option builder properly handles while loops."""
    evaluated: List[int] = []

    @effect.option[int]()
    def fn() -> Generator[int, int, int]:
        i = 0
        while i < 3:
            evaluated.append(i)
            _ = yield i  # Using _ for unused variable
            i += 1
        return i

    computation = fn()
    assert evaluated == [0, 1, 2]
    assert computation == Some(3)


def test_option_builder_projection_int_str():
    """Test that option builder properly handles type projections."""

    @effect.option[str]()
    def fn() -> Generator[str, str, str]:
        z: str = "Not found"
        for x in Some(42.0):
            for y in Some(int(x)):
                z = yield from Some(str(y))

        return z

    for x in fn():
        assert x == "42"
        break
    else:
        assert False


def test_option_builder_yield_from_nothing_short_circuit():
    """Test that yield from NOTHING properly short circuits nested operations."""

    @effect.option[int]()
    def fn() -> Generator[int, int, int]:
        x = yield from NOTHING  # Short circuits here

        # The rest should not execute
        y = yield from Some(43)
        return x + y

    computation = fn()
    assert computation is NOTHING


def test_option_builder_plain_function_body():
    """A body without a yield statement is treated like a `return` statement."""

    @effect.option[int]()
    def fn() -> int:
        return 42

    computation = fn()
    assert computation == Some(42)


def test_option_builder_plain_function_body_none():
    """A plain function body returning None maps to zero()."""

    @effect.option[int]()
    def fn() -> None:
        return None

    computation = fn()
    assert computation is NOTHING


def test_option_builder_runtime_error_propagates():
    """A RuntimeError raised in the body propagates instead of being swallowed."""

    @effect.option[int]()
    def fn() -> Generator[int, int, int]:
        raise RuntimeError("boom")
        yield 42  # Should not reach here

    with raises(RuntimeError, match="boom"):
        fn()


def test_option_builder_none_retains_last_yield():
    @effect.option[int]()
    def fn() -> Generator[int, int, None]:
        value = yield 42
        assert value == 42
        return None

    assert fn() == Some(42)


def test_option_builder_explicit_none_yield_is_success():
    @effect.option[None]()
    def fn() -> Generator[None, None, None]:
        yield None

    assert fn() == Some(None)
