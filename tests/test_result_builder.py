"""Scoped computations: migrated builder behavior and scope ownership contracts.

Generator syntax is replaced by bind and return. An empty body or a final None
is successful; previously bound values never replace the body's final return.
"""

from inspect import Signature, signature, unwrap
from typing import assert_type, cast

import pytest

from expression import Error, Nothing, Ok, Result, effect
from expression.effect import ResultScope
from tests.utils import CustomException


def test_result_scope_preserves_intermediate_and_final_types():
    @effect.result
    def computation(scope: ResultScope[str], number: int, *, suffix: str = "!") -> bool:
        value = scope.bind(Ok(number))
        text = scope.bind(Ok(str(value)))
        assert_type(value, int)
        assert_type(text, str)
        return text + suffix == "42!"

    assert_type(computation(42), Result[bool, str])
    assert computation(42) == Ok(True)
    assert computation(1, suffix="?") == Ok(False)
    assert tuple(signature(computation).parameters) == ("number", "suffix")
    assert signature(computation).return_annotation is Signature.empty
    assert computation.__annotations__ == {"number": int, "suffix": str}
    assert signature(unwrap(computation)).return_annotation is bool


def test_result_scope_short_circuits_with_original_error_and_cleanup():
    trace: list[str] = []
    failure = Error("missing")

    @effect.result
    def computation(scope: ResultScope[str]) -> int:
        try:
            scope.bind(failure)
            trace.append("unreachable")
            return 42
        finally:
            trace.append("cleanup")

    assert computation() is failure
    assert trace == ["cleanup"]


def test_result_scope_none_is_a_successful_payload():
    @effect.result
    def computation(scope: ResultScope[str]) -> None:
        return scope.bind(Ok(None))

    assert_type(computation(), Result[None, str])
    assert computation() == Ok(None)


def test_result_scope_preserves_first_failure_when_signal_is_caught():
    @effect.result
    def computation(scope: ResultScope[str]) -> int:
        try:
            scope.bind(Error("first"))
        except BaseException:
            pass
        return 42

    assert computation() == Error("first")


def test_result_scope_cannot_replace_failure_after_catching_signal():
    @effect.result
    def computation(scope: ResultScope[str]) -> int:
        try:
            scope.bind(Error("first"))
        except BaseException:
            pass
        return scope.bind(Error("second"))

    assert computation() == Error("first")


def test_result_scope_ordinary_exceptions_propagate_and_close_scope():
    captured: list[ResultScope[str]] = []

    @effect.result
    def computation(scope: ResultScope[str]) -> int:
        captured.append(scope)
        raise ValueError("unexpected")

    with pytest.raises(ValueError, match="unexpected"):
        computation()
    with pytest.raises(RuntimeError, match="no longer active"):
        captured[0].bind(Ok(42))


def test_result_scope_cannot_escape_successful_computation():
    @effect.result
    def computation(scope: ResultScope[str]) -> ResultScope[str]:
        return scope

    escaped = computation()
    assert isinstance(escaped, Ok)
    with pytest.raises(RuntimeError, match="no longer active"):
        escaped.ok.bind(Ok(42))


def test_nested_result_scopes_do_not_consume_outer_failure():
    trace: list[str] = []

    @effect.result
    def outer(scope: ResultScope[str]) -> int:
        @effect.result
        def inner(inner_scope: ResultScope[int]) -> int:
            inner_scope.bind(Ok(1))
            return scope.bind(Error("outer"))

        inner()
        trace.append("unreachable")
        return 42

    assert outer() == Error("outer")
    assert trace == []


def test_recursive_computations_have_independent_scopes():
    @effect.result
    def factorial(scope: ResultScope[str], n: int) -> int:
        if n < 0:
            scope.bind(Error("negative"))
        if n == 0:
            return 1
        return n * scope.bind(factorial(n - 1))

    assert factorial(5) == Ok(120)
    assert factorial(-1) == Error("negative")


def test_result_scope_rejects_other_effect_families_at_runtime():
    @effect.result
    def computation(scope: ResultScope[str]) -> int:
        return scope.bind(cast(Result[int, str], Nothing()))

    with pytest.raises(TypeError, match="Ok or Error"):
        computation()


def test_result_callback_supports_bound_methods():
    class Service:
        def __init__(self, number: int) -> None:
            self.number = number

        def compute(self, scope: ResultScope[str]) -> str:
            return str(scope.bind(Ok(self.number)))

    assert effect.run_result(Service(42).compute) == Ok("42")


def test_try_scope_uses_explicit_exception_errors():
    failure = ValueError("expected")

    @effect.try_
    def computation(scope: ResultScope[Exception], fail: bool) -> int:
        if fail:
            scope.bind(Error(failure))
        return scope.bind(Ok(42))

    assert_type(computation(False), Result[int, Exception])
    assert computation(False) == Ok(42)
    assert computation(True) == Error(failure)


def test_result_scope_evaluation_order():
    evaluated: list[int] = []

    @effect.result
    def computation(scope: ResultScope[str]) -> int:
        evaluated.append(1)
        x = scope.bind(Ok(42))
        evaluated.append(2)
        y = scope.bind(Ok(43))
        evaluated.append(3)
        return x + y

    assert computation() == Ok(85)
    assert evaluated == [1, 2, 3]


def test_result_scope_short_circuits_after_successful_bind():
    evaluated: list[int] = []
    failure = Error("failure")

    @effect.result
    def computation(scope: ResultScope[str]) -> int:
        evaluated.append(1)
        x = scope.bind(Ok(42))
        evaluated.append(2)
        y = scope.bind(failure)
        evaluated.append(3)
        return x + y

    assert computation() is failure
    assert evaluated == [1, 2]


def test_result_scope_final_return_overrides_discarded_bind_values():
    evaluated: list[int] = []

    @effect.result
    def computation(scope: ResultScope[str]) -> int:
        evaluated.append(1)
        scope.bind(Ok(42))
        evaluated.append(2)
        scope.bind(Ok(43))
        evaluated.append(3)
        return 44

    assert computation() == Ok(44)
    assert evaluated == [1, 2, 3]


@pytest.mark.parametrize("payload", [Ok(42), Error("failure")])
def test_result_scope_returned_container_is_a_successful_payload(payload: Result[int, str]):
    @effect.result
    def computation(scope: ResultScope[str]) -> Result[int, str]:
        return payload

    actual = computation()
    assert_type(actual, Result[Result[int, str], str])
    assert isinstance(actual, Ok)
    assert actual.ok is payload


@pytest.mark.parametrize("payload", [Ok(42), Error("failure")])
def test_result_scope_bind_unwraps_exactly_one_layer(payload: Result[int, str]):
    @effect.result
    def computation(scope: ResultScope[str]) -> Result[int, str]:
        value = scope.bind(Ok(payload))
        assert_type(value, Result[int, str])
        return value

    actual = computation()
    assert_type(actual, Result[Result[int, str], str])
    assert isinstance(actual, Ok)
    assert actual.ok is payload


def test_result_scope_empty_body_returns_successful_none():
    @effect.result
    def computation(scope: ResultScope[str]) -> None:
        pass

    assert computation() == Ok(None)


def test_result_scope_explicit_none_return_is_successful():
    @effect.result
    def computation(scope: ResultScope[str]) -> None:
        return None

    assert computation() == Ok(None)


def test_result_scope_none_return_does_not_retain_last_bound_value():
    @effect.result
    def computation(scope: ResultScope[str]) -> None:
        scope.bind(Ok(42))
        return None

    assert computation() == Ok(None)


def test_result_scope_fallthrough_does_not_retain_last_bound_value():
    @effect.result
    def computation(scope: ResultScope[str]) -> None:
        scope.bind(Ok(42))

    assert computation() == Ok(None)


@pytest.mark.parametrize("increment", [0, 1])
def test_result_scope_bound_payload_is_unwrapped_and_return_value_is_wrapped(increment: int):
    @effect.result
    def computation(scope: ResultScope[str]) -> int:
        value = scope.bind(Ok(42))
        assert_type(value, int)
        return value + increment

    assert computation() == Ok(42 + increment)


def test_result_scope_multiple_operations():
    @effect.result
    def computation(scope: ResultScope[str]) -> int:
        x = scope.bind(Ok(42))
        y = scope.bind(Ok(43))
        z = scope.bind(Ok(44))
        return x + y + z

    assert computation() == Ok(129)


def test_result_scope_nested_successful_computations():
    @effect.result
    def inner(scope: ResultScope[str], x: int) -> int:
        y = scope.bind(Ok(x + 1))
        return y + 1

    @effect.result
    def outer(scope: ResultScope[str]) -> int:
        x = scope.bind(Ok(42))
        y = scope.bind(inner(x))
        return y + 1

    assert outer() == Ok(45)


def test_result_scope_nested_failure_short_circuits_outer_bind():
    evaluated: list[str] = []
    failure = Error("failure")

    @effect.result
    def inner(scope: ResultScope[str]) -> int:
        evaluated.append("inner")
        return scope.bind(failure)

    @effect.result
    def outer(scope: ResultScope[str]) -> int:
        evaluated.append("outer")
        value = scope.bind(inner())
        evaluated.append("unreachable")
        return value

    assert outer() is failure
    assert evaluated == ["outer", "inner"]


@pytest.mark.parametrize("failure_at", [None, 1])
def test_result_scope_while_loop(failure_at: int | None):
    evaluated: list[int] = []
    failure = Error("failure")

    @effect.result
    def computation(scope: ResultScope[str]) -> int:
        i = 0
        while i < 3:
            evaluated.append(i)
            scope.bind(failure if i == failure_at else Ok(i))
            i += 1
        return i

    if failure_at is None:
        assert computation() == Ok(3)
        assert evaluated == [0, 1, 2]
    else:
        assert computation() is failure
        assert evaluated == [0, 1]


def test_result_scope_projection_in_nested_for_loops():
    @effect.result
    def computation(scope: ResultScope[str]) -> str:
        text = "Not found"
        for x in Ok(42.0):
            for y in Ok(int(x)):
                text = scope.bind(Ok(str(y)))
        return text

    assert computation() == Ok("42")
    assert list(computation()) == ["42"]


def test_result_scope_plain_return_is_wrapped():
    @effect.result
    def computation(scope: ResultScope[str]) -> int:
        return 42

    assert computation() == Ok(42)


@pytest.mark.parametrize("error", [CustomException("test error"), RuntimeError("boom")])
def test_result_scope_preserves_raised_exception_identity(error: Exception):
    @effect.result
    def computation(scope: ResultScope[str]) -> int:
        scope.bind(Ok(42))
        raise error

    with pytest.raises(type(error)) as caught:
        computation()
    assert caught.value is error
