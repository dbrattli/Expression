"""Tests for async_result builder implementation."""

import asyncio
from collections.abc import AsyncGenerator
from typing import List

import pytest
from pytest import raises

from expression import effect, Ok, Error, Result
from tests.utils import CustomException


@pytest.mark.asyncio
async def test_async_result_builder_evaluation_order():
    """Test that async_result builder evaluates computations in the correct order."""
    evaluated: List[int] = []

    @effect.async_result[int, str]()
    async def fn() -> AsyncGenerator[int, int]:
        evaluated.append(1)  # First computation
        x: int = yield 42

        evaluated.append(2)  # Second computation
        y: int = yield 43

        evaluated.append(3)  # Final computation
        yield x + y  # Instead of return, use yield for the final value

    computation = await fn()
    assert evaluated == [1, 2, 3]  # All computations ran in order
    assert computation == Ok(85)


@pytest.mark.asyncio
async def test_async_result_builder_short_circuit():
    """Test that async_result builder properly short circuits with Error."""
    evaluated: List[int] = []

    @effect.async_result[int, str]()
    async def fn() -> AsyncGenerator[int, int]:
        evaluated.append(1)  # First computation
        x: int = yield 42

        evaluated.append(2)  # Should not reach here
        # Use await with Error to leverage the awaitable functionality
        y: int = yield await Error("error")  # Short circuits here

        evaluated.append(3)  # Should not reach here
        yield x + y  # This won't be reached

    computation = await fn()
    assert evaluated == [1, 2]  # Should run until yield Error
    assert computation == Error("error")


@pytest.mark.asyncio
async def test_async_result_builder_combine():
    """Test that async_result builder properly combines computations."""
    evaluated: List[int] = []

    @effect.async_result[int, str]()
    async def fn() -> AsyncGenerator[int, int]:
        evaluated.append(1)
        yield 42  # First computation

        evaluated.append(2)
        yield 43  # Second computation combined with first

        evaluated.append(3)
        yield 44  # Final result

    computation = await fn()
    assert evaluated == [1, 2, 3]  # All computations ran
    assert computation == Ok(44)  # Returns final value


@pytest.mark.asyncio
async def test_async_result_builder_return_from():
    """Test that async_result builder properly handles return! (return_from)."""

    @effect.async_result[int, str]()
    async def fn() -> AsyncGenerator[int, int]:
        x: int = yield await Ok(42)
        yield x

    computation = await fn()
    match computation:
        case Result(tag="ok", ok=value):
            assert value == 42
        case _:
            assert False


@pytest.mark.asyncio
async def test_async_result_builder_zero():
    """Test that async_result builder properly handles empty computations."""

    @effect.async_result[int, str]()
    async def fn() -> AsyncGenerator[int, int]:
        if False:
            yield 42
        # No yield should use zero()

    computation = await fn()
    assert computation == Ok(None)  # Assert that zero() returns Ok(None)


@pytest.mark.asyncio
async def test_async_result_builder_yield_ok():
    """Test that async_result builder properly handles yielding Ok."""

    @effect.async_result[int, str]()
    async def fn() -> AsyncGenerator[int, int]:
        # Use await with Ok to leverage the awaitable functionality
        x: int = yield await Ok(42)
        yield x + 1

    computation = await fn()
    match computation:
        case Result(tag="ok", ok=value):
            assert value == 43
        case _:
            assert False


@pytest.mark.asyncio
async def test_async_result_builder_yield_error():
    """Test that async_result builder properly handles yielding Error."""

    @effect.async_result[int, str]()
    async def fn() -> AsyncGenerator[int, int]:
        # Use await with Error to leverage the awaitable functionality
        x: int = yield await Error("error")
        yield x + 1  # Should not reach here

    computation = await fn()
    match computation:
        case Result(tag="error", error=err):
            assert err == "error"
        case _:
            assert False


@pytest.mark.asyncio
async def test_async_result_builder_multiple_operations():
    """Test that async_result builder properly handles multiple operations."""

    @effect.async_result[int, str]()
    async def fn() -> AsyncGenerator[int, int]:
        x: int = yield 42
        y: int = yield await Ok(43)
        z: int = yield 44
        yield x + y + z

    computation = await fn()
    match computation:
        case Result(tag="ok", ok=value):
            assert value == 129  # 42 + 43 + 44
        case _:
            assert False


@pytest.mark.asyncio
async def test_async_result_builder_nested():
    """Test that async_result builder properly handles nested computations."""

    @effect.async_result[int, str]()
    async def inner(x: int) -> AsyncGenerator[int, int]:
        y: int = yield x + 1
        yield y + 1

    @effect.async_result[int, str]()
    async def outer() -> AsyncGenerator[int, int]:
        x: int = yield 42

        # Call inner and await its result
        inner_result = await inner(x)
        y: int = yield await inner_result  # Then yield the result

        yield y + 1

    computation = await outer()
    assert computation == Ok(45)  # 42 -> 43 -> 44 -> 45


@pytest.mark.asyncio
async def test_async_result_builder_throws():
    """Test that async_result builder properly handles exceptions."""
    error = "test error"

    @effect.async_result[int, str]()
    async def fn() -> AsyncGenerator[int, int]:
        raise CustomException(error)
        yield 42  # Should not reach here

    with raises(CustomException) as ex_info:
        await fn()
    assert ex_info.value.message == error  # CustomException has message attribute


@pytest.mark.asyncio
async def test_async_result_builder_return_ok():
    """Test that async_result builder properly handles returning Ok."""

    @effect.async_result[int, str]()
    async def fn() -> AsyncGenerator[int, int]:
        x: int = yield 42
        yield x  # Use yield instead of return

    computation = await fn()
    match computation:
        case Result(tag="ok", ok=value):
            assert value == 42  # Value should be wrapped in Ok
        case _:
            assert False


@pytest.mark.asyncio
async def test_async_result_builder_yield_ok_wrapped():
    """Test that async_result builder properly handles yielding Ok directly."""

    @effect.async_result[int, str]()
    async def fn() -> AsyncGenerator[int, int]:
        x: int = yield await Ok(42)  # Yield Ok directly
        yield x  # Use yield instead of return

    computation = await fn()
    match computation:
        case Result(tag="ok", ok=value):
            assert value == 42  # Value should be unwrapped
        case _:
            assert False

@pytest.mark.asyncio
async def test_async_result_builder_return_error_wrapped():
    """Test that async_result builder properly handles returning Error directly."""

    @effect.async_result[Result[int, str], str]()
    async def fn() -> AsyncGenerator[Result[int, str], Result[int, str]]:
        yield Error("error")  # Use yield await instead of return
        # No need for additional yield

    computation = await fn()
    match computation:
        case Result(tag="ok", ok=inner_result):  # Match Ok case now
            match inner_result:
                case Result(tag="error", error=err):  # Match inner Error case
                    assert err == "error"  # Assert against inner Error value
                case _:
                    assert False  # Inner result should be Error
        case _:
            assert False  # Outer result should be Ok


@pytest.mark.asyncio
async def test_async_result_builder_yield_value_async():
    """Test that async_result builder properly handles async-style yields."""

    @effect.async_result[int, str]()
    async def fn() -> AsyncGenerator[int, int]:
        yield 42
        # No need for explicit return None

    computation = await fn()
    match computation:
        case Result(tag="ok", ok=value):
            assert value == 42
        case _:
            assert False


@pytest.mark.asyncio
async def test_async_result_builder_while():
    """Test that async_result builder properly handles while loops."""
    evaluated: List[int] = []

    @effect.async_result[int, str]()
    async def fn() -> AsyncGenerator[int, int]:
        i = 0
        while i < 3:
            evaluated.append(i)
            _ = yield i  # Using _ for unused variable
            i += 1
        yield i

    computation = await fn()
    assert evaluated == [0, 1, 2]
    assert computation == Ok(3)


@pytest.mark.asyncio
async def test_async_result_builder_projection_int_str():
    """Test that async_result builder properly handles type projections."""

    @effect.async_result[str, str]()
    async def fn() -> AsyncGenerator[str, str]:
        z: str = "Not found"

        # Iterate over Ok result (since Result is iterable)
        for x in Ok(42.0):
            for y in Ok(int(x)):
                z = yield await Ok(str(y))

        yield z

    computation = await fn()
    match computation:
        case Result(tag="ok", ok=value):
            assert value == "42"
        case _:
            assert False


@pytest.mark.asyncio
async def test_async_result_builder_yield_error_short_circuit():
    """Test that yielding Error properly short circuits nested operations."""

    @effect.async_result[int, str]()
    async def fn() -> AsyncGenerator[int, int]:
        x = yield await Error("error")  # Short circuits here

        # The rest should not execute
        y = yield await Ok(43)
        yield x + y

    computation = await fn()
    match computation:
        case Result(tag="error", error=err):
            assert err == "error"
        case _:
            assert False


@pytest.mark.asyncio
async def test_async_result_builder_with_async_functions():
    """Test that async_result builder properly works with async functions."""

    async def async_function(x: int) -> int:
        await asyncio.sleep(0.01)  # Small delay to simulate async work
        return x * 2

    @effect.async_result[int, str]()
    async def fn() -> AsyncGenerator[int, int]:
        x: int = yield 21

        # Call an async function and use its result
        doubled = await async_function(x)
        y: int = yield doubled

        yield y

    computation = await fn()
    assert computation == Ok(42)


@pytest.mark.asyncio
async def test_async_result_builder_with_async_result_functions():
    """Test that async_result builder properly works with functions returning async Results."""

    async def async_ok_function(x: int) -> int:
        await asyncio.sleep(0.01)  # Small delay to simulate async work
        return await Ok(x * 2)

    async def async_error_function(msg: str) -> int:
        await asyncio.sleep(0.01)  # Small delay to simulate async work
        return await Error(msg)

    @effect.async_result[int, str]()
    async def success_fn() -> AsyncGenerator[int, int]:
        x: int = yield 21

        # Call async function and get its result
        result = await async_ok_function(x)
        # Then yield the result
        y: int = yield result

        yield y

    @effect.async_result[int, str]()
    async def error_fn() -> AsyncGenerator[int, int]:
        _: int = yield 21

        # Call async function and get its result
        result = await async_error_function("async error")
        # Then yield it - this should short-circuit
        y: int = yield result

        yield y  # Should not reach here

    success_computation = await success_fn()
    assert success_computation == Ok(42)

    error_computation = await error_fn()
    assert error_computation == Error("async error")


@pytest.mark.asyncio
async def test_async_result_builder_with_nested_async_generators():
    """Test that async_result builder properly works with nested async generators."""

    @effect.async_result[int, str]()
    async def inner_gen(x: int) -> AsyncGenerator[int, int]:
        y: int = yield x + 1
        yield y + 1

    @effect.async_result[int, str]()
    async def outer_gen() -> AsyncGenerator[int, int]:
        x: int = yield 40

        # Call inner_gen and await its result
        inner_result = await inner_gen(x)
        # Then yield the result
        y: int = yield await inner_result

        yield y

    computation = await outer_gen()
    assert computation == Ok(42)  # 40 -> 41 -> 42
