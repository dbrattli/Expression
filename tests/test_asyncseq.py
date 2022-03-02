import asyncio

import pytest
from hypothesis import given
from hypothesis import strategies as st

from expression.collections.asyncseq import AsyncSeq


@pytest.mark.asyncio
async def test_asyncseq_empty():
    xs = AsyncSeq.empty()
    async for _ in xs:
        assert False


@given(st.integers(min_value=0, max_value=100))  # type: ignore
def test_asyncseq_range(count: int):
    acc = 0

    async def runner():
        nonlocal acc

        xs = AsyncSeq.range(count)
        async for x in xs:
            acc += x

    asyncio.run(runner())
    assert acc == sum(range(count))


@given(st.integers(min_value=0, max_value=100))  # type: ignore
def test_asyncseq_map(count: int):
    acc = 0

    async def runner():
        nonlocal acc
        xs = AsyncSeq.range(count)
        async for x in xs:
            acc += x

    asyncio.run(runner())
    assert acc == sum(range(count))
