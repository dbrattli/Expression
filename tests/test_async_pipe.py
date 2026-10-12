from collections.abc import Callable
import asyncio

from hypothesis import given
from hypothesis import strategies as st

from expression.extra.pipe import async_pipe
from expression.extra import async_result
from expression import Result, Ok, result


@given(st.integers())
def test_pipe_id(x: int):
    value = asyncio.run(async_pipe(x))
    assert value == x


@given(st.integers())
def test_pipe_awaitable_only(x: int):
    async def awaitable_value() -> int:
        return x

    value = asyncio.run(async_pipe(awaitable_value()))
    assert value == x


@given(st.integers())
def test_pipe_fn(x: int):
    async def gn(x: int) -> int:
        return x + 1

    value = asyncio.run(async_pipe(x, gn))
    assert value == asyncio.run(gn(x))


@given(st.integers(), st.integers(), st.integers())
def test_pipe_fn_gn(x: int, y: int, z: int):
    fn: Callable[[int], int] = lambda x: x + z

    async def gn(x: int) -> int:
        return x * y

    value = asyncio.run(async_pipe(x, fn, gn))

    assert value == asyncio.run(gn(fn(x)))

    value = asyncio.run(
        async_pipe(
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
        async_pipe(
            Ok(x),
            result.bind(fn),
            async_result.bind(gn),
        )
    )

    assert value == Ok((x + z) * y)

    value = asyncio.run(
        async_pipe(
            Ok(x),
            async_result.bind(gn),
            result.bind(fn),
        )
    )

    assert value == Ok((x * y) + z)
