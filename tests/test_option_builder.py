"""Scoped computations: migrated builder behavior and scope ownership contracts.

Generator syntax is replaced by bind and return. An empty body or a final None
is successful; previously bound values never replace the body's final return.
"""

from concurrent.futures import ThreadPoolExecutor
from inspect import Signature, signature, unwrap
from typing import assert_type, cast

import pytest

from expression import NOTHING, Nothing, Option, Some, effect
from expression.effect import OptionScope
from tests.utils import CustomException


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


def test_option_scope_evaluation_order():
    evaluated: list[int] = []

    @effect.option
    def computation(scope: OptionScope) -> int:
        evaluated.append(1)
        x = scope.bind(Some(42))
        evaluated.append(2)
        y = scope.bind(Some(43))
        evaluated.append(3)
        return x + y

    assert computation() == Some(85)
    assert evaluated == [1, 2, 3]


def test_option_scope_short_circuits_after_successful_bind():
    evaluated: list[int] = []
    failure = NOTHING

    @effect.option
    def computation(scope: OptionScope) -> int:
        evaluated.append(1)
        x = scope.bind(Some(42))
        evaluated.append(2)
        y = scope.bind(failure)
        evaluated.append(3)
        return x + y

    assert computation() is failure
    assert evaluated == [1, 2]


def test_option_scope_final_return_overrides_discarded_bind_values():
    evaluated: list[int] = []

    @effect.option
    def computation(scope: OptionScope) -> int:
        evaluated.append(1)
        scope.bind(Some(42))
        evaluated.append(2)
        scope.bind(Some(43))
        evaluated.append(3)
        return 44

    assert computation() == Some(44)
    assert evaluated == [1, 2, 3]


@pytest.mark.parametrize("payload", [Some(42), NOTHING])
def test_option_scope_returned_container_is_a_successful_payload(payload: Option[int]):
    @effect.option
    def computation(scope: OptionScope) -> Option[int]:
        return payload

    actual = computation()
    assert_type(actual, Option[Option[int]])
    assert isinstance(actual, Some)
    assert actual.some is payload


@pytest.mark.parametrize("payload", [Some(42), NOTHING])
def test_option_scope_bind_unwraps_exactly_one_layer(payload: Option[int]):
    @effect.option
    def computation(scope: OptionScope) -> Option[int]:
        value = scope.bind(Some(payload))
        assert_type(value, Option[int])
        return value

    actual = computation()
    assert_type(actual, Option[Option[int]])
    assert isinstance(actual, Some)
    assert actual.some is payload


def test_option_scope_empty_body_returns_successful_none():
    @effect.option
    def computation(scope: OptionScope) -> None:
        pass

    assert computation() == Some(None)


def test_option_scope_explicit_none_return_is_successful():
    @effect.option
    def computation(scope: OptionScope) -> None:
        return None

    assert computation() == Some(None)


def test_option_scope_none_return_does_not_retain_last_bound_value():
    @effect.option
    def computation(scope: OptionScope) -> None:
        scope.bind(Some(42))
        return None

    assert computation() == Some(None)


def test_option_scope_fallthrough_does_not_retain_last_bound_value():
    @effect.option
    def computation(scope: OptionScope) -> None:
        scope.bind(Some(42))

    assert computation() == Some(None)


@pytest.mark.parametrize("increment", [0, 1])
def test_option_scope_bound_payload_is_unwrapped_and_return_value_is_wrapped(increment: int):
    @effect.option
    def computation(scope: OptionScope) -> int:
        value = scope.bind(Some(42))
        assert_type(value, int)
        return value + increment

    assert computation() == Some(42 + increment)


def test_option_scope_multiple_operations():
    @effect.option
    def computation(scope: OptionScope) -> int:
        x = scope.bind(Some(42))
        y = scope.bind(Some(43))
        z = scope.bind(Some(44))
        return x + y + z

    assert computation() == Some(129)


def test_option_scope_nested_successful_computations():
    @effect.option
    def inner(scope: OptionScope, x: int) -> int:
        y = scope.bind(Some(x + 1))
        return y + 1

    @effect.option
    def outer(scope: OptionScope) -> int:
        x = scope.bind(Some(42))
        y = scope.bind(inner(x))
        return y + 1

    assert outer() == Some(45)


def test_option_scope_nested_failure_short_circuits_outer_bind():
    evaluated: list[str] = []
    failure = NOTHING

    @effect.option
    def inner(scope: OptionScope) -> int:
        evaluated.append("inner")
        return scope.bind(failure)

    @effect.option
    def outer(scope: OptionScope) -> int:
        evaluated.append("outer")
        value = scope.bind(inner())
        evaluated.append("unreachable")
        return value

    assert outer() is failure
    assert evaluated == ["outer", "inner"]


@pytest.mark.parametrize("failure_at", [None, 1])
def test_option_scope_while_loop(failure_at: int | None):
    evaluated: list[int] = []
    failure = NOTHING

    @effect.option
    def computation(scope: OptionScope) -> int:
        i = 0
        while i < 3:
            evaluated.append(i)
            scope.bind(failure if i == failure_at else Some(i))
            i += 1
        return i

    if failure_at is None:
        assert computation() == Some(3)
        assert evaluated == [0, 1, 2]
    else:
        assert computation() is failure
        assert evaluated == [0, 1]


def test_option_scope_projection_in_nested_for_loops():
    @effect.option
    def computation(scope: OptionScope) -> str:
        text = "Not found"
        for x in Some(42.0):
            for y in Some(int(x)):
                text = scope.bind(Some(str(y)))
        return text

    assert computation() == Some("42")
    assert list(computation()) == ["42"]


def test_option_scope_plain_return_is_wrapped():
    @effect.option
    def computation(scope: OptionScope) -> int:
        return 42

    assert computation() == Some(42)


@pytest.mark.parametrize("error", [CustomException("test error"), RuntimeError("boom")])
def test_option_scope_preserves_raised_exception_identity(error: Exception):
    @effect.option
    def computation(scope: OptionScope) -> int:
        scope.bind(Some(42))
        raise error

    with pytest.raises(type(error)) as caught:
        computation()
    assert caught.value is error
