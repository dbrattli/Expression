import pytest
from hypothesis import given
from hypothesis import strategies as st

from expression.collections.asyncseq import AsyncSeq

# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio


async def test_asyncseq_empty():
    xs = AsyncSeq.empty()
    async for _ in xs:
        assert False


@given(st.integers(min_value=0, max_value=100))  # type: ignore
async def test_asyncseq_range(count: int):
    xs = AsyncSeq.range(count)
    acc = 0
    async for x in xs:
        acc += x

    assert acc == sum(range(count))


@given(st.integers(min_value=0, max_value=100))  # type: ignore
async def test_asyncseq_map(count: int):
    xs = AsyncSeq.range(count)
    acc = 0
    async for x in xs:
        acc += x

    assert acc == sum(range(count))
