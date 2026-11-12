import asyncio

import pytest
from hypothesis import given  # type: ignore
from hypothesis import strategies as st

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
