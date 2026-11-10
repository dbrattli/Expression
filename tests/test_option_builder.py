from concurrent.futures import ThreadPoolExecutor
from inspect import Signature, signature, unwrap
from typing import assert_type, cast

import pytest

from expression import Nothing, Option, Some, effect
from expression.effect import OptionScope


def test_option_scope_preserves_intermediate_and_final_types():
    @effect.option
    def computation(scope: OptionScope, number: int, *, suffix: str = "!") -> bool:
        value = scope.bind(Some(number))
        text = scope.bind(Some(str(value)))
        assert_type(value, int)
        assert_type(text, str)
        return text + suffix == "42!"

    assert_type(computation(42), Option[bool])
    assert computation(42) == Some(True)
    assert computation(1, suffix="?") == Some(False)
    assert tuple(signature(computation).parameters) == ("number", "suffix")
    assert signature(computation).return_annotation is Signature.empty
    assert computation.__annotations__ == {"number": int, "suffix": str}
    assert signature(unwrap(computation)).return_annotation is bool
    assert computation.__name__ == "computation"


def test_option_scope_short_circuits_and_runs_cleanup():
    trace: list[str] = []

    @effect.option
    def computation(scope: OptionScope) -> int:
        try:
            scope.bind(Nothing())
            trace.append("unreachable")
            return 1
        finally:
            trace.append("cleanup")

    assert computation() is Nothing()
    assert trace == ["cleanup"]


def test_option_scope_none_is_a_successful_payload():
    @effect.option
    def computation(scope: OptionScope) -> None:
        return scope.bind(Some(None))

    assert_type(computation(), Option[None])
    assert computation() == Some(None)
    assert computation() is not Nothing()


def test_option_scope_preserves_first_failure_when_signal_is_caught():
    @effect.option
    def computation(scope: OptionScope) -> int:
        try:
            scope.bind(Nothing())
        except BaseException:
            pass
        return 42

    assert computation() is Nothing()


def test_option_scope_cannot_bind_after_caught_failure():
    trace: list[str] = []

    @effect.option
    def computation(scope: OptionScope) -> int:
        try:
            scope.bind(Nothing())
        except BaseException:
            pass
        value = scope.bind(Some(42))
        trace.append("resumed")
        return value

    assert computation() is Nothing()
    assert trace == []


def test_option_scope_ordinary_exceptions_propagate_and_close_scope():
    captured: list[OptionScope] = []

    @effect.option
    def computation(scope: OptionScope) -> int:
        captured.append(scope)
        raise ValueError("unexpected")

    with pytest.raises(ValueError, match="unexpected"):
        computation()
    with pytest.raises(RuntimeError, match="no longer active"):
        captured[0].bind(Some(1))


def test_option_scope_cannot_escape_successful_computation():
    @effect.option
    def computation(scope: OptionScope) -> OptionScope:
        return scope

    escaped = computation()
    assert isinstance(escaped, Some)
    with pytest.raises(RuntimeError, match="no longer active"):
        escaped.some.bind(Some(1))


def test_nested_option_scopes_do_not_consume_outer_failure():
    trace: list[str] = []

    @effect.option
    def outer(scope: OptionScope) -> int:
        @effect.option
        def inner(inner_scope: OptionScope) -> int:
            inner_scope.bind(Some(1))
            return scope.bind(Nothing())

        inner()
        trace.append("unreachable")
        return 42

    assert outer() is Nothing()
    assert trace == []


def test_option_scope_rejects_other_effect_families_at_runtime():
    from expression import Ok

    @effect.option
    def computation(scope: OptionScope) -> int:
        return scope.bind(cast(Option[int], Ok(1)))

    with pytest.raises(TypeError, match="Some or Nothing"):
        computation()


def test_option_callback_supports_bound_methods():
    class Service:
        def __init__(self, number: int) -> None:
            self.number = number

        def compute(self, scope: OptionScope) -> str:
            return str(scope.bind(Some(self.number)))

    assert effect.run_option(Service(42).compute) == Some("42")


def test_option_scope_rejects_another_thread():
    @effect.option
    def computation(scope: OptionScope) -> int:
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(scope.bind, Some(42))
            with pytest.raises(RuntimeError, match="another execution context"):
                future.result()
        return scope.bind(Some(1))

    assert computation() == Some(1)
