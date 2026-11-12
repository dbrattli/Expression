import asyncio
import sys
from collections.abc import Callable
from typing import Any, assert_type

import pytest
from hypothesis import given
from hypothesis import strategies as st

from expression import NOTHING, Error, Ok, Result, Some, apipe, pipe, result
from expression.extra import async_result


@given(st.integers())
def test_pipe_id(x: int):
    value = asyncio.run(apipe(x))
    assert value == x


@given(st.integers())
def test_pipe_awaitable_only(x: int):
    async def awaitable_value() -> int:
        return x

    value = asyncio.run(apipe(awaitable_value()))
    assert value == x


@given(st.integers())
def test_pipe_fn(x: int):
    async def gn(x: int) -> int:
        return x + 1

    value = asyncio.run(apipe(x, gn))
    assert value == asyncio.run(gn(x))


@given(st.integers(), st.integers(), st.integers())
def test_pipe_fn_gn(x: int, y: int, z: int):
    fn: Callable[[int], int] = lambda x: x + z

    async def gn(x: int) -> int:
        return x * y

    value = asyncio.run(apipe(x, fn, gn))

    assert value == asyncio.run(gn(fn(x)))

    value = asyncio.run(
        apipe(
            x,
            gn,
            fn,
        )
    )

    assert value == fn(asyncio.run(gn(x)))


@given(st.integers(), st.integers(), st.integers())
def test_pipe_async_result(x: int, y: int, z: int):
    fn: Callable[[int], Result[int, str]] = lambda x: Ok(x + z)

    async def gn(x: int) -> Result[int, str]:
        return Ok(x * y)

    value = asyncio.run(
        apipe(
            Ok(x),
            result.bind(fn),
            async_result.bind(gn),
        )
    )

    assert value == Ok((x + z) * y)

    value = asyncio.run(
        apipe(
            Ok(x),
            async_result.bind(gn),
            result.bind(fn),
        )
    )

    assert value == Ok((x * y) + z)


# Runtime boundaries and inference are part of the public contract.


@pytest.mark.asyncio
async def test_apipe_initial_coroutine_and_mixed_stage_types():
    async def initial() -> int:
        return 2

    async def length(value: str) -> int:
        return len(value)

    assert_type(await apipe(initial()), int)
    assert_type(await apipe(2), int)
    value = await apipe(initial(), str, length, lambda x: x + 1)
    assert_type(value, int)
    assert value == 2


@pytest.mark.asyncio
async def test_apipe_preserves_option_and_result_values():
    for value in (Some(1), NOTHING, Ok(1), Error("failure")):
        assert await apipe(value) is value
        assert await apipe(0, lambda _: value) is value

    async def result_value(_: int) -> Result[int, str]:
        return Error("failure")

    assert await apipe(0, result_value) == Error("failure")


@pytest.mark.asyncio
async def test_apipe_long_pipeline():
    def increment(value: int) -> int:
        return value + 1

    stages: Any = [increment] * (sys.getrecursionlimit() + 100)
    assert await apipe(0, *stages) == len(stages)


@pytest.mark.asyncio
async def test_apipe_is_deferred_and_sequential():
    events: list[str] = []

    def first(value: int) -> int:
        events.append("first")
        return value + 1

    async def second(value: int) -> int:
        events.append("second started")
        await asyncio.sleep(0)
        events.append("second finished")
        return value * 2

    def third(value: int) -> int:
        events.append("third")
        return value

    operation = apipe(1, first, second, third)
    assert events == []
    assert await operation == 4
    assert events == ["first", "second started", "second finished", "third"]


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
async def test_apipe_propagates_exceptions(asynchronous: bool):
    failure = ValueError("failure")
    calls: list[int] = []

    def fail(value: int) -> int:
        raise failure

    async def async_fail(value: int) -> int:
        raise failure

    with pytest.raises(ValueError) as caught:
        await apipe(1, async_fail if asynchronous else fail, calls.append)
    assert caught.value is failure
    assert calls == []


@pytest.mark.asyncio
async def test_apipe_propagates_cancellation():
    started = asyncio.Event()
    calls: list[int] = []

    async def wait(value: int) -> int:
        started.set()
        await asyncio.Event().wait()
        return value

    task = asyncio.create_task(apipe(1, wait, calls.append))
    await started.wait()
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert calls == []


@pytest.mark.asyncio
async def test_apipe_passes_futures_through_and_wrapper_awaits_them():
    future: asyncio.Future[int] = asyncio.get_running_loop().create_future()
    future.set_result(42)
    assert await apipe(future) is future
    assert await apipe(0, lambda _: future) is future

    async def resolve(value: asyncio.Future[int]) -> int:
        return await value

    assert await apipe(future, resolve) == 42


@pytest.mark.asyncio
async def test_pipe_still_passes_coroutines_to_task_scheduler():
    async def increment(value: int) -> int:
        return value + 1

    task = pipe(1, increment, asyncio.create_task)
    assert isinstance(task, asyncio.Task)
    assert await task == 2


@pytest.mark.asyncio
async def test_async_result_bind_preserves_error_and_skips_mapper():
    calls: list[int] = []

    async def mapper(value: int) -> Result[str, str]:
        calls.append(value)
        return Error("mapper failed")

    bind = async_result.bind(mapper)
    result_value = await bind(Error("initial failure"))
    assert_type(result_value, Result[str, str])
    assert result_value == Error("initial failure")
    assert calls == []
    assert await bind(Ok(1)) == Error("mapper failed")
    assert calls == [1]


@pytest.mark.asyncio
async def test_async_result_bind_accepts_future_mapper():
    def mapper(value: int) -> asyncio.Future[Result[str, str]]:
        future: asyncio.Future[Result[str, str]] = asyncio.get_running_loop().create_future()
        future.set_result(Ok(str(value)))
        return future

    assert await apipe(Ok(42), async_result.bind(mapper)) == Ok("42")
