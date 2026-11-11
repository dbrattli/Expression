"""CE operation laws and explicit deviations from F# compiler translation."""

from collections.abc import Generator
from contextlib import contextmanager

import pytest

from expression import NOTHING, Error, Ok, Some
from investigations.fsharp_ce.computation import (
    OptionBody,
    ResultBody,
    YieldResultBody,
    computation,
    option,
    result,
    yield_result,
)
from investigations.fsharp_ce.positive import describe, forward, optional


def test_let_bang_and_return_preserve_mixed_types():
    assert describe("3").run() == Ok("3 items")
    assert describe("bad").run() == Error("invalid number")
    assert optional(Some(3)).run() == Some("3")
    assert optional(NOTHING).run() is NOTHING


def test_tail_return_bang_delegates_success_and_failure():
    assert forward("3").run() == describe("3").run()
    assert forward("bad").run() == describe("bad").run()


def test_return_lifts_container_but_return_bang_unwraps_one_layer():
    failure = Error("inner")

    @result
    def lift() -> ResultBody[Error[str], str]:
        yield from computation(Ok(None))
        return failure

    @result
    def delegate() -> ResultBody[int, str]:
        return (yield from computation(failure))

    assert lift().run() == Ok(failure)
    assert delegate().run() is failure


def test_return_bang_can_preserve_none_and_nested_option_payloads():
    @option
    def none_payload() -> OptionBody[None]:
        return (yield from computation(Some(None)))

    @option
    def nested_payload() -> OptionBody[Some[int]]:
        return (yield from computation(Some(Some(42))))

    assert none_payload().run() == Some(None)
    assert nested_payload().run() == Some(Some(42))


def test_delay_and_repeatable_run_do_not_execute_on_binding_the_object():
    trace: list[str] = []

    @result
    def step() -> ResultBody[int, str]:
        trace.append("run")
        value = yield from computation(Ok(42))
        return value

    pending = step()  # let, not let!: no execution yet.
    assert trace == []
    assert pending.run() == Ok(42)
    assert pending.run() == Ok(42)
    assert trace == ["run", "run"]


def test_bind_evaluates_each_step_once_and_stops_before_next_operation():
    trace: list[str] = []
    failure = Error("failed")

    @result
    def fail() -> ResultBody[int, str]:
        trace.append("fail")
        return (yield from computation(failure))

    @result
    def outer() -> ResultBody[int, str]:
        trace.append("start")
        number = yield from computation(Ok(1))
        number += yield from fail()
        trace.append("unreachable")
        return number

    assert outer().run() is failure
    assert trace == ["start", "fail"]


def test_do_bang_unit_and_loops_sequence_effects():
    trace: list[int] = []

    @result
    def write(number: int) -> ResultBody[None, str]:
        trace.append(number)
        return (yield from computation(Ok(None)))

    @result
    def outer() -> ResultBody[int, str]:
        for number in range(3):
            yield from write(number)
        count = 0
        while count < 2:
            yield from write(count + 3)
            count += 1
        return count

    assert outer().run() == Ok(2)
    assert trace == [0, 1, 2, 3, 4]


def test_try_finally_and_using_release_resources_on_short_circuit():
    trace: list[str] = []

    @contextmanager
    def resource() -> Generator[None, None, None]:
        trace.append("enter")
        try:
            yield
        finally:
            trace.append("dispose")

    @option
    def outer() -> OptionBody[int]:
        try:
            with resource():
                yield from computation(NOTHING)
                trace.append("unreachable")
                return 1
        finally:
            trace.append("finally")

    assert outer().run() is NOTHING
    assert trace == ["enter", "dispose", "finally"]


def test_try_with_catches_exception_but_not_a_result_error():
    @result
    def raises() -> ResultBody[int, str]:
        yield from computation(Ok(1))
        raise ValueError("unexpected")

    @result
    def recovers() -> ResultBody[int, str]:
        try:
            return (yield from raises())
        except ValueError:
            return 42

    @result
    def fails() -> ResultBody[int, str]:
        try:
            return (yield from computation(Error("expected")))
        except ValueError:
            return 42

    assert recovers().run() == Ok(42)
    assert fails().run() == Error("expected")


def test_left_identity_right_identity_and_associativity():
    def f(number: int):
        return computation(Ok(str(number)))

    def g(text: str):
        return computation(Ok(len(text)))

    @result
    def left_identity() -> ResultBody[str, str]:
        number = yield from computation(Ok(42))
        return (yield from f(number))

    @result
    def right_identity() -> ResultBody[int, str]:
        number = yield from computation(Ok(42))
        return number

    @result
    def sequential() -> ResultBody[int, str]:
        number = yield from computation(Ok(42))
        text = yield from f(number)
        return (yield from g(text))

    @result
    def grouped() -> ResultBody[int, str]:
        text = yield from left_identity()
        return (yield from g(text))

    assert left_identity().run() == f(42).run()
    assert right_identity().run() == Ok(42)
    assert sequential().run() == grouped().run()


def test_legacy_yield_return_spelling_supports_different_bound_payloads():
    @yield_result
    def outer() -> YieldResultBody[str, str]:
        number = yield from computation(Ok(42))
        text = yield from describe(str(number))
        yield text

    assert outer().run() == Ok("42 items")


def test_legacy_combine_is_last_value_and_return_none_is_ambiguous():
    @yield_result
    def omitted() -> YieldResultBody[int, str]:
        yield 42

    @yield_result
    def explicit_none() -> YieldResultBody[int, str]:
        yield 42
        return None

    @yield_result
    def combine() -> YieldResultBody[int, str]:
        yield 42
        yield 43

    @yield_result
    def none_payload() -> YieldResultBody[None, str]:
        yield None

    assert omitted().run() == explicit_none().run() == Ok(42)
    assert combine().run() == Ok(43)
    assert none_payload().run() == Ok(None)


def test_type_correct_conditional_yield_can_produce_no_result():
    @yield_result
    def maybe(include: bool) -> YieldResultBody[str, str]:
        if include:
            yield "value"

    assert maybe(True).run() == Ok("value")
    with pytest.raises(RuntimeError, match="did not produce a result"):
        maybe(False).run()


def test_unit_fallthrough_is_explicit_policy_not_universal_fsharp_zero():
    @option
    def empty() -> OptionBody[None]:
        yield from ()

    # Python return-based runner treats None as a successful payload.
    # An option CE whose Zero() is None would instead produce NOTHING.
    assert empty().run() == Some(None)


def test_raw_object_payload_can_hide_wrong_error_channel():

    @yield_result
    def payload() -> YieldResultBody[object, str]:
        # object accepts every step type too, so the wrong error type escapes
        # checking even with ordinary let! delegation, not a forged event.
        yield from computation(Error(123))
        yield "unreachable"

    # This violates the annotated str error channel: the legacy-yield variant
    # cannot promise sound error typing for arbitrary raw payload types.
    actual = payload().run()
    assert isinstance(actual, Error)
    assert actual.error == 123
