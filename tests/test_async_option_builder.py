"""Tests for async_option builder implementation."""

import asyncio
from collections.abc import AsyncGenerator
from typing import List

import pytest
from pytest import raises

from expression import effect, Some, Nothing, Option
from tests.utils import CustomException


@pytest.mark.asyncio
async def test_async_option_builder_evaluation_order():
    """Test that async_option builder evaluates computations in the correct order."""
    evaluated: List[int] = []

    @effect.async_option[int]()
    async def fn() -> AsyncGenerator[int, int]:
        evaluated.append(1)  # First computation
        x: int = yield 42

        evaluated.append(2)  # Second computation
        y: int = yield 43

        evaluated.append(3)  # Final computation
        yield x + y  # Instead of return, use yield for the final value

    computation = await fn()
    assert evaluated == [1, 2, 3]  # All computations ran in order
    assert computation == Some(85)


@pytest.mark.asyncio
async def test_async_option_builder_short_circuit():
    """Test that async_option builder properly short circuits with Nothing."""
    evaluated: List[int] = []

    @effect.async_option[int]()
    async def fn() -> AsyncGenerator[int, int]:
        evaluated.append(1)  # First computation
        x: int = yield 42

        evaluated.append(2)  # Should not reach here
        # Use await with Nothing to leverage the awaitable functionality
        y: int = yield await Nothing  # Short circuits here

        evaluated.append(3)  # Should not reach here
        yield x + y  # This won't be reached

    computation = await fn()
    assert evaluated == [1, 2]  # Should run until yield Nothing
    assert computation is Nothing


@pytest.mark.asyncio
async def test_async_option_builder_combine():
    """Test that async_option builder properly combines computations."""
    evaluated: List[int] = []

    @effect.async_option[int]()
    async def fn() -> AsyncGenerator[int, int]:
        evaluated.append(1)
        yield 42  # First computation

        evaluated.append(2)
        yield 43  # Second computation combined with first

        evaluated.append(3)
        yield 44  # Final result

    computation = await fn()
    assert evaluated == [1, 2, 3]  # All computations ran
    assert computation == Some(44)  # Returns final value


@pytest.mark.asyncio
async def test_async_option_builder_return_from():
    """Test that async_option builder properly handles return! (return_from)."""

    @effect.async_option[int]()
    async def fn() -> AsyncGenerator[int, int]:
        x: int = yield await Some(42)
        yield x

    computation = await fn()
    match computation:
        case Option(tag="some", some=value):
            assert value == 42
        case _:
            assert False


@pytest.mark.asyncio
async def test_async_option_builder_zero():
    """Test that async_option builder properly handles empty computations."""

    @effect.async_option[int]()
    async def fn() -> AsyncGenerator[int, int]:
        if False:
            yield 42
        # No yield should use zero()

    computation = await fn()
    assert computation is Nothing  # Assert that zero() returns Nothing


@pytest.mark.asyncio
async def test_async_option_builder_yield_some():
    """Test that async_option builder properly handles yielding Some."""

    @effect.async_option[int]()
    async def fn() -> AsyncGenerator[int, int]:
        # Use await with Some to leverage the awaitable functionality
        x: int = yield await Some(42)
        yield x + 1

    computation = await fn()
    match computation:
        case Option(tag="some", some=value):
            assert value == 43
        case _:
            assert False


@pytest.mark.asyncio
async def test_async_option_builder_yield_nothing():
    """Test that async_option builder properly handles yielding Nothing."""

    @effect.async_option[int]()
    async def fn() -> AsyncGenerator[int, int]:
        # Use await with Nothing to leverage the awaitable functionality
        x: int = yield await Nothing
        yield x + 1  # Should not reach here

    computation = await fn()
    assert computation is Nothing


@pytest.mark.asyncio
async def test_async_option_builder_multiple_operations():
    """Test that async_option builder properly handles multiple operations."""

    @effect.async_option[int]()
    async def fn() -> AsyncGenerator[int, int]:
        x: int = yield 42
        y: int = yield await Some(43)
        z: int = yield 44
        yield x + y + z

    computation = await fn()
    match computation:
        case Option(tag="some", some=value):
            assert value == 129  # 42 + 43 + 44
        case _:
            assert False


@pytest.mark.asyncio
async def test_async_option_builder_nested():
    """Test that async_option builder properly handles nested computations."""

    @effect.async_option[int]()
    async def inner(x: int) -> AsyncGenerator[int, int]:
        y: int = yield x + 1
        yield y + 1

    @effect.async_option[int]()
    async def outer() -> AsyncGenerator[int, int]:
        x: int = yield 42

        # Call inner and await its result
        inner_result = await inner(x)
        y: int = yield await inner_result  # Then yield the result

        yield y + 1

    computation = await outer()
    assert computation == Some(45)  # 42 -> 43 -> 44 -> 45


@pytest.mark.asyncio
async def test_async_option_builder_throws():
    """Test that async_option builder properly handles exceptions."""
    error = "test error"

    @effect.async_option[int]()
    async def fn() -> AsyncGenerator[int, int]:
        raise CustomException(error)
        yield 42  # Should not reach here

    with raises(CustomException) as ex_info:
        await fn()
    assert ex_info.value.message == error  # CustomException has message attribute


@pytest.mark.asyncio
async def test_async_option_builder_return_some():
    """Test that async_option builder properly handles returning Some."""

    @effect.async_option[int]()
    async def fn() -> AsyncGenerator[int, int]:
        x: int = yield 42
        yield x  # Use yield instead of return

    computation = await fn()
    match computation:
        case Option(tag="some", some=value):
            assert value == 42  # Value should be wrapped in Some
        case _:
            assert False


@pytest.mark.asyncio
async def test_async_option_builder_yield_some_wrapped():
    """Test that async_option builder properly handles yielding Some directly."""

    @effect.async_option[int]()
    async def fn() -> AsyncGenerator[int, int]:
        x: int = yield await Some(42)  # Yield Some directly
        yield x  # Use yield instead of return

    computation = await fn()
    match computation:
        case Option(tag="some", some=value):
            assert value == 42  # Value should be unwrapped
        case _:
            assert False


@pytest.mark.asyncio
async def test_async_option_builder_yield_value_async():
    """Test that async_option builder properly handles async-style yields."""

    @effect.async_option[int]()
    async def fn() -> AsyncGenerator[int, int]:
        yield 42
        # No need for explicit return None

    computation = await fn()
    match computation:
        case Option(tag="some", some=value):
            assert value == 42
        case _:
            assert False


@pytest.mark.asyncio
async def test_async_option_builder_while():
    """Test that async_option builder properly handles while loops."""
    evaluated: List[int] = []

    @effect.async_option[int]()
    async def fn() -> AsyncGenerator[int, int]:
        i = 0
        while i < 3:
            evaluated.append(i)
            _ = yield i  # Using _ for unused variable
            i += 1
        yield i

    computation = await fn()
    assert evaluated == [0, 1, 2]
    assert computation == Some(3)


@pytest.mark.asyncio
async def test_async_option_builder_projection_int_str():
    """Test that async_option builder properly handles type projections."""

    @effect.async_option[str]()
    async def fn() -> AsyncGenerator[str, str]:
        z: str = "Not found"

        # Iterate over Some result (since Option is iterable)
        for x in Some(42.0):
            for y in Some(int(x)):
                z = yield await Some(str(y))

        yield z

    computation = await fn()
    match computation:
        case Option(tag="some", some=value):
            assert value == "42"
        case _:
            assert False


@pytest.mark.asyncio
async def test_async_option_builder_yield_nothing_short_circuit():
    """Test that yielding Nothing properly short circuits nested operations."""

    @effect.async_option[int]()
    async def fn() -> AsyncGenerator[int, int]:
        x = yield await Nothing  # Short circuits here

        # The rest should not execute
        y = yield await Some(43)
        yield x + y

    computation = await fn()
    assert computation is Nothing


@pytest.mark.asyncio
async def test_async_option_builder_with_async_functions():
    """Test that async_option builder properly works with async functions."""

    async def async_function(x: int) -> int:
        await asyncio.sleep(0.01)  # Small delay to simulate async work
        return x * 2

    @effect.async_option[int]()
    async def fn() -> AsyncGenerator[int, int]:
        x: int = yield 21

        # Call an async function and use its result
        doubled = await async_function(x)
        y: int = yield doubled

        yield y

    computation = await fn()
    assert computation == Some(42)


@pytest.mark.asyncio
async def test_async_option_builder_with_async_option_functions():
    """Test that async_option builder properly works with functions returning async Options."""

    async def async_some_function(x: int) -> int:
        await asyncio.sleep(0.01)  # Small delay to simulate async work
        return await Some(x * 2)

    async def async_nothing_function() -> int:
        await asyncio.sleep(0.01)  # Small delay to simulate async work
        return await Nothing

    @effect.async_option[int]()
    async def success_fn() -> AsyncGenerator[int, int]:
        x: int = yield 21

        # Call async function and get its result
        result = await async_some_function(x)
        # Then yield the result
        y: int = yield result

        yield y

    @effect.async_option[int]()
    async def nothing_fn() -> AsyncGenerator[int, int]:
        _: int = yield 21

        # Call async function and get its result
        result = await async_nothing_function()
        # Then yield it - this should short-circuit
        y: int = yield result

        yield y  # Should not reach here

    success_computation = await success_fn()
    assert success_computation == Some(42)

    nothing_computation = await nothing_fn()
    assert nothing_computation is Nothing


@pytest.mark.asyncio
async def test_async_option_builder_with_nested_async_generators():
    """Test that async_option builder properly works with nested async generators."""

    @effect.async_option[int]()
    async def inner_gen(x: int) -> AsyncGenerator[int, int]:
        y: int = yield x + 1
        yield y + 1

    @effect.async_option[int]()
    async def outer_gen() -> AsyncGenerator[int, int]:
        x: int = yield 40

        # Call inner_gen and await its result
        inner_result = await inner_gen(x)
        # Then yield the result
        y: int = yield await inner_result

        yield y

    computation = await outer_gen()
    assert computation == Some(42)  # 40 -> 41 -> 42
