import asyncio
from collections.abc import AsyncIterable, AsyncIterator, Awaitable, Iterable
from typing import assert_type

import pytest
from hypothesis import given  # type: ignore
from hypothesis import strategies as st

from expression import pipe
from expression.collections import asyncseq
from expression.collections.asyncseq import AsyncSeq


@pytest.mark.asyncio
async def test_asyncseq_empty():
    xs = AsyncSeq.empty()
    async for _ in xs:
        assert False


@given(st.integers(min_value=0, max_value=100))
def test_asyncseq_range(count: int):
    acc = 0

    async def runner():
        nonlocal acc

        xs = AsyncSeq.range(count)
        async for x in xs:
            acc += x

    asyncio.run(runner())
    assert acc == sum(range(count))


@given(st.integers(min_value=0, max_value=100))
def test_asyncseq_map(count: int):
    acc = 0

    async def runner():
        nonlocal acc
        xs = AsyncSeq.range(count)
        async for x in xs:
            acc += x

    asyncio.run(runner())
    assert acc == sum(range(count))


@pytest.mark.asyncio
@pytest.mark.parametrize("count", [0, 1, 3, 4])
async def test_asyncseq_take_preserves_remaining_items(count: int):
    source = AsyncSeq.range(3)
    taken = [value async for value in await source.take(count)]
    remaining = [value async for value in source]
    assert taken == list(range(min(count, 3)))
    assert remaining == list(range(min(count, 3), 3))


@pytest.mark.asyncio
@pytest.mark.parametrize("count", [0, 1])
async def test_asyncseq_take_does_not_request_another_item(count: int):
    async def source():
        for value in range(count):
            yield value
        raise AssertionError("Requested an item beyond the take limit")

    assert [value async for value in await AsyncSeq(source()).take(count)] == list(range(count))


@pytest.mark.asyncio
@pytest.mark.parametrize("async_source", [False, True])
@pytest.mark.parametrize("count", [0, 3])
async def test_amap_pipe_preserves_nested_results(async_source: bool, count: int):
    async def enrich(value: int) -> list[str]:
        await asyncio.sleep(0)
        return [str(value), str(value * 2)]

    source = asyncseq.range(count) if async_source else range(count)
    stream = pipe(source, asyncseq.amap(enrich), asyncseq.map(tuple))
    assert [item async for item in stream] == [(str(value), str(value * 2)) for value in range(count)]


@pytest.mark.asyncio
async def test_amap_fluent_and_awaitable_callback():
    def enrich(value: int) -> Awaitable[str]:
        future: asyncio.Future[str] = asyncio.get_running_loop().create_future()
        future.set_result(str(value))
        return future

    stream = AsyncSeq.range(3).amap(enrich)
    assert_type(stream, AsyncSeq[str])
    assert_type(asyncseq.amap(enrich)([1, 2]), AsyncIterable[str])
    assert_type(pipe(asyncseq.range(3), asyncseq.amap(enrich)), AsyncIterable[str])
    assert [item async for item in stream] == ["0", "1", "2"]


@pytest.mark.asyncio
@pytest.mark.parametrize("async_source", [False, True])
async def test_amap_is_lazy_and_sequential(async_source: bool):
    events: list[tuple[str, int]] = []
    started = asyncio.Event()
    release = asyncio.Event()

    def source() -> Iterable[int]:
        for value in range(3):
            events.append(("source", value))
            yield value

    async def asource() -> AsyncIterator[int]:
        for value in source():
            yield value

    async def enrich(value: int) -> int:
        events.append(("start", value))
        started.set()
        await release.wait()
        events.append(("end", value))
        return value * 2

    stream = asyncseq.amap(enrich)(asource() if async_source else source())
    assert events == []
    iterator = aiter(stream)

    async def next_item() -> int:
        return await anext(iterator)

    task = asyncio.create_task(next_item())
    try:
        await asyncio.wait_for(started.wait(), timeout=5)
        assert events == [("source", 0), ("start", 0)]
        release.set()
        assert await asyncio.wait_for(task, timeout=5) == 0
        assert events == [("source", 0), ("start", 0), ("end", 0)]
        assert [item async for item in iterator] == [2, 4]
        assert events == [(event, value) for value in range(3) for event in ("source", "start", "end")]
    finally:
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)


@pytest.mark.asyncio
@pytest.mark.parametrize("async_source", [False, True])
async def test_amap_propagates_mapper_failure(async_source: bool):
    visited: list[int] = []
    failure = ValueError("mapper failed")

    async def enrich(value: int) -> int:
        visited.append(value)
        if value == 1:
            raise failure
        return value

    source = asyncseq.range(3) if async_source else range(3)
    iterator = aiter(asyncseq.amap(enrich)(source))
    assert await anext(iterator) == 0
    with pytest.raises(ValueError) as error:
        await anext(iterator)
    assert error.value is failure
    assert visited == [0, 1]
    with pytest.raises(StopAsyncIteration):
        await anext(iterator)


@pytest.mark.asyncio
@pytest.mark.parametrize("async_source", [False, True])
async def test_amap_propagates_source_failure(async_source: bool):
    def source() -> Iterable[int]:
        yield 1
        raise ValueError("source failed")

    async def asource() -> AsyncIterator[int]:
        for value in source():
            yield value

    async def enrich(value: int) -> int:
        return value * 2

    iterator = aiter(asyncseq.amap(enrich)(asource() if async_source else source()))
    assert await anext(iterator) == 2
    with pytest.raises(ValueError, match="source failed"):
        await anext(iterator)


@pytest.mark.asyncio
@pytest.mark.parametrize("async_source", [False, True])
async def test_amap_cancellation_stops_mapping(async_source: bool):
    started = asyncio.Event()
    cancelled = asyncio.Event()
    visited: list[int] = []

    async def enrich(value: int) -> int:
        visited.append(value)
        started.set()
        try:
            await asyncio.Event().wait()
        finally:
            cancelled.set()
        return value

    source = asyncseq.range(3) if async_source else range(3)
    iterator = aiter(asyncseq.amap(enrich)(source))

    async def next_item() -> int:
        return await anext(iterator)

    task = asyncio.create_task(next_item())
    try:
        await asyncio.wait_for(started.wait(), timeout=5)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert cancelled.is_set()
        assert visited == [0]
        with pytest.raises(StopAsyncIteration):
            await anext(iterator)
    finally:
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)
