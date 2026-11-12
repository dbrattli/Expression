import json
import pickle
from collections.abc import Callable
from copy import copy, deepcopy
from dataclasses import FrozenInstanceError, asdict, dataclass, replace
from typing import Annotated, Any, assert_type

import pytest
from hypothesis import given  # type: ignore
from hypothesis import strategies as st
from pydantic import BaseModel, Field, GetCoreSchemaHandler, TypeAdapter, ValidationError
from pydantic_core import CoreSchema, core_schema

from expression import Error, Nothing, Ok, Option, Result, Some, result
from expression.collections import Block
from expression.extra.result import pipeline, sequence

from .utils import CustomException


def test_pattern_match_with_alias():
    xs: Result[int, str] = Ok(42)

    match xs:
        case Ok(x):
            assert x == 42
        case _:
            assert False


def test_result_ok():
    xs = Ok(42)

    assert isinstance(xs, (Ok, Error))
    assert xs.is_ok()
    assert not xs.is_error()
    assert str(xs) == "Ok 42"

    match xs:
        case Ok(x):
            assert x == 42
        case _:
            assert False


def test_result_match_ok():
    xs = Ok(42)

    match xs:
        case Ok(x):
            assert x == 42
        case _:
            assert False


def test_result_match_error():
    xs: Result[int, str] = Error("err")

    match xs:
        case Error(err):
            assert err == "err"
        case _:  # type: ignore
            assert False


def test_result_ok_iterate():
    for x in Ok(42):
        assert x == 42


def test_result_error():
    error = CustomException("d'oh!")
    xs: Result[str, Exception] = Error(error)

    assert isinstance(xs, (Ok, Error))
    assert not xs.is_ok()
    assert xs.is_error()
    assert str(xs) == f"Error {error}"

    match xs:
        case Error(ex):
            assert ex == error


# def test_result_error_iterate():
#     with pytest.raises(Exception) as excinfo:
#         error: Result[int, str] = Error("err")
#         for _ in error:
#             assert False

#     assert excinfo.value.error == "err"  # type: ignore


@given(st.integers(), st.integers())
def test_result_ok_equals_ok(x: int, y: int):
    xs: Result[int, Exception] = Ok(x)
    ys: Result[int, Exception] = Ok(y)

    assert xs == ys if x == y else xs != ys


@given(st.integers())  # type: ignore
def test_result_ok_not_equals_error(x: int):
    assert not Ok(x) == Error(x)
    assert not Error(x) == Ok(x)


@given(st.text(), st.text())
def test_result_error_equals_error(x: int, y: int):
    xs: Result[int, int] = Error(x)
    ys: Result[int, int] = Error(y)

    assert xs == ys if x == y else xs != ys


@given(st.integers(), st.integers())
def test_result_map_piped(x: int, y: int):
    xs: Result[int, Exception] = Ok(x)
    mapper: Callable[[int], int] = lambda x: x + y

    ys = xs.pipe(result.map(mapper))  # NOTE: shows type error for mypy
    match ys:
        case Ok(value):
            assert value == mapper(x)
        case _:
            assert False


@given(st.integers(), st.integers())
def test_result_map_ok_fluent(x: int, y: int):
    xs: Result[int, Exception] = Ok(x)
    mapper: Callable[[int], int] = lambda x: x + y

    ys = xs.map(mapper)
    match ys:
        case Ok(value):
            assert value == mapper(x)
        case _:
            assert False


@given(st.integers(), st.integers())
def test_result_ok_chained_map(x: int, y: int):
    xs: Result[int, Exception] = Ok(x)
    mapper1: Callable[[int], int] = lambda x: x + y
    mapper2: Callable[[int], int] = lambda x: x * 10

    ys = xs.map(mapper1).map(mapper2)

    match ys:
        case Ok(value):
            assert value == mapper2(mapper1(x))
        case _:
            assert False


@given(st.text(), st.integers())  # type: ignore
def test_result_map_error_piped(msg: str, y: int):
    xs: Result[int, str] = Error(msg)
    mapper: Callable[[int], int] = lambda x: x + y

    ys = xs.pipe(result.map(mapper))

    match ys:
        case Error(err):
            assert err == msg
        case _:
            assert False


@given(st.text(), st.integers())  # type: ignore
def test_result_map_error_fluent(msg: str, y: int):
    xs: Result[int, str] = Error(msg)
    mapper: Callable[[int], int] = lambda x: x + y

    ys = xs.map(mapper)
    match ys:
        case Error(err):
            assert err == msg
        case _:
            assert False


@given(st.text(), st.integers())  # type: ignore
def test_result_error_chained_map(msg: str, y: int):
    xs: Result[int, str] = Error(msg)
    mapper1: Callable[[int], int] = lambda x: x + y
    mapper2: Callable[[int], int] = lambda x: x * 10

    ys = xs.map(mapper1).map(mapper2)
    match ys:
        case Error(err):
            assert err == msg
        case _:
            assert False


def test_result_apply():
    value: Result[int, str] = Ok(2)
    function: Result[Callable[[int], int], str] = Ok(lambda x: x + 1)

    assert value.apply(function) == Ok(3)
    assert value.pipe(result.apply(function)) == Ok(3)


def test_result_apply_errors():
    value_error: Result[int, str] = Error("value error")
    function_error: Result[Callable[[int], int], str] = Error("function error")
    function: Result[Callable[[int], int], str] = Ok(lambda x: x + 1)

    assert value_error.apply(function) == Error("value error")
    assert Ok(2).apply(function_error) == Error("function error")
    assert value_error.apply(function_error) == Error("function error")


@given(st.text())
def test_map_error(msg: str):
    assert Error(msg).map_error(lambda x: f"more {x}") == Error("more " + msg)


@given(st.text())
def test_map_error_piped(msg: str):
    assert Error(msg).pipe(result.map_error(lambda x: f"more {x}")) == Error(f"more {msg}")


@given(st.integers(), st.integers())  # type: ignore
def test_result_bind_piped(x: int, y: int):
    xs: Result[int, str] = Ok(x)
    mapper: Callable[[int], Result[int, str]] = lambda x: Ok(x + y)

    ys = xs.pipe(result.bind(mapper))
    match ys:
        case Ok(value):
            assert Ok(value) == mapper(x)
        case _:
            assert False


@given(st.lists(st.integers()))  # type: ignore
def test_result_traverse_ok(xs: list[int]):
    ys: Block[Result[int, str]] = Block([Ok(x) for x in xs])
    zs = sequence(ys)
    match zs:
        case Ok(value):
            assert sum(value) == sum(xs)
        case _:
            assert False


@given(st.lists(st.integers(), min_size=5))  # type: ignore
def test_result_traverse_error(xs: list[int]):
    error = "Do'h"
    ys: Block[Result[int, str]] = Block([Ok(x) if i == 3 else Error(error) for x, i in enumerate(xs)])

    zs = sequence(ys)
    match zs:
        case Error(err):
            assert err == error
        case _:
            assert False


def test_pipeline_none():
    hn = pipeline()

    assert hn(42) == Ok(42)


def test_pipeline_works():
    fn: Callable[[int], Result[int, Exception]] = lambda x: Ok(x * 10)
    gn: Callable[[int], Result[int, Exception]] = lambda x: Ok(x + 10)

    hn = pipeline(
        fn,
        gn,
    )

    assert hn(42) == Ok(430)


def test_pipeline_error():
    error: Result[int, str] = Error("failed")
    fn: Callable[[int], Result[int, str]] = lambda x: Ok(x * 10)
    gn: Callable[[int], Result[int, str]] = lambda x: error

    hn = pipeline(
        fn,
        gn,
    )

    assert hn(42) == error


def test_filter_ok_passing_predicate():
    xs: Result[int, str] = Ok(42)
    ys = xs.filter(lambda x: x > 10, "error")

    assert ys == xs


def test_filter_ok_failing_predicate():
    xs: Result[int, str] = Ok(5)
    ys = xs.filter(lambda x: x > 10, "error")

    assert ys == Error("error")


def test_filter_error():
    error = Error("original error")
    ys = error.filter(lambda x: x > 10, "error")

    assert ys == error


def test_filter_piped():
    def predicate(value: int) -> bool:
        return value > 10

    assert Ok(42).pipe(result.filter(predicate, "error")) == Ok(42)


def test_filter_with_ok_passing_predicate():
    xs: Result[int, str] = Ok(42)
    ys = xs.filter_with(lambda x: x > 10, lambda value: f"error {value}")

    assert ys == xs


def test_filter_with_ok_failing_predicate():
    xs: Result[int, str] = Ok(5)
    ys = xs.filter_with(lambda x: x > 10, lambda value: f"error {value}")

    assert ys == Error("error 5")


def test_filter_with_error():
    error = Error("original error")
    ys = error.filter_with(lambda x: x > 10, lambda value: f"error {value}")

    assert ys == error


def test_filter_with_piped():
    def predicate(value: int) -> bool:
        return value > 10

    assert Ok(42).pipe(result.filter_with(predicate, lambda value: f"error {value}")) == Ok(42)


class MyError(BaseModel):
    message: str


PositiveInt = Annotated[int, Field(gt=0)]


class Username(str):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: GetCoreSchemaHandler) -> CoreSchema:
        return core_schema.no_info_after_validator_function(cls, handler(str))


class Model(BaseModel):
    one: Result[int, MyError]
    two: Result[str, MyError] = Error(MyError(message="error"))
    three: Result[float, MyError] = Error(MyError(message="error"))
    annotated_type: Result[PositiveInt, MyError] = Error(MyError(message="error"))
    annotated_type_error: Result[PositiveInt, MyError] = Error(MyError(message="error"))

    custom_type: Result[Username, MyError] = Error(MyError(message="error"))
    custom_type_error: Result[Username, MyError] = Error(MyError(message="error"))


def test_parse_block_works():
    obj = dict(
        one=dict(tag="ok", ok=42), annotated_type=dict(tag="ok", ok=42), custom_type=dict(tag="ok", ok="johndoe")
    )
    model = Model.model_validate(obj)

    assert isinstance(model.one, Ok)
    assert model.one == Ok(42)
    assert model.two == Error(MyError(message="error"))
    assert model.three == Error(MyError(message="error"))
    assert model.annotated_type == Ok(42)
    assert model.annotated_type_error == Error(MyError(message="error"))
    assert model.custom_type == Ok(Username("johndoe"))
    assert model.custom_type_error == Error(MyError(message="error"))


def test_ok_to_dict_works():
    result = Ok(10)
    obj = result.dict()
    assert obj == dict(tag="ok", ok=10)


def test_error_to_dict_works():
    error = MyError(message="got error")
    result = Error(error)
    obj = result.dict()
    assert obj == dict(tag="error", error=dict(message="got error"))


def test_ok_from_from_dict_works():
    obj = dict(tag="ok", ok=10)
    adapter = TypeAdapter(Result[int, MyError])
    result = adapter.validate_python(obj)

    assert result
    assert isinstance(result, (Ok, Error))
    match result:
        case Ok(x):
            assert x == 10
        case _:
            assert False


def test_error_from_dict_works():
    obj = dict(tag="error", error=dict(message="got error"))
    adapter = TypeAdapter(Result[int, MyError])
    result = adapter.validate_python(obj)

    assert result
    assert isinstance(result, (Ok, Error))
    match result:
        case Error(error):
            assert error.message == "got error"
        case _:
            assert False


def test_model_to_json_works():
    obj = dict(
        one=dict(tag="ok", ok=10), annotated_type=dict(tag="ok", ok=10), custom_type=dict(tag="ok", ok="johndoe")
    )

    model = Model.model_validate(obj)
    obj = model.model_dump_json()
    assert json.loads(obj) == json.loads(
        '{"one":{"tag":"ok","ok":10},"two":{"tag":"error","error":{"message":"error"}},"three":{"tag":"error","error":{"message":"error"}},"annotated_type":{"tag":"ok","ok":10},"annotated_type_error":{"tag":"error","error":{"message":"error"}},"custom_type":{"tag":"ok","ok":"johndoe"},"custom_type_error":{"tag":"error","error":{"message":"error"}}}'
    )


def test_error_default_value():
    xs: Result[int, int] = Error(0)

    zs = xs.default_value(42)

    assert zs == 42


def test_ok_default_value():
    xs: Result[int, int] = Ok(42)
    zs = xs.default_value(0)

    assert zs == 42


def test_error_default_with():
    xs: Result[int, int] = Error(0)

    zs = xs.default_with(lambda x: x + 42)

    assert zs == 42


def test_ok_default_with():
    xs: Result[int, int] = Ok(42)
    zs = xs.default_with(lambda x: 0)

    assert zs == 42


def test_result_to_option_ok():
    Ok(42).to_option()
    res: Result[int, Any] = Ok(42)
    xs = result.to_option(res)
    assert xs.is_some()


def test_result_to_option_error():
    xs: Option[Any] = result.to_option(Error("oops"))
    assert xs.is_none()


def test_result_of_option_ok():
    xs = result.of_option(Some(42), "oops")
    assert xs == Ok(42)


def test_result_of_option_error():
    xs = result.of_option(Nothing(), "oops")
    assert xs == Error("oops")


def test_result_of_option_with_ok():
    xs = result.of_option_with(Some(42), error=lambda: exec('raise(Exception("Should not be called"))'))
    assert xs == Ok(42)


def test_result_of_option_with_error():
    xs = result.of_option_with(Nothing(), error=lambda: "oops")
    assert xs == Error("oops")


def test_result_swap_with_ok():
    ok: Result[int, str] = Ok(1)
    xs = result.swap(ok)
    assert xs == Error(1)


def test_result_swap_with_error():
    error: Result[str, int] = Error(1)
    xs = result.swap(error)
    assert xs == Ok(1)


def test_swap_piped():
    assert Ok(42).pipe(result.swap) == Error(42)


def test_ok_or_else_ok():
    xs: Result[int, str] = Ok(42)
    ys = xs.or_else(Ok(0))
    assert ys == Ok(42)


def test_ok_or_else_error():
    xs: Result[int, str] = Ok(42)
    ys = xs.or_else(Error("new error"))
    assert ys == Ok(42)


def test_error_or_else_ok():
    xs: Result[int, str] = Error("original error")
    ys = xs.or_else(Ok(0))
    assert ys == Ok(0)


def test_error_or_else_error():
    xs: Result[int, str] = Error("original error")
    ys = xs.or_else(Error("new error"))
    assert ys == Error("new error")


def test_or_else_piped():
    assert Ok(42).pipe(result.or_else(Ok(0))) == Ok(42)


def test_ok_or_else_with_ok():
    xs: Result[str, str] = Ok("good")
    ys = xs.or_else_with(lambda error: Ok(f"new error from {error}"))
    assert ys == Ok("good")


def test_ok_or_else_with_error():
    xs: Result[str, str] = Ok("good")
    ys = xs.or_else_with(lambda error: Ok(f"new error from {error}"))
    assert ys == Ok("good")


def test_error_or_else_with_ok():
    xs: Result[str, str] = Error("original error")
    ys = xs.or_else_with(lambda error: Ok(f"fixed {error}"))
    assert ys == Ok("fixed original error")


def test_error_or_else_with_error():
    xs: Result[str, str] = Error("original error")
    ys = xs.or_else_with(lambda error: Error(f"new error from {error}"))
    assert ys == Error("new error from original error")


def test_or_else_with_piped():
    assert Ok(42).pipe(result.or_else_with(lambda _: Ok(0))) == Ok(42)


def test_merge_ok():
    assert Ok(42).merge() == 42


def test_merge_error():
    # Explicit type annotation required as merge favours the _TSource type
    xs: Result[str, str] = Error("error")
    assert xs.merge() == "error"


class Parent:
    pass


@dataclass
class Child1(Parent):
    x: int


@dataclass
class Child2(Parent):
    pass


def test_merge_subclasses():
    xs = Ok(Child1(x=42))
    assert xs.merge() == Child1(x=42)


def test_merge_piped():
    assert Ok(42).pipe(result.merge) == 42


class A:
    pass


class B(A):
    pass


def test_result_covariance() -> None:
    x: Result[B, str] = Ok(B())
    y: Result[A, str] = x

    assert y.is_ok()


def test_result_covariance_error() -> None:
    x: Result[str, B] = Error(B())
    y: Result[str, A] = x

    assert y.is_error()


def test_case_fields_are_real_and_frozen():
    value = Ok(42)
    assert asdict(value) == {"ok": 42, "tag": "ok"}
    assert replace(value, ok=43) == Ok(43)
    assert not hasattr(value, "error")
    assert not hasattr(Error("bad"), "ok")
    with pytest.raises(FrozenInstanceError):
        setattr(value, "ok", 0)
    with pytest.raises(TypeError):
        Ok(1, tag="error")  # type: ignore[call-arg]


def test_result_cases_are_closed():
    for case_type in (Ok, Error):
        with pytest.raises(TypeError, match="final"):
            type("AdditionalCase", (case_type,), {})


def test_result_copy_pickle_and_hash():
    for value in (Ok((1, 2)), Error("bad")):
        assert copy(value) == value
        assert deepcopy(value) == value
        assert pickle.loads(pickle.dumps(value)) == value
        assert hash(value) == hash(copy(value))
    with pytest.raises(TypeError):
        hash(Ok([]))


def test_result_iteration_and_awaiting_use_effect_protocol():
    from expression.core.error import EffectError

    assert list(Ok(42)) == [42]
    with pytest.raises(EffectError):
        list(Error("bad"))
    assert hasattr(Ok(42), "__await__")
    assert hasattr(Error("bad"), "__await__")


def test_result_does_not_order_cases():
    with pytest.raises(TypeError):
        Ok(1) < Error("bad")  # type: ignore[operator]


@pytest.mark.parametrize(
    "value",
    [
        {"ok": 42},
        {"tag": "error", "ok": 42},
        {"tag": "ok", "error": "bad"},
        {"tag": "unknown", "ok": 42},
        {"tag": "ok", "ok": 42, "error": "bad"},
        {"tag": "ok", "ok": "invalid integer"},
    ],
)
def test_result_wire_input_rejects_invalid_cases(value: object):
    adapter = TypeAdapter(Result[int, str])
    with pytest.raises(ValidationError):
        adapter.validate_python(value)


def test_result_nested_tagged_roundtrip():
    adapter = TypeAdapter(Result[Result[None, str], str])
    value: Result[Result[None, str], str] = Ok(Ok(None))
    encoded = adapter.dump_json(value)
    assert json.loads(encoded) == {"tag": "ok", "ok": {"tag": "ok", "ok": None}}
    assert adapter.validate_json(encoded) == value
    assert value.dict() == json.loads(encoded)
    assert adapter.validate_python({"tag": "ok", "ok": {"tag": "error", "error": "nested"}}) == Ok(Error("nested"))


def test_result_schema_discriminates_cases():
    schema = TypeAdapter(Result[int, str]).json_schema()
    assert schema["discriminator"]["propertyName"] == "tag"
    assert set(schema["discriminator"]["mapping"]) == {"ok", "error"}


@pytest.mark.parametrize("payload", [42, "text", None, {"nested": [1, 2]}])
@pytest.mark.parametrize("tag", ["ok", "error"])
def test_unparameterized_result_pydantic_roundtrip(tag: str, payload: object):
    class BareResultModel(BaseModel):
        value: Result

    wire = {"tag": tag, tag: payload}
    expected = Ok(payload) if tag == "ok" else Error(payload)
    adapter = TypeAdapter(Result)
    value = adapter.validate_python(wire)
    assert value == expected
    assert adapter.validate_json(adapter.dump_json(value)) == expected
    assert adapter.dump_python(value) == wire
    schema = adapter.json_schema()
    assert set(schema["discriminator"]["mapping"]) == {"ok", "error"}

    model = BareResultModel.model_validate({"value": wire})
    assert model.value == expected
    assert model.model_dump() == {"value": wire}
    assert BareResultModel.model_validate_json(model.model_dump_json()) == model
    assert "value" in BareResultModel.model_json_schema()["properties"]


def result_pipe_type_contract(
    value: Result[int, str], other: Result[int, float], function: Result[Callable[[int], bytes], float]
) -> None:
    """Check unresolved unions rather than assignments narrowed to one case."""

    def compute(number: int) -> Result[str, float]:
        return Ok(str(number))

    def recover(error: str) -> Result[bytes, bool]:
        return Ok(error.encode())

    def positive(number: int) -> bool:
        return number > 0

    def add(left: int, right: int) -> int:
        return left + right

    assert_type(value.pipe(result.map(str)), Result[str, str])
    assert_type(value.pipe(result.map_error(len)), Result[int, int])
    assert_type(value.pipe(result.bind(compute)), Ok[str] | Error[float] | Error[str])
    assert_type(value.pipe(result.or_else(Ok(b"recovered"))), Ok[int] | Ok[bytes])
    assert_type(value.pipe(result.or_else_with(recover)), Ok[int] | Ok[bytes] | Error[bool])
    assert_type(value.pipe(result.default_value(0.0)), int | float)
    assert_type(value.pipe(result.default_with(len)), int)
    assert_type(value.pipe(result.swap), Result[str, int])
    assert_type(value.pipe(result.merge), int | str)
    assert_type(value.pipe(result.to_option), Option[int])
    assert_type(value.pipe(result.filter(positive, 1.0)), Ok[int] | Error[str] | Error[float])
    assert_type(value.pipe(result.filter_with(positive, float)), Ok[int] | Error[str] | Error[float])
    assert_type(other.pipe(result.map2(add)(value)), Ok[int] | Error[str] | Error[float])
    assert_type(value.pipe(result.apply(function)), Ok[bytes] | Error[str] | Error[float])
    assert_type(Ok(1).pipe(result.apply(Ok(str))), Ok[str])
    assert_type(Ok(1).pipe(result.apply(Error("failed"))), Error[str])
    assert_type(Ok(2).pipe(result.map2(add)(Ok(1))), Ok[int])
    assert_type(Ok(2).pipe(result.map2(add)(Error("failed"))), Error[str])
    assert_type(result.of_option(Nothing(), "missing"), Error[str])
    assert_type(result.of_option(Some(42), "missing"), Ok[int])


def test_curried_binary_operations_preserve_error_precedence():
    def add(left: int, right: int) -> int:
        return left + right

    assert result.map2(add)(Ok(2))(Ok(3)) == Ok(5)
    assert result.map2(add)(Error("first"))(Error("second")) == Error("first")
    assert result.map2(add)(Ok(2))(Error("second")) == Error("second")
    assert Error("value").pipe(result.apply(Error("function"))) == Error("function")
    assert Ok(2).pipe(result.apply(Error("function"))) == Error("function")
