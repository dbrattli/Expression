from collections.abc import Callable, Generator
from typing import Annotated, Any

import pytest
from hypothesis import given  # type: ignore
from hypothesis import strategies as st
from pydantic import BaseModel, TypeAdapter
from pydantic.annotated_handlers import GetCoreSchemaHandler
from pydantic_core import core_schema

from expression import Error, Nothing, Ok, Option, Result, Some, effect, result
from expression.collections import Block
from expression.extra.result import pipeline, sequence

from .utils import CustomException


class CustomString(str):
    @classmethod
    def __get_pydantic_core_schema__(
            cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> Any:
        return core_schema.no_info_after_validator_function(cls, handler(str))

def test_pattern_match_with_alias():
    xs: Result[int, str] = Ok(42)

    match xs:
        case Result(tag="ok", ok=x):
            assert x == 42
        case _:
            assert False


def test_result_ok():
    xs: Result[int, str] = Result.Ok(42)

    assert isinstance(xs, Result)
    assert xs.is_ok()
    assert not xs.is_error()
    assert str(xs) == "Ok 42"

    match xs:
        case Result(tag="ok", ok=x):
            assert x == 42
        case _:
            assert False


def test_result_match_ok():
    xs: Result[int, str] = Result.Ok(42)

    match xs:
        case Result(tag="ok", ok=x):
            assert x == 42
        case _:
            assert False


def test_result_match_error():
    xs: Result[int, str] = Error("err")

    match xs:
        case Result(tag="error", error=err):
            assert err == "err"
        case _:  # type: ignore
            assert False


def test_result_ok_iterate():
    for x in Ok(42):
        assert x == 42


def test_result_error():
    error = CustomException("d'oh!")
    xs: Result[str, Exception] = Error(error)

    assert isinstance(xs, Result)
    assert not xs.is_ok()
    assert xs.is_error()
    assert str(xs) == f"Error {error}"

    match xs:
        case Result(tag="ok"):
            assert False

        case Result(error=ex):
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
        case Result(tag="ok", ok=value):
            assert value == mapper(x)
        case _:
            assert False


@given(st.integers(), st.integers())
def test_result_map_ok_fluent(x: int, y: int):
    xs: Result[int, Exception] = Ok(x)
    mapper: Callable[[int], int] = lambda x: x + y

    ys = xs.map(mapper)
    match ys:
        case Result(tag="ok", ok=value):
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
        case Result(tag="ok", ok=value):
            assert value == mapper2(mapper1(x))
        case _:
            assert False


@given(st.text(), st.integers())  # type: ignore
def test_result_map_error_piped(msg: str, y: int):
    xs: Result[int, str] = Error(msg)
    mapper: Callable[[int], int] = lambda x: x + y

    ys = xs.pipe(result.map(mapper))

    match ys:
        case Result(tag="error", error=err):
            assert err == msg
        case _:
            assert False


@given(st.text(), st.integers())  # type: ignore
def test_result_map_error_fluent(msg: str, y: int):
    xs: Result[int, str] = Error(msg)
    mapper: Callable[[int], int] = lambda x: x + y

    ys = xs.map(mapper)
    match ys:
        case Result(tag="error", error=err):
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
        case Result(tag="error", error=err):
            assert err == msg
        case _:
            assert False


@given(st.integers(), st.integers())  # type: ignore
def test_result_bind_piped(x: int, y: int):
    xs: Result[int, str] = Ok(x)
    mapper: Callable[[int], Result[int, str]] = lambda x: Ok(x + y)

    ys = xs.pipe(result.bind(mapper))
    match ys:
        case Result(tag="ok", ok=value):
            assert Ok(value) == mapper(x)
        case _:
            assert False


@given(st.lists(st.integers()))  # type: ignore
def test_result_traverse_ok(xs: list[int]):
    ys: Block[Result[int, str]] = Block([Ok(x) for x in xs])
    zs = sequence(ys)
    match zs:
        case Result(tag="ok", ok=value):
            assert sum(value) == sum(xs)
        case _:
            assert False


@given(st.lists(st.integers(), min_size=5))  # type: ignore
def test_result_traverse_error(xs: list[int]):
    error = "Do'h"
    ys: Block[Result[int, str]] = Block([Ok(x) if i == 3 else Error(error) for x, i in enumerate(xs)])

    zs = sequence(ys)
    match zs:
        case Result(tag="error", error=err):
            assert err == error
        case _:
            assert False


def test_result_effect_zero():
    @effect.result()
    def fn():
        while False:
            yield

    with pytest.raises(NotImplementedError):
        fn()


def test_result_effect_yield_ok():
    @effect.result[int, Exception]()
    def fn():
        yield 42
        return None

    xs = fn()
    for x in xs:
        assert x == 42


def test_result_effect_return_ok():
    @effect.result[int, Exception]()
    def fn() -> Generator[int, int, int]:
        x: int = yield 42
        return x

    xs = fn()
    match xs:
        case Result(tag="ok", ok=x):
            assert x == 42
        case _:
            assert False


def test_result_effect_yield_from_ok():
    @effect.result[int, Exception]()
    def fn() -> Generator[int, int, int]:
        x = yield from Ok(42)
        return x + 1

    xs = fn()
    match xs:
        case Result(tag="ok", ok=x):
            assert x == 43
        case _:
            assert False


def test_result_effect_yield_from_error():
    error = "Do'h"

    def mayfail() -> Result[int, str]:
        return Error(error)

    @effect.result[int, Exception]()
    def fn() -> Generator[int, int, int]:
        xs = mayfail()
        x: int = yield from xs
        return x + 1

    xs = fn()
    match xs:
        case Result(tag="error", error=err):
            assert err == error
        case _:
            assert False, "Should not happen"


def test_result_effect_multiple_ok():
    @effect.result[int, Exception]()
    def fn() -> Generator[int, int, int]:
        x: int = yield 42
        y = yield from Ok(43)

        return x + y

    xs = fn()
    match xs:
        case Result(tag="ok", ok=value):
            assert value == 85
        case _:
            assert False


def test_result_effect_throws():
    error = CustomException("this happend!")

    @effect.result[int, Exception]()
    def fn() -> Generator[int, int, int]:
        _ = yield from Ok(42)
        raise error

    with pytest.raises(CustomException) as exc:
        fn()

    assert exc.value == error


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


class MyError(BaseModel):
    message: str


class Model(BaseModel):
    one: Result[int, MyError]
    two: Result[str, MyError] = Error(MyError(message="error"))
    three: Result[float, MyError] = Error(MyError(message="error"))


def test_parse_block_works():
    obj = dict(one=dict(ok=42))
    model = Model.model_validate(obj)

    assert isinstance(model.one, Result)
    assert model.one == Ok(42)
    assert model.two == Error(MyError(message="error"))
    assert model.three == Error(MyError(message="error"))


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
    obj = dict(ok=10)
    adapter = TypeAdapter(Result[int, MyError])
    result = adapter.validate_python(obj)

    assert result
    assert isinstance(result, Result)
    match result:
        case Result(tag="ok", ok=x):
            assert x == 10
        case _:
            assert False


def test_error_from_dict_works():
    obj = dict(error=dict(message="got error"))
    adapter = TypeAdapter(Result[int, MyError])
    result = adapter.validate_python(obj)

    assert result
    assert isinstance(result, Result)
    match result:
        case Result(tag="error", error=error):
            assert error.message == "got error"
        case _:
            assert False


def test_model_to_json_works():
    model = Model(one=Ok(10))
    obj = model.model_dump_json()
    assert (
        obj
        == '{"one":{"tag":"ok","ok":10},"two":{"tag":"error","error":{"message":"error"}},"three":{"tag":"error","error":{"message":"error"}}}'
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
    xs = result.of_option(Nothing, "oops")
    assert xs == Error("oops")


def test_result_of_option_with_ok():
    xs = result.of_option_with(Some(42), error=lambda: exec('raise(Exception("Should not be called"))'))
    assert xs == Ok(42)


def test_result_of_option_with_error():
    xs = result.of_option_with(Nothing, error=lambda: "oops")
    assert xs == Error("oops")


def test_result_swap_with_ok():
    ok: Result[int, str] = Ok(1)
    xs = result.swap(ok)
    assert xs == Error(1)


def test_result_swap_with_error():
    error: Result[str, int] = Error(1)
    xs = result.swap(error)
    assert xs == Ok(1)

def test_nested_type_in_pydantic():
    class Target(BaseModel):
        value: Result[Annotated[Annotated[int, 1], 2], Any]

    schema = Target.model_json_schema()
    assert "properties" in schema
    properties = schema["properties"]
    assert "value" in properties
    value = properties["value"]
    assert value == {
        "anyOf": [
            {
                "properties": {"tag": {"title": "Tag", "type": "string"}, "ok": {"title": "Ok", "type": "integer"}},
                "required": ["tag", "ok"],
                "type": "object",
            },
            {
                "properties": {"tag": {"title": "Tag", "type": "string"}, "error": {"title": "Error"}},
                "required": ["tag", "error"],
                "type": "object",
            },
        ],
        "title": "Value",
    }


def test_custom_type_in_pydantic():
    class Target(BaseModel): # pyright: ignore[reportUnusedClass]
        value:  Result[CustomString, Any]

def test_nested_custom_type_in_pydantic():
    class Target(BaseModel): # pyright: ignore[reportUnusedClass]
        value:  Result[Annotated[Annotated[CustomString, 1], 2], Any]
