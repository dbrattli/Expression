import asyncio
from inspect import Signature, signature, unwrap
from typing import assert_type, cast

import pytest

from expression import Nothing, Ok, Option, Some, effect
from expression.effect import OptionScope


@pytest.mark.asyncio
async def test_async_option_scope_binds_awaited_values_and_final_type():
    async def fetch(number: int) -> Option[int]:
        await asyncio.sleep(0)
        return Some(number) if number > 0 else Nothing()

    @effect.async_option
    async def computation(scope: OptionScope, number: int) -> str:
        value = scope.bind(await fetch(number))
        assert_type(value, int)
        return str(value)

    assert_type(await computation(42), Option[str])
    assert await computation(42) == Some("42")
    assert await computation(0) is Nothing()
    assert tuple(signature(computation).parameters) == ("number",)
    assert signature(computation).return_annotation is Signature.empty
    assert computation.__annotations__ == {"number": int}
    assert signature(unwrap(computation)).return_annotation is str


@pytest.mark.asyncio
async def test_async_option_none_is_a_successful_payload():
    @effect.async_option
    async def computation(scope: OptionScope) -> None:
        return scope.bind(Some(None))

    assert_type(await computation(), Option[None])
    assert await computation() == Some(None)


@pytest.mark.asyncio
async def test_async_option_failure_runs_cleanup():
    trace: list[str] = []

    @effect.async_option
    async def computation(scope: OptionScope) -> int:
        try:
            scope.bind(Nothing())
            trace.append("unreachable")
            return 42
        finally:
            await asyncio.sleep(0)
            trace.append("cleanup")

    assert await computation() is Nothing()
    assert trace == ["cleanup"]


@pytest.mark.asyncio
async def test_async_option_caught_failure_is_terminal():
    @effect.async_option
    async def computation(scope: OptionScope) -> int:
        try:
            scope.bind(Nothing())
        except BaseException:
            pass
        return 42

    assert await computation() is Nothing()


@pytest.mark.asyncio
async def test_async_option_cancellation_propagates_and_closes_scope():
    ready = asyncio.Event()
    blocked = asyncio.Event()
    captured: list[OptionScope] = []
    trace: list[str] = []

    @effect.async_option
    async def computation(scope: OptionScope) -> int:
        captured.append(scope)
        ready.set()
        try:
            await blocked.wait()
            return scope.bind(Some(42))
        finally:
            trace.append("cleanup")

    task = asyncio.create_task(computation())
    assert_type(task, asyncio.Task[Option[int]])
    await ready.wait()
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert trace == ["cleanup"]
    with pytest.raises(RuntimeError, match="no longer active"):
        captured[0].bind(Some(1))


@pytest.mark.asyncio
async def test_async_option_scope_rejects_another_task():
    @effect.async_option
    async def computation(scope: OptionScope) -> int:
        async def misuse() -> int:
            return scope.bind(Some(42))

        with pytest.raises(RuntimeError, match="another execution context"):
            await asyncio.create_task(misuse())
        return scope.bind(Some(1))

    assert await computation() == Some(1)


@pytest.mark.asyncio
async def test_async_option_calls_have_independent_scopes():
    @effect.async_option
    async def computation(scope: OptionScope, number: int) -> int:
        await asyncio.sleep(0)
        return scope.bind(Some(number) if number > 0 else Nothing())

    assert await asyncio.gather(computation(1), computation(0), computation(2)) == [Some(1), Nothing(), Some(2)]


@pytest.mark.asyncio
async def test_async_option_unexpected_exception_propagates():
    @effect.async_option
    async def computation(scope: OptionScope) -> int:
        scope.bind(Some(1))
        raise ValueError("unexpected")

    with pytest.raises(ValueError, match="unexpected"):
        await computation()


@pytest.mark.asyncio
async def test_async_option_rejects_wrong_family():
    @effect.async_option
    async def computation(scope: OptionScope) -> int:
        return scope.bind(cast(Option[int], Ok(42)))

    with pytest.raises(TypeError, match="Some or Nothing"):
        await computation()


@pytest.mark.asyncio
async def test_async_option_callback_supports_bound_methods():
    class Service:
        async def compute(self, scope: OptionScope) -> str:
            await asyncio.sleep(0)
            return str(scope.bind(Some(42)))

    assert await effect.async_run_option(Service().compute) == Some("42")


def test_async_option_coroutine_supports_asyncio_run():
    @effect.async_option
    async def computation(scope: OptionScope, number: int) -> str:
        return str(scope.bind(Some(number)))

    result = asyncio.run(computation(42))
    assert_type(result, Option[str])
    assert result == Some("42")
