"""Tests for result builder implementation."""

from collections.abc import Generator
from typing import List

from pytest import raises

from expression import effect, Ok, Error, Result
from tests.utils import CustomException


def test_result_builder_evaluation_order():
    """Test that result builder evaluates computations in the correct order."""
    evaluated: List[int] = []

    @effect.result[int, str]()
    def fn() -> Generator[int, int, int]:
        evaluated.append(1)  # First computation
        x: int = yield 42

        evaluated.append(2)  # Second computation
        y: int = yield 43

        evaluated.append(3)  # Final computation
        return x + y

    computation = fn()
    assert evaluated == [1, 2, 3]  # All computations ran in order
    assert computation == Ok(85)


def test_result_builder_short_circuit():
    """Test that result builder properly short circuits with Error."""
    evaluated: List[int] = []

    @effect.result[int, str]()
    def fn() -> Generator[int, int, int]:
        evaluated.append(1)  # First computation
        x: int = yield 42

        evaluated.append(2)  # Should not reach here
        y: int = yield from Error("error")  # Short circuits

        evaluated.append(3)  # Should not reach here
        return x + y

    computation = fn()
    assert evaluated == [1, 2]  # Should run until yield from Error
    assert computation == Error("error")


def test_result_builder_combine():
    """Test that result builder properly combines computations."""
    evaluated: List[int] = []

    @effect.result[int, str]()
    def fn() -> Generator[int, int, int]:
        evaluated.append(1)
        yield 42  # First computation

        evaluated.append(2)
        yield 43  # Second computation combined with first

        evaluated.append(3)
        return 44  # Final result

    computation = fn()
    assert evaluated == [1, 2, 3]  # All computations ran
    assert computation == Ok(44)  # Returns final value


def test_result_builder_return_from():
    """Test that result builder properly handles return! (return_from)."""

    @effect.result[Result[int, str], str]()
    def fn() -> Generator[Result[int, str], Result[int, str], Result[int, str]]:
        x: Result[int, str] = yield Ok(42)
        return x

    computation = fn()
    match computation:
        case Result(tag="ok", ok=value):
            assert value == Ok(42)
        case _:
            assert False


def test_result_builder_zero():
    """Test that result builder properly handles empty computations."""

    @effect.result[int, str]()
    def fn() -> Generator[int, int, None]:
        if False:
            yield 42
        # No return or yield should use zero()

    computation = fn()
    assert computation == Ok(None) # Assert that zero() returns Ok(None)


def test_result_builder_yield_from_ok():
    """Test that result builder properly handles yield from Ok."""

    @effect.result[int, str]()
    def fn() -> Generator[int, int, int]:
        x: int = yield from Ok(42)
        return x + 1

    computation = fn()
    match computation:
        case Result(tag="ok", ok=value):
            assert value == 43
        case _:
            assert False


def test_result_builder_yield_from_error():
    """Test that result builder properly handles yield from Error."""

    @effect.result[int, str]()
    def fn() -> Generator[int, int, int]:
        x: int = yield from Error("error")
        return x + 1  # Should not reach here

    computation = fn()
    match computation:
        case Result(tag="error", error=err):
            assert err == "error"
        case _:
            assert False


def test_result_builder_multiple_operations():
    """Test that result builder properly handles multiple operations."""

    @effect.result[int, str]()
    def fn() -> Generator[int, int, int]:
        x: int = yield 42
        y: int = yield from Ok(43)
        z: int = yield 44
        return x + y + z

    computation = fn()
    match computation:
        case Result(tag="ok", ok=value):
            assert value == 129  # 42 + 43 + 44
        case _:
            assert False


def test_result_builder_nested():
    """Test that result builder properly handles nested computations."""

    @effect.result[int, str]()
    def inner(x: int) -> Generator[int, int, int]:
        y: int = yield x + 1
        return y + 1

    @effect.result[int, str]()
    def outer() -> Generator[int, int, int]:
        x: int = yield 42
        y: int = yield from inner(x)  # Nested computation
        return y + 1

    computation = outer()
    assert computation == Ok(45)  # 42 -> 43 -> 44 -> 45


def test_result_builder_throws():
    """Test that result builder properly handles exceptions."""
    error = "test error"

    @effect.result[int, str]()
    def fn() -> Generator[int, int, int]:
        raise CustomException(error)
        yield 42  # Should not reach here

    with raises(CustomException) as ex_info:
        fn()
    assert ex_info.value.message == error  # CustomException has message attribute


def test_result_builder_return_ok():
    """Test that result builder properly handles returning Ok."""

    @effect.result[int, str]()
    def fn() -> Generator[int, int, int]:
        x: int = yield 42
        return x  # Return unwrapped value

    computation = fn()
    match computation:
        case Result(tag="ok", ok=value):
            assert value == 42  # Value should be wrapped in Ok
        case _:
            assert False


def test_result_builder_yield_ok_wrapped():
    """Test that result builder properly handles yielding Ok directly."""

    @effect.result[Result[int, str], str]()
    def fn() -> Generator[Result[int, str], Result[int, str], Result[int, str]]:
        x: Result[int, str] = yield Ok(42)  # Yield Ok directly
        return x  # Return the wrapped value

    computation = fn()
    match computation:
        case Result(tag="ok", ok=value):
            assert value == Ok(42)  # Value should be wrapped in Ok
        case _:
            assert False


def test_result_builder_return_error_wrapped():
    """Test that result builder properly handles returning Error directly."""

    @effect.result[Result[int, str], str]()
    def fn() -> Generator[Result[int, str], Result[int, str], Result[int, str]]:
        return Error("error")
        yield  # Should not reach here

    computation = fn()
    match computation:
        case Result(tag="ok", ok=inner_result): # Match Ok case now
            match inner_result:
                case Result(tag="error", error=err): # Match inner Error case
                    assert err == "error" # Assert against inner Error value
                case _:
                    assert False # Inner result should be Error
        case _:
            assert False # Outer result should be Ok


def test_result_builder_yield_value_async():
    """Test that result builder properly handles async-style yields."""

    @effect.result[int, str]()
    def fn() -> Generator[int, None, None]:
        yield 42
        return None  # Explicit return None to match generator type

    computation = fn()
    match computation:
        case Result(tag="ok", ok=value):
            assert value == 42
        case _:
            assert False


def test_result_builder_while():
    """Test that result builder properly handles while loops."""
    evaluated: List[int] = []

    @effect.result[int, str]()
    def fn() -> Generator[int, int, int]:
        i = 0
        while i < 3:
            evaluated.append(i)
            _ = yield i  # Using _ for unused variable
            i += 1
        return i

    computation = fn()
    assert evaluated == [0, 1, 2]
    assert computation == Ok(3)


def test_result_builder_projection_int_str():
    """Test that result builder properly handles type projections."""

    @effect.result[str, str]()
    def fn() -> Generator[str, str, str]:
        z: str = "Not found"
        for x in Ok(42.0):
            for y in Ok(int(x)):
                z = yield from Ok(str(y))

        return z

    for x in fn():
        assert x == "42"
        break
    else:
        assert False


def test_result_builder_yield_from_error_short_circuit():
    """Test that yield from Error properly short circuits nested operations."""

    @effect.result[int, str]()
    def fn() -> Generator[int, int, int]:
        x = yield from Error("error")  # Short circuits here

        # The rest should not execute
        y = yield from Ok(43)
        return x + y

    computation = fn()
    match computation:
        case Result(tag="error", error=err):
            assert err == "error"
        case _:
            assert False
