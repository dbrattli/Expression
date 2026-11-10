"""Runtime boundaries of a synchronous, next-only generator runner."""

from collections.abc import Generator
from typing import cast

import pytest

from expression import NOTHING, Error, Ok, Option, Result, Some
from investigations.typed_generators import adapter as gen
from investigations.typed_generators.positive import optional_workflow, workflow


def test_independent_payloads_parameters_and_failure():
    assert workflow(Ok(42)) == Ok(True)
    assert workflow(Ok(42), suffix="?") == Ok(False)
    failure = Error("failed")
    assert workflow(failure) is failure
    assert optional_workflow(Some(42)) == Some("42")
    assert optional_workflow(NOTHING) is NOTHING


def test_error_short_circuit_runs_delegated_and_outer_cleanup():
    trace: list[str] = []
    failure = Error("failed")

    def step() -> gen.ResultComputation[int, str]:
        try:
            yield from gen.bind(failure)
            trace.append("unreachable step")
            return 1
        finally:
            trace.append("step cleanup")

    @gen.result
    def computation() -> gen.ResultComputation[int, str]:
        try:
            trace.append("start")
            yield from gen.bind(Ok(42))
            value = yield from step()
            trace.append("unreachable body")
            return value
        finally:
            trace.append("outer cleanup")

    assert computation() is failure
    assert trace == ["start", "step cleanup", "outer cleanup"]


def test_option_short_circuit_and_cleanup():
    trace: list[str] = []

    @gen.option
    def computation() -> gen.OptionComputation[int]:
        try:
            yield from gen.bind(Some(42))
            yield from gen.bind(NOTHING)
            trace.append("unreachable")
            return 1
        finally:
            trace.append("cleanup")

    assert computation() is NOTHING
    assert trace == ["cleanup"]


@pytest.mark.parametrize("value", [Ok(42), Error("inner")])
def test_returned_result_is_not_flattened(value: Result[int, str]):
    @gen.result
    def computation() -> gen.ResultComputation[Result[int, str], str]:
        yield from gen.bind(Ok(1))
        return value

    actual = computation()
    assert isinstance(actual, Ok)
    assert actual.ok is value


@pytest.mark.parametrize("value", [Some(42), NOTHING])
def test_returned_option_is_not_flattened(value: Option[int]):
    @gen.option
    def computation() -> gen.OptionComputation[Option[int]]:
        return (yield from gen.bind(Some(value)))

    actual = computation()
    assert isinstance(actual, Some)
    assert actual.some is value


def test_final_none_and_empty_generator_are_successful():
    @gen.result
    def computation() -> gen.ResultComputation[None, str]:
        yield from gen.bind(Ok(42))
        return None

    @gen.option
    def empty() -> gen.OptionComputation[None]:
        yield from ()

    assert computation() == Ok(None)
    assert empty() == Some(None)


def test_loops_and_nested_decorated_computations():
    @gen.result
    def step(number: int) -> gen.ResultComputation[int, str]:
        value = yield from gen.bind(Ok(number))
        return value + 1

    @gen.result
    def computation() -> gen.ResultComputation[int, str]:
        total = 0
        for number in range(3):
            total += yield from gen.bind(step(number))
        return total

    assert computation() == Ok(6)


def test_original_exception_propagates_with_cleanup():
    error = RuntimeError("unexpected")
    trace: list[str] = []

    @gen.result
    def computation() -> gen.ResultComputation[int, str]:
        try:
            yield from gen.bind(Ok(42))
            raise error
        finally:
            trace.append("cleanup")

    with pytest.raises(RuntimeError) as caught:
        computation()
    assert caught.value is error
    assert trace == ["cleanup"]


def test_catching_generator_exit_cannot_replace_error_with_success():
    failure = Error("failed")

    @gen.result
    def computation() -> gen.ResultComputation[int, str]:
        try:
            yield from gen.bind(failure)
        except BaseException:
            return 42
        return 0

    assert computation() is failure


def test_cleanup_exception_propagates_instead_of_being_silenced():
    @gen.option
    def computation() -> gen.OptionComputation[int]:
        try:
            yield from gen.bind(NOTHING)
        finally:
            raise ValueError("cleanup")

    with pytest.raises(ValueError, match="cleanup"):
        computation()


def test_yielding_during_failure_cleanup_is_rejected():
    @gen.result
    def computation() -> gen.ResultComputation[int, str]:
        try:
            yield from gen.bind(Error("failed"))
        finally:
            yield Ok(1)
        return 42

    with pytest.raises(RuntimeError, match="ignored GeneratorExit"):
        computation()


def test_runtime_rejects_wrong_family_and_closes_generator():
    trace: list[str] = []

    @gen.result
    def computation() -> gen.ResultComputation[int, str]:
        try:
            yield cast(Result[int, str], Some(42))
            return 1
        finally:
            trace.append("cleanup")

    with pytest.raises(TypeError, match="Ok or Error"):
        computation()
    assert trace == ["cleanup"]


def test_failed_adapter_cannot_be_resumed_manually():
    step = gen.bind(Error("failed"))
    assert next(step) == Error("failed")
    with pytest.raises(RuntimeError, match="must not be resumed"):
        next(step)


def test_plain_yield_discards_payload_and_final_return_wins():
    @gen.result
    def computation() -> gen.ResultComputation[int, str]:
        assert (yield Ok(42)) is None
        yield Ok(43)
        return 44

    assert computation() == Ok(44)


def test_decorated_bound_method():
    class Service:
        def __init__(self, value: int):
            self.value = value

        @gen.option
        def run(self, suffix: str) -> gen.OptionComputation[str]:
            value = yield from gen.bind(Some(self.value))
            return str(value) + suffix

    assert Service(42).run("!") == Some("42!")


def test_captured_generator_can_escape_and_be_driven_manually():
    # Unlike a scope, the protocol itself has no invocation ownership guard.
    captured: list[Generator[Ok[object], None, int]] = []

    @gen.result
    def computation() -> gen.ResultComputation[int, str]:
        step = gen.bind(Ok(42))
        captured.append(step)
        yield Ok(1)
        return 0

    assert computation() == Ok(0)
    assert next(captured[0]) == Ok(42)
    with pytest.raises(StopIteration) as done:
        next(captured[0])
    assert done.value.value == 42


@pytest.mark.parametrize(
    "source",
    [
        "async def computation():\n    yield from ()\n",
        "async def computation():\n    yield 1\n    return 42\n",
    ],
)
def test_async_generators_cannot_express_this_protocol(source: str):
    with pytest.raises(SyntaxError):
        compile(source, "async-generator-probe", "exec")
