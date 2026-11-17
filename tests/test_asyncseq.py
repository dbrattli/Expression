import asyncio
from collections.abc import AsyncIterable, AsyncIterator, Awaitable, Callable, Iterable
from typing import assert_type

import pytest
from hypothesis import given  # type: ignore
from hypothesis import strategies as st

from expression import NOTHING, Option, Some, pipe
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
        xs = AsyncSeq.range(count).map(lambda value: value * 2)
        async for x in xs:
            acc += x

    asyncio.run(runner())
    assert acc == 2 * sum(range(count))


@pytest.mark.asyncio
@pytest.mark.parametrize("count", [0, 1, 3, 4])
async def test_asyncseq_take_preserves_remaining_items(count: int):
    source = AsyncSeq.range(3)
    taken = [value async for value in source.take(count)]
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

    assert [value async for value in AsyncSeq(source()).take(count)] == list(range(count))


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


@pytest.mark.asyncio
@pytest.mark.parametrize("async_source", [False, True])
@pytest.mark.parametrize("count", [0, 4])
async def test_async_callback_operations(async_source: bool, count: int):
    def source() -> Iterable[int] | AsyncIterable[int]:
        return asyncseq.range(count) if async_source else range(count)

    async def predicate(value: int) -> bool:
        await asyncio.sleep(0)
        return value % 2 == 0

    async def chooser(value: int) -> Option[str]:
        return Some(str(value)) if value % 2 == 0 else NOTHING

    async def folder(state: str, value: int) -> str:
        await asyncio.sleep(0)
        return state + str(value)

    async def back_folder(value: int, state: str) -> str:
        return state + str(value)

    expected = list(range(0, count, 2))
    assert [x async for x in pipe(source(), asyncseq.afilter(predicate))] == expected
    assert [x async for x in AsyncSeq.range(count).afilter(predicate)] == expected
    assert [x async for x in pipe(source(), asyncseq.achoose(chooser))] == list(map(str, expected))
    assert [x async for x in AsyncSeq.range(count).achoose(chooser)] == list(map(str, expected))
    state = "".join(map(str, range(count)))
    assert await pipe(source(), asyncseq.afold(folder, "")) == state
    assert await AsyncSeq.range(count).afold(folder, "") == state
    assert await pipe(source(), asyncseq.afold_back(back_folder, "")) == state[::-1]
    assert await AsyncSeq.range(count).afold_back(back_folder, "") == state[::-1]
    states = [state[:i] for i in range(count + 1)]
    assert [x async for x in pipe(source(), asyncseq.ascan(folder, ""))] == states
    assert [x async for x in AsyncSeq.range(count).ascan(folder, "")] == states
    assert_type(AsyncSeq.range(count).achoose(chooser), AsyncSeq[str])
    assert_type(AsyncSeq.range(count).afilter(predicate), AsyncSeq[int])
    assert_type(AsyncSeq.range(count).ascan(folder, ""), AsyncSeq[str])
    assert_type(await AsyncSeq.range(count).afold(folder, ""), str)
    assert_type(await AsyncSeq.range(count).afold_back(back_folder, ""), str)


@pytest.mark.asyncio
@pytest.mark.parametrize("async_source", [False, True])
@pytest.mark.parametrize("async_inner", [False, True])
async def test_acollect_flattens_in_order(async_source: bool, async_inner: bool):
    visited: list[int] = []

    async def mapping(value: int) -> Iterable[str] | AsyncIterable[str]:
        visited.append(value)

        async def inner() -> AsyncIterator[str]:
            for i in range(value):
                yield str(i)

        return inner() if async_inner else [str(i) for i in range(value)]

    source = asyncseq.range(4) if async_source else range(4)
    stream = pipe(source, asyncseq.acollect(mapping))
    assert_type(stream, AsyncIterable[str])
    assert visited == []
    iterator = aiter(stream)
    assert await anext(iterator) == "0"
    assert visited == [0, 1]
    assert [x async for x in iterator] == ["0", "1", "0", "1", "2"]
    assert visited == [0, 1, 2, 3]
    fluent = AsyncSeq.range(4).acollect(mapping)
    assert_type(fluent, AsyncSeq[str])
    assert [x async for x in fluent] == ["0", "0", "1", "0", "1", "2"]


@pytest.mark.asyncio
async def test_ascan_initial_state_does_not_touch_source():
    async def source() -> AsyncIterator[int]:
        raise AssertionError("Source should not be advanced")
        yield 0

    async def scanner(state: int, value: int) -> int:
        raise AssertionError("Scanner should not be called")

    iterator = aiter(asyncseq.ascan(scanner, 42)(source()))
    assert await anext(iterator) == 42


async def _consume_callback_operation(
    operation: str, source: Iterable[int] | AsyncIterable[int], callback: Callable[[int], Awaitable[int]]
) -> list[int]:
    async def predicate(value: int) -> bool:
        return bool(await callback(value))

    async def chooser(value: int) -> Option[int]:
        return Some(await callback(value))

    async def mapping(value: int) -> Iterable[int]:
        return [await callback(value)]

    async def folder(state: int, value: int) -> int:
        return state + await callback(value)

    async def back_folder(value: int, state: int) -> int:
        return state + await callback(value)

    if operation == "afold":
        return [await asyncseq.afold(folder, 0)(source)]
    if operation == "afold_back":
        return [await asyncseq.afold_back(back_folder, 0)(source)]
    if operation == "afilter":
        stream = asyncseq.afilter(predicate)(source)
    elif operation == "achoose":
        stream = asyncseq.achoose(chooser)(source)
    elif operation == "acollect":
        stream = asyncseq.acollect(mapping)(source)
    else:
        stream = asyncseq.ascan(folder, 0)(source)
    return [value async for value in stream]


_CALLBACK_OPERATIONS = ["afilter", "achoose", "acollect", "afold", "afold_back", "ascan"]


@pytest.mark.asyncio
@pytest.mark.parametrize("operation", _CALLBACK_OPERATIONS)
@pytest.mark.parametrize("async_source", [False, True])
async def test_async_operations_propagate_callback_failures(operation: str, async_source: bool):
    visited: list[int] = []
    failure = ValueError("callback failed")

    async def callback(value: int) -> int:
        visited.append(value)
        raise failure

    source = asyncseq.range(3) if async_source else range(3)
    with pytest.raises(ValueError) as error:
        await _consume_callback_operation(operation, source, callback)
    assert error.value is failure
    assert visited == ([2] if operation == "afold_back" else [0])


@pytest.mark.asyncio
@pytest.mark.parametrize("operation", _CALLBACK_OPERATIONS)
@pytest.mark.parametrize("async_source", [False, True])
async def test_async_operations_cancel_pending_callback(operation: str, async_source: bool):
    started = asyncio.Event()
    finished = asyncio.Event()
    visited: list[int] = []

    async def callback(value: int) -> int:
        visited.append(value)
        started.set()
        try:
            await asyncio.Event().wait()
        finally:
            finished.set()
        return value

    source = asyncseq.range(3) if async_source else range(3)
    task = asyncio.create_task(_consume_callback_operation(operation, source, callback))
    try:
        await asyncio.wait_for(started.wait(), timeout=5)
        assert visited == ([2] if operation == "afold_back" else [0])
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert finished.is_set()
        assert len(visited) == 1
    finally:
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)


@pytest.mark.asyncio
@pytest.mark.parametrize("operation", _CALLBACK_OPERATIONS)
async def test_async_operations_propagate_source_failure(operation: str):
    async def source() -> AsyncIterator[int]:
        raise ValueError("source failed")
        yield 0

    async def callback(value: int) -> int:
        raise AssertionError("Callback should not run")

    with pytest.raises(ValueError, match="source failed"):
        await _consume_callback_operation(operation, source(), callback)


@pytest.mark.asyncio
async def test_sync_transformations_chain_lazily_with_async_callbacks():
    events: list[int] = []

    async def source() -> AsyncIterator[int]:
        for value in range(6):
            events.append(value)
            yield value

    async def enrich(value: int) -> int:
        return value * 10

    stream = (
        AsyncSeq(source())
        .map(lambda value: value + 1)
        .filter(lambda value: value % 2 == 0)
        .choose(lambda value: Some(value) if value < 6 else NOTHING)
        .collect(lambda value: AsyncSeq.range(value, value + 2))
        .skip(1)
        .tail()
        .scan(lambda state, value: state + value, 0)
        .amap(enrich)
        .take(3)
    )
    assert_type(stream, AsyncSeq[int])
    assert events == []
    assert [value async for value in stream] == [0, 40, 90]
    assert events == [0, 1, 2, 3]


@pytest.mark.asyncio
async def test_concat_returns_chainable_lazy_sequence():
    events: list[str] = []

    async def inner() -> AsyncIterator[int]:
        events.append("inner")
        yield 2
        yield 3

    async def outer() -> AsyncIterator[AsyncIterable[int]]:
        events.append("outer")
        yield AsyncSeq.empty()
        yield inner()

    stream = AsyncSeq(outer()).concat()
    assert_type(stream, AsyncSeq[int])
    assert events == []
    assert await stream.map(lambda value: value * 2).sum() == 10
    assert events == ["outer", "inner"]


@pytest.mark.asyncio
async def test_scan_initial_state_is_lazy_and_chainable():
    async def source() -> AsyncIterator[int]:
        raise AssertionError("Source must not be advanced")
        yield 0

    stream = AsyncSeq(source()).scan(lambda state, value: state + value, 42)
    assert_type(stream, AsyncSeq[int])
    assert await stream.take(1).head() == 42
    assert [value async for value in AsyncSeq.range(0).scan(lambda state, value: state + value, 42)] == [42]


@pytest.mark.asyncio
@pytest.mark.parametrize("count", [-1, 0, 2, 5])
async def test_skip_and_tail_preserve_values(count: int):
    stream = AsyncSeq.range(4).skip(count)
    assert_type(stream, AsyncSeq[int])
    assert [value async for value in stream] == list(range(4))[max(count, 0) :]
    assert [value async for value in AsyncSeq.range(count).tail()] == list(range(count))[1:]


@pytest.mark.asyncio
async def test_fluent_sync_transformations_match_functional_api():
    def mapper(value: int) -> int:
        return value * 2

    def predicate(value: int) -> bool:
        return value % 3 != 0

    def chooser(value: int) -> Option[int]:
        return Some(value) if value < 7 else NOTHING

    def mapping(value: int) -> AsyncIterable[int]:
        return AsyncSeq.range(value, value + 2)

    fluent = AsyncSeq.range(5).map(mapper).filter(predicate).choose(chooser).collect(mapping)
    functional = pipe(
        asyncseq.range(5),
        asyncseq.map(mapper),
        asyncseq.filter(predicate),
        asyncseq.choose(chooser),
        asyncseq.collect(mapping),
    )
    assert_type(fluent, AsyncSeq[int])
    assert [value async for value in fluent] == [value async for value in functional]


@pytest.mark.asyncio
async def test_sync_mapper_failure_is_deferred_until_consumption():
    def fail(value: int) -> int:
        raise ValueError("mapper failed")

    stream = AsyncSeq.range(1).map(fail).filter(lambda value: True)
    with pytest.raises(ValueError, match="mapper failed"):
        await stream.head()


@pytest.mark.asyncio
async def test_terminal_operations_remain_awaitable_after_transformations():
    def source() -> AsyncSeq[int]:
        return AsyncSeq.range(4).map(lambda value: value + 1)

    assert await source().fold(lambda state, value: state + str(value), "") == "1234"
    assert await source().fold_back(lambda value, state: state + str(value), "") == "4321"
    assert await source().head() == 1
    assert await source().length() == 4
    assert await source().sum() == 10
    assert await source().min() == 1
    assert await source().max() == 4
    assert await source().take(0).fold(lambda state, value: state + value, 42) == 42
    with pytest.raises(ValueError, match="Sequence contains no elements"):
        await source().take(0).head()
