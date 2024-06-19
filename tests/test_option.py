from collections.abc import Callable, Generator
from typing import Any, Annotated

import pytest
from hypothesis import given  # type: ignore
from hypothesis import strategies as st
from pydantic import BaseModel, Field, GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema

from expression import (
    Error,
    Nothing,
    Ok,
    Option,
    Result,
    Some,
    effect,
    option,
    pipe,
    pipe2,
)
from expression.core.option import Nothing, Option, Some
from expression.extra.option import pipeline
from tests.utils import CustomException


def test_option_some():
    xs = Some(42)

    assert isinstance(xs, Option)
    assert pipe(xs, option.is_some) is True
    assert pipe(xs, option.is_none) is False


def test_option_some_match():
    xs = Option.Some(42)

    match xs:
        case Option(tag="some", some=x):
            assert x == 42

        case _:
            assert False


def test_option_some_match_fluent():
    xs = Some(42)
    ys = xs.map(lambda x: x + 1)

    match ys:
        case Option(tag="some", some=value):
            assert value == 43
        case _:
            assert False


def test_option_some_iterate():
    xs = Some(42)

    for x in option.to_list(xs):
        assert x == 42
        break
    else:
        assert False


def test_option_none():
    xs = Nothing

    assert isinstance(xs, Option)
    assert xs.pipe(option.is_some) is False
    assert xs.pipe(option.is_none) is True


def test_option_none_match():
    xs = Nothing

    match xs:
        case Option(tag="some"):
            assert False

        case x if x is Nothing:
            assert True

        case _:
            assert False


def test_option_nothing_iterate():
    xs = Nothing

    for _ in option.to_list(xs):
        assert False


def test_option_none_equals_none():
    xs = Nothing
    ys = Nothing

    assert xs == ys


def test_option_none_not_equals_some():
    xs = Some(42)
    ys = Nothing

    assert xs != ys
    assert ys != xs


def test_option_order_some_some_works():
    xs = Some(42)
    ys = Some(41)

    assert xs > ys
    assert ys < xs


def test_option_order_some_none_works():
    xs = Some(42)
    ys = Nothing

    assert xs > ys
    assert ys < xs


def test_option_order_none_none_works():
    xs = Nothing
    ys = Nothing

    assert not (xs < ys)


def test_option_none_default_value():
    xs = Nothing

    zs = xs.default_value(42)

    assert zs == 42


def test_option_some_default_value():
    xs: Option[int] = Some(42)
    zs = xs.default_value(0)

    assert zs == 42


def test_option_none_default_with():
    xs = Nothing

    zs = xs.default_with(lambda: 42)

    assert zs == 42


def test_option_some_default_with():
    xs: Option[int] = Some(42)
    zs = xs.default_with(lambda: 0)

    assert zs == 42


def test_option_none_default_arg():
    xs = Nothing
    zs = option.default_arg(xs, 42)

    assert zs == 42


def test_option_some_default_arg():
    xs: Option[int] = Some(42)
    zs = option.default_arg(xs, 0)

    assert zs == 42


@given(
    st.one_of(st.integers(), st.text(), st.floats()),  # type: ignore
    st.one_of(st.integers(), st.text(), st.floats()),  # type: ignore
)
def test_option_some_equals_some(a: Any, b: Any):
    xs = Some(a)
    ys = Some(b)

    assert xs == ys if a == b else xs != ys


def test_option_some_map_piped():
    xs = Some(42)
    mapper: Callable[[int], int] = lambda x: x + 1
    ys: Option[int] = xs.pipe(option.map(mapper))

    match ys:
        case Option(tag="some", some=y):
            assert y == 43
        case _:
            assert False


def test_option_none_map_piped():
    xs: Option[int] = Nothing
    mapper: Callable[[int], int] = lambda x: x + 1
    map = option.map(mapper)
    ys = xs.pipe(map)

    assert ys is Nothing


def test_option_some_map_fluent():
    xs = Some(42)
    ys = xs.map(lambda x: x + 1)

    match ys:
        case Option(tag="some", some=value):
            assert value == 43
        case _:
            assert False


def test_option_none_map():
    xs = Nothing
    ys = xs.map(lambda x: x + 1)

    assert ys is Nothing


@given(st.integers(), st.integers())  # type: ignore
def test_option_some_map2_piped(x: int, y: int):
    xs = Some(x)
    ys = Some(y)
    mapper: Callable[[int, int], int] = lambda x, y: x + y
    zs = pipe2((xs, ys), option.map2(mapper))

    match zs:
        case Option(tag="some", some=value):
            assert value == x + y
        case _:
            assert False


def test_option_starmap_fluent():
    xs = Some((42, 43))
    mapper: Callable[[int, int], int] = lambda x, y: x + y
    ys = xs.starmap(mapper)

    match ys:
        case Option(tag="some", some=value):
            assert value == 85
        case _:
            assert False


def test_option_starmap_piped():
    xs = Some((42, 43))
    mapper: Callable[[int, int], int] = lambda x, y: x + y
    ys = pipe(xs, option.starmap(mapper))

    match ys:
        case Option(tag="some", some=value):
            assert value == 85
        case _:
            assert False


def test_option_some_bind_fluent():
    xs = Some(42)
    ys = xs.bind(lambda x: Some(x + 1))

    match ys:
        case Option(tag="some", some=value):
            assert value == 43
        case _:
            assert False


def test_option_some_bind_none_fluent():
    xs = Some(42)
    ys = xs.bind(lambda x: Nothing)

    match ys:
        case Option(tag="none"):
            assert True
        case _:
            assert False


def test_option_none_bind_none_fluent():
    xs = Nothing
    ys = xs.bind(lambda x: Nothing)

    match ys:
        case Option(tag="some"):
            assert False
        case _:
            assert True


def test_option_some_bind_piped():
    binder: Callable[[int], Option[int]] = lambda x: Some(x + 1)
    xs = Some(42)
    ys = xs.pipe(
        option.bind(binder),
    )

    match ys:
        case Option(tag="some", some=value):
            assert value == 43
        case _:
            assert False


def test_option_filter_none():
    xs = Nothing
    assert xs.filter(lambda x: True) == Nothing


def test_option_filter_some():
    xs = Some(42)
    assert xs.filter(lambda x: x > 41) == Some(42)
    assert xs.filter(lambda x: x > 42) == Nothing


def test_option_none_to_list():
    xs = Nothing
    assert xs.to_list() == []


def test_option_some_to_list():
    xs = Some(42)
    assert xs.to_list() == [42]


def test_option_none_to_seq():
    xs = Nothing
    assert list(xs.to_seq()) == []


def test_option_some_to_seq():
    xs = Some(42)
    assert list(xs.to_seq()) == [42]


def test_option_none_to_str():
    xs = Nothing
    assert str(xs) == "Nothing"


def test_option_some_to_str():
    xs = Some(42)
    assert str(xs) == f"Some {xs.value}"


def test_option_none_is_none():
    xs = Nothing
    assert xs.is_none()


def test_option_none_is_some():
    xs = Nothing
    assert not xs.is_some()


def test_option_some_is_none():
    xs = Some(42)
    assert not xs.is_none()


def test_option_some_is_some():
    xs = Some(42)
    assert xs.is_some()


def test_option_of_object_none():
    xs = option.of_obj(None)
    assert xs.is_none()


def test_option_of_object_value():
    xs = option.of_obj(42)
    assert xs.is_some()


def test_option_of_result_ok():
    result: Result[int, Any] = Ok(42)
    xs = option.of_result(result)
    assert xs.is_some()


def test_option_of_result_error():
    xs: Option[int] = option.of_result(Error("oops"))
    assert xs.is_none()


def test_option_to_result_ok():
    xs = option.to_result(Some(42), "oops")
    assert xs == Ok(42)


def test_option_to_result_error():
    xs = option.to_result(Nothing, "oops")
    assert xs == Error("oops")


def test_option_to_result_with_ok():
    def raise_error() -> Any:
        raise Exception("Should not be called")

    xs = option.to_result_with(Some(42), error=raise_error)
    assert xs == Ok(42)


def test_option_to_result_with_error():
    xs = option.to_result_with(Nothing, error=lambda: "oops")
    assert xs == Error("oops")


def test_option_to_optional_some():
    xs = option.to_optional(Some(1))
    assert xs == 1


def test_option_to_optional_nothing():
    xs = option.to_optional(Nothing)
    assert xs is None


def test_option_builder_zero():
    @effect.option[int]()
    def fn():
        while False:
            yield

    xs = fn()
    assert xs is Nothing


def test_option_builder_yield_value():
    @effect.option[int]()
    def fn():
        yield 42

    xs = fn()
    match xs:
        case Option(tag="some", some=value):
            assert value == 42
        case _:
            assert False


def test_option_builder_yield_value_async():
    @effect.option[int]()
    def fn():
        yield 42

    xs = fn()
    match xs:
        case Option(tag="some", some=value):
            assert value == 42
        case _:
            assert False


def test_option_builder_yield_some_wrapped():
    @effect.option[Option[int]]()
    def fn() -> Generator[Option[int], Option[int], Option[int]]:
        x: Option[int] = yield Some(42)
        return x

    xs = fn()
    match xs:
        case Option(tag="some", some=value):
            assert value == Some(42)
        case _:
            assert False


def test_option_builder_return_some():
    @effect.option[int]()
    def fn() -> Generator[int, int, int]:
        x: int = yield 42
        return x

    xs = fn()
    match xs:
        case Option(tag="some", some=value):
            assert value == 42
        case _:
            assert False


def test_option_builder_return_nothing_wrapped():
    @effect.option[Option[int]]()
    def fn():
        return Nothing
        yield

    xs = fn()
    match xs:
        case Option(tag="some", some=value):
            assert value is Nothing
        case _:
            assert False


def test_option_builder_yield_from_some():
    @effect.option[int]()
    def fn() -> Generator[int, int, int]:
        x = yield from Some(42)
        return x + 1

    xs = fn()
    match xs:
        case Option(tag="some", some=value):
            assert value == 43
        case _:
            assert False


def test_option_builder_yield_from_none():
    @effect.option[int]()
    def fn() -> Generator[int, int, int]:
        x: int
        x = yield from Nothing
        return x

    xs = fn()
    assert xs is Nothing


def test_option_builder_multiple_some():
    @effect.option[int]()
    def fn() -> Generator[int, int, int]:
        x: int = yield 42
        y = yield from Some(43)

        return x + y

    xs = fn()
    match xs:
        case Option(tag="some", some=value):
            assert value == 85
        case _:
            assert False


def test_option_builder_none_short_circuits():
    @effect.option[int]()
    def fn() -> Generator[int, int, int]:
        x: int = yield from Nothing
        y = yield from Some(43)

        return x + y

    xs = fn()
    assert xs is Nothing


def test_option_builder_throws():
    error = "do'h"

    @effect.option()
    def fn():
        raise CustomException(error)
        yield

    with pytest.raises(CustomException) as ex:
        fn()

    assert ex.value.message == error


def test_pipeline_none():
    hn = pipeline()

    assert hn(42) == Some(42)


def test_pipeline_works():
    fn: Callable[[int], Option[int]] = lambda x: Some(x * 10)
    gn: Callable[[int], Option[int]] = lambda x: Some(x + 10)

    hn = pipeline(
        fn,
        gn,
    )

    assert hn(42) == Some(430)


def test_pipeline_error():
    fn: Callable[[int], Option[int]] = lambda x: Some(x * 10)
    gn: Callable[[int], Option[int]] = lambda x: Nothing

    hn = pipeline(
        fn,
        gn,
    )

    assert hn(42) == Nothing


PositiveInt = Annotated[int, Field(gt=0)]


class Username(str):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: GetCoreSchemaHandler) -> CoreSchema:
        return core_schema.no_info_after_validator_function(cls, handler(str))


class Model(BaseModel):
    one: Option[int]
    two: Option[str] = Nothing
    three: Option[float] = Nothing
    annotated_type: Option[PositiveInt] = Nothing
    annotated_type_none: Option[PositiveInt] = Nothing

    custom_type: Option[Username] = Nothing
    custom_type_none: Option[Username] = Nothing


def test_parse_option_works():
    obj = dict(
        one=10, two=None, annotated_type=20, annotated_type_none=None, custom_type="test_user", custom_type_none=None
    )
    model = Model.model_validate(obj)

    assert model.one.is_some()
    assert model.one.value == 10
    assert model.two == Nothing
    assert model.three == Nothing
    assert model.custom_type == Some("test_user")
    assert model.annotated_type == Some(20)
    assert model.annotated_type_none == Nothing
    assert model.custom_type_none == Nothing


def test_serialize_option_works():
    model = Model(one=Some(10))
    json = model.model_dump_json()
    assert (
        json
        == '{"one":10,"two":null,"three":null,"annotated_type":null,"annotated_type_none":null,"custom_type":null,"custom_type_none":null}'
    )

    model_ = Model.model_validate_json(json)

    assert model_.one.is_some()
    assert model_.one.value == 10
    assert model_.two == Nothing
    assert model_.three == Nothing


def test_pickle_option_works():
    import pickle

    x = Some(10)
    y = Nothing
    dump_x = pickle.dumps(x)
    load_x = pickle.loads(dump_x)
    dump_y = pickle.dumps(y)
    load_y = pickle.loads(dump_y)
    assert x == load_x
    assert y == load_y


#
