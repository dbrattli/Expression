import asyncio
from inspect import Signature, signature, unwrap
from typing import assert_type, cast

import pytest

from expression import Error, Nothing, Ok, Result, effect
from expression.effect import ResultScope


@pytest.mark.asyncio
async def test_async_result_scope_binds_awaited_values_and_final_type():
    async def fetch(number: int) -> Result[int, str]:
        await asyncio.sleep(0)
        return Ok(number) if number > 0 else Error("missing")

    @effect.async_result
    async def computation(scope: ResultScope[str], number: int) -> str:
        value = scope.bind(await fetch(number))
        assert_type(value, int)
        text = scope.bind(Ok(str(value)))
        assert_type(text, str)
        return text + "!"

    assert_type(await computation(42), Result[str, str])
    assert await computation(42) == Ok("42!")
    assert await computation(0) == Error("missing")
    assert tuple(signature(computation).parameters) == ("number",)
    assert signature(computation).return_annotation is Signature.empty
    assert computation.__annotations__ == {"number": int}
    assert signature(unwrap(computation)).return_annotation is str


@pytest.mark.asyncio
async def test_async_result_none_is_a_successful_payload():
    @effect.async_result
    async def computation(scope: ResultScope[str]) -> None:
        return scope.bind(Ok(None))

    assert_type(await computation(), Result[None, str])
    assert await computation() == Ok(None)


@pytest.mark.asyncio
async def test_async_result_failure_runs_cleanup():
    trace: list[str] = []
    failure = Error("missing")

    @effect.async_result
    async def computation(scope: ResultScope[str]) -> int:
        try:
            scope.bind(failure)
            trace.append("unreachable")
            return 42
        finally:
            await asyncio.sleep(0)
            trace.append("cleanup")

    assert await computation() is failure
    assert trace == ["cleanup"]


@pytest.mark.asyncio
async def test_async_result_caught_failure_is_terminal():
    @effect.async_result
    async def computation(scope: ResultScope[str]) -> int:
        try:
            scope.bind(Error("first"))
        except BaseException:
            pass
        return 42

    assert await computation() == Error("first")


@pytest.mark.asyncio
async def test_async_result_cancellation_propagates_and_closes_scope():
    ready = asyncio.Event()
    blocked = asyncio.Event()
    captured: list[ResultScope[str]] = []
    trace: list[str] = []

    @effect.async_result
    async def computation(scope: ResultScope[str]) -> int:
        captured.append(scope)
        ready.set()
        try:
            await blocked.wait()
            return scope.bind(Ok(42))
        finally:
            trace.append("cleanup")

    task = asyncio.create_task(computation())
    assert_type(task, asyncio.Task[Result[int, str]])
    await ready.wait()
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert trace == ["cleanup"]
    with pytest.raises(RuntimeError, match="no longer active"):
        captured[0].bind(Ok(1))


@pytest.mark.asyncio
async def test_async_result_scope_rejects_another_task():
    @effect.async_result
    async def computation(scope: ResultScope[str]) -> int:
        async def misuse() -> int:
            return scope.bind(Ok(42))

        with pytest.raises(RuntimeError, match="another execution context"):
            await asyncio.create_task(misuse())
        return scope.bind(Ok(1))

    assert await computation() == Ok(1)


@pytest.mark.asyncio
async def test_async_result_calls_have_independent_scopes():
    @effect.async_result
    async def computation(scope: ResultScope[str], number: int) -> int:
        await asyncio.sleep(0)
        return scope.bind(Ok(number) if number > 0 else Error("missing"))

    assert await asyncio.gather(computation(1), computation(0), computation(2)) == [Ok(1), Error("missing"), Ok(2)]


@pytest.mark.asyncio
async def test_nested_async_scopes_preserve_outer_signal_ownership():
    trace: list[str] = []

    @effect.async_result
    async def outer(scope: ResultScope[str]) -> int:
        @effect.async_result
        async def inner(inner_scope: ResultScope[int]) -> int:
            inner_scope.bind(Ok(1))
            return scope.bind(Error("outer"))

        await inner()
        trace.append("unreachable")
        return 42

    assert await outer() == Error("outer")
    assert trace == []


@pytest.mark.asyncio
async def test_async_result_unexpected_exception_propagates():
    @effect.async_result
    async def computation(scope: ResultScope[str]) -> int:
        scope.bind(Ok(1))
        raise ValueError("unexpected")

    with pytest.raises(ValueError, match="unexpected"):
        await computation()


@pytest.mark.asyncio
async def test_async_result_rejects_wrong_family():
    @effect.async_result
    async def computation(scope: ResultScope[str]) -> int:
        return scope.bind(cast(Result[int, str], Nothing()))

    with pytest.raises(TypeError, match="Ok or Error"):
        await computation()


@pytest.mark.asyncio
async def test_async_result_callback_supports_bound_methods():
    class Service:
        async def compute(self, scope: ResultScope[str]) -> str:
            await asyncio.sleep(0)
            return str(scope.bind(Ok(42)))

    assert await effect.async_run_result(Service().compute) == Ok("42")


@pytest.mark.asyncio
async def test_async_try_scope_uses_explicit_exception_errors():
    failure = ValueError("expected")

    @effect.async_try
    async def computation(scope: ResultScope[Exception], fail: bool) -> int:
        if fail:
            scope.bind(Error(failure))
        return scope.bind(Ok(42))

    task = asyncio.create_task(computation(False))
    assert_type(task, asyncio.Task[Result[int, Exception]])
    assert_type(await task, Result[int, Exception])
    assert await computation(False) == Ok(42)
    assert await computation(True) == Error(failure)


def test_async_result_coroutine_supports_asyncio_run():
    @effect.async_result
    async def computation(scope: ResultScope[str], number: int) -> str:
        return str(scope.bind(Ok(number)))

    result = asyncio.run(computation(42))
    assert_type(result, Result[str, str])
    assert result == Ok("42")


def test_async_try_coroutine_supports_asyncio_run():
    @effect.async_try
    async def computation(scope: ResultScope[Exception], number: int) -> str:
        return str(scope.bind(Ok(number)))

    result = asyncio.run(computation(42))
    assert_type(result, Result[str, Exception])
    assert result == Ok("42")
