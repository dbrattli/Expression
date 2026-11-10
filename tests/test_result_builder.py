from inspect import Signature, signature, unwrap
from typing import assert_type, cast

import pytest

from expression import Error, Nothing, Ok, Result, effect
from expression.effect import ResultScope


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
        return scope.bind(cast(Result[int, str], Nothing))

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
