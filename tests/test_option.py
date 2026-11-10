from collections.abc import Callable
from copy import copy, deepcopy
from dataclasses import FrozenInstanceError, asdict, replace
from operator import lt
import json
import pickle

import pytest
from typing import Any, Annotated, assert_type

from hypothesis import given  # type: ignore
from hypothesis import strategies as st
from pydantic import BaseModel, Field, GetCoreSchemaHandler, TypeAdapter, ValidationError
from pydantic_core import CoreSchema, core_schema

from expression import (
    Error,
    Nothing,
    Ok,
    Option,
    Result,
    Some,
    option,
    pipe,
    pipe2,
)
from expression.core.option import Nothing
from expression.extra.option import pipeline


def test_option_some():
    xs = Some(42)

    assert isinstance(xs, Some)
    assert pipe(xs, option.is_some) is True
    assert pipe(xs, option.is_none) is False


def test_option_some_match():
    xs = Some(42)

    match xs:
        case Some(some=x):
            assert x == 42

        case _:
            assert False


def test_option_some_match_fluent():
    xs = Some(42)
    ys = xs.map(lambda x: x + 1)

    match ys:
        case Some(some=value):
            assert value == 43
        case _:
            assert False


def test_option_apply():
    value: Option[int] = Some(2)
    function: Option[Callable[[int], int]] = Some(lambda x: x + 1)

    assert value.apply(function) == Some(3)
    assert value.pipe(option.apply(function)) == Some(3)


def test_option_apply_nothing():
    value: Option[int] = Some(2)
    function: Option[Callable[[int], int]] = Some(lambda x: x + 1)

    assert Nothing().apply(function) == Nothing()
    assert value.apply(Nothing()) == Nothing()


def test_option_some_iterate_to_list():
    xs = Some(42)

    for x in xs.to_list():
        assert x == 42
        break
    else:
        assert False


def test_option_some_iterate():
    xs = Some(42)

    for x in xs:
        assert x == 42
        break
    else:
        assert False


def test_option_none():
    xs = Nothing()

    assert isinstance(xs, Nothing)
    assert xs.pipe(option.is_some) is False
    assert xs.pipe(option.is_none) is True


def test_option_none_match():
    xs = Nothing()

    match xs:
        case x if x is Nothing():
            assert True

        case _:
            assert False


def test_option_nothing_iterate():
    xs = Nothing()

    for _ in option.to_list(xs):
        assert False


def test_option_none_equals_none():
    xs = Nothing()
    ys = Nothing()

    assert xs == ys


def test_option_none_not_equals_some():
    xs = Some(42)
    ys = Nothing()

    assert xs != ys
    assert ys != xs


@pytest.mark.parametrize("left,right", [(Some(42), Some(41)), (Some(42), Nothing()), (Nothing(), Nothing())])
def test_options_have_no_implicit_order(left: Any, right: Any):
    with pytest.raises(TypeError):
        lt(left, right)


def test_option_none_default_value():
    xs: Option[int] = Nothing()

    zs = xs.default_value(42)

    assert zs == 42


def test_option_some_default_value():
    xs: Option[int] = Some(42)
    zs = xs.default_value(0)

    assert zs == 42


def test_option_none_default_with():
    xs = Nothing()

    zs = xs.default_with(lambda: 42)

    assert zs == 42


def test_option_some_default_with():
    xs: Option[int] = Some(42)
    zs = xs.default_with(lambda: 0)

    assert zs == 42


def test_option_none_default_arg():
    xs = Nothing()
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
        case Some(some=y):
            assert y == 43
        case _:
            assert False


def test_option_none_map_piped():
    xs: Option[int] = Nothing()
    mapper: Callable[[int], int] = lambda x: x + 1
    map = option.map(mapper)
    ys = xs.pipe(map)

    assert ys is Nothing()


def test_option_some_map_fluent():
    xs = Some(42)
    ys = xs.map(lambda x: x + 1)

    match ys:
        case Some(some=value):
            assert value == 43
        case _:
            assert False


def test_option_none_map():
    xs = Nothing()
    ys = xs.map(lambda x: x + 1)

    assert ys is Nothing()


@given(st.integers(), st.integers())  # type: ignore
def test_option_some_map2_piped(x: int, y: int):
    xs = Some(x)
    ys = Some(y)
    mapper: Callable[[int, int], int] = lambda x, y: x + y
    zs = pipe2((xs, ys), option.map2(mapper))

    match zs:
        case Some(some=value):
            assert value == x + y
        case _:
            assert False


def test_option_starmap_fluent():
    xs = Some((42, 43))
    mapper: Callable[[int, int], int] = lambda x, y: x + y
    ys = xs.starmap(mapper)

    match ys:
        case Some(some=value):
            assert value == 85
        case _:
            assert False


def test_option_starmap_piped():
    xs = Some((42, 43))
    mapper: Callable[[int, int], int] = lambda x, y: x + y
    ys = pipe(xs, option.starmap(mapper))

    match ys:
        case Some(some=value):
            assert value == 85
        case _:
            assert False


def test_option_some_bind_fluent():
    xs = Some(42)
    ys = xs.bind(lambda x: Some(x + 1))

    match ys:
        case Some(some=value):
            assert value == 43
        case _:
            assert False


def test_option_some_bind_none_fluent():
    xs = Some(42)
    ys = xs.bind(lambda x: Nothing())

    match ys:
        case Nothing():
            assert True
        case _:
            assert False


def test_option_none_bind_none_fluent():
    xs = Nothing()
    ys = xs.bind(lambda x: Nothing())

    assert ys is Nothing()


def test_option_some_bind_piped():
    binder: Callable[[int], Option[int]] = lambda x: Some(x + 1)
    xs = Some(42)
    ys = xs.pipe(
        option.bind(binder),
    )

    match ys:
        case Some(some=value):
            assert value == 43
        case _:
            assert False


def test_option_filter_none():
    xs = Nothing()
    assert xs.filter(lambda x: True) == Nothing()


def test_option_filter_some():
    xs = Some(42)
    assert xs.filter(lambda x: x > 41) == Some(42)
    assert xs.filter(lambda x: x > 42) == Nothing()


def test_option_none_to_list():
    xs = Nothing()
    assert xs.to_list() == []


def test_option_some_to_list():
    xs = Some(42)
    assert xs.to_list() == [42]


def test_option_none_to_seq():
    xs = Nothing()
    assert list(xs.to_seq()) == []


def test_option_some_to_seq():
    xs = Some(42)
    assert list(xs.to_seq()) == [42]


def test_option_none_to_str():
    xs = Nothing()
    assert str(xs) == "Nothing"


def test_option_some_to_str():
    xs = Some(42)
    assert str(xs) == f"Some {xs.value}"


def test_option_none_is_none():
    xs = Nothing()
    assert xs.is_none()


def test_option_none_is_some():
    xs = Nothing()
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
    xs = option.to_result(Nothing(), "oops")
    assert xs == Error("oops")


def test_option_to_result_with_ok():
    def raise_error() -> Any:
        raise Exception("Should not be called")

    xs = option.to_result_with(Some(42), error=raise_error)
    assert xs == Ok(42)


def test_option_to_result_with_error():
    xs = option.to_result_with(Nothing(), error=lambda: "oops")
    assert xs == Error("oops")


def test_option_to_optional_some():
    xs = option.to_optional(Some(1))
    assert xs == 1


def test_option_to_optional_nothing():
    xs = option.to_optional(Nothing())
    assert xs is None


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
    gn: Callable[[int], Option[int]] = lambda x: Nothing()

    hn = pipeline(
        fn,
        gn,
    )

    assert hn(42) == Nothing()


PositiveInt = Annotated[int, Field(gt=0)]


class Username(str):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: GetCoreSchemaHandler) -> CoreSchema:
        return core_schema.no_info_after_validator_function(cls, handler(str))


class Model(BaseModel):
    one: Option[int]
    two: Option[str] = Nothing()
    three: Option[float] = Nothing()
    annotated_type: Option[PositiveInt] = Nothing()
    annotated_type_none: Option[PositiveInt] = Nothing()

    custom_type: Option[Username] = Nothing()
    custom_type_none: Option[Username] = Nothing()


class TupleModel(BaseModel):
    values: Option[tuple[int, ...]]


def test_parse_option_works():
    obj = dict(
        one={"tag": "some", "some": 10},
        two={"tag": "none"},
        annotated_type={"tag": "some", "some": 20},
        annotated_type_none={"tag": "none"},
        custom_type={"tag": "some", "some": "test_user"},
        custom_type_none={"tag": "none"},
    )
    model = Model.model_validate(obj)

    assert model.one.is_some()
    assert model.one.value == 10
    assert model.two == Nothing()
    assert model.three == Nothing()
    assert model.custom_type == Some("test_user")
    assert model.annotated_type == Some(20)
    assert model.annotated_type_none == Nothing()
    assert model.custom_type_none == Nothing()


def test_parse_option_tuple_works():
    model = TupleModel.model_validate({"values": {"tag": "some", "some": [1, 2, 3]}})

    assert model.values == Some((1, 2, 3))


def test_serialize_option_works():
    model = Model(one=Some(10))
    encoded = model.model_dump_json()
    assert json.loads(encoded) == {
        "one": {"tag": "some", "some": 10},
        "two": {"tag": "none"},
        "three": {"tag": "none"},
        "annotated_type": {"tag": "none"},
        "annotated_type_none": {"tag": "none"},
        "custom_type": {"tag": "none"},
        "custom_type_none": {"tag": "none"},
    }
    model_ = Model.model_validate_json(encoded)

    assert model_.one.is_some()
    assert model_.one.value == 10
    assert model_.two == Nothing()
    assert model_.three == Nothing()


class A:
    pass


class B(A):
    pass


def test_option_covariance() -> None:
    x: Option[B] = Some(B())
    y: Option[A] = x

    assert y.is_some()


def test_pickle_option_works():
    import pickle

    x = Some(10)
    y = Nothing()
    dump_x = pickle.dumps(x)
    load_x = pickle.loads(dump_x)
    dump_y = pickle.dumps(y)
    load_y = pickle.loads(dump_y)
    assert x == load_x
    assert y == load_y


def test_nothing_iteration_is_empty():
    assert list(Nothing()) == []
    assert list(Some(None)) == [None]


def test_nothing_is_canonical_across_dataclass_operations():
    empty = Nothing()
    assert isinstance(empty, Nothing)
    assert Nothing() is empty
    assert repr(empty) == "Nothing()"
    assert copy(Nothing()) is Nothing()
    assert deepcopy(Nothing()) is Nothing()
    assert replace(Nothing()) is Nothing()
    assert pickle.loads(pickle.dumps(Nothing())) is Nothing()


def test_case_fields_and_frozen_values():
    assert Some.__match_args__ == ("some",)
    assert Nothing.__match_args__ == ()
    assert asdict(Some(1)) == {"some": 1, "tag": "some"}
    assert replace(Some(1), some=2) == Some(2)
    assert hash(Some(1)) == hash(Some(1))
    with pytest.raises(TypeError):
        hash(Some([]))
    with pytest.raises(FrozenInstanceError):
        setattr(Some(1), "some", 2)
    with pytest.raises(AttributeError):
        getattr(Nothing(), "some")
    with pytest.raises(ValueError):
        _ = Nothing().value


def test_case_subclassing_is_rejected():
    for case_type in (Some, Nothing):
        with pytest.raises(TypeError, match="final"):
            type("Extra", (case_type,), {})


def test_tagged_none_payload_and_nesting_roundtrip():
    adapter = TypeAdapter(Option[Option[int | None]])
    cases: list[Option[Option[int | None]]] = [Nothing(), Some(Nothing()), Some(Some(None)), Some(Some(1))]
    encoded = [adapter.dump_json(value) for value in cases]
    assert len(set(encoded)) == len(cases)
    assert [adapter.validate_json(value) for value in encoded] == cases
    assert adapter.validate_json(b'{"tag":"none"}') is Nothing()
    assert option.model_dump(Some(None)) == {"tag": "some", "some": None}
    assert option.model_dump(Some(Nothing())) == {"tag": "some", "some": {"tag": "none"}}
    assert option.model_dump(Some(Some(1))) == {"tag": "some", "some": {"tag": "some", "some": 1}}


@pytest.mark.parametrize(
    "data",
    [
        {"tag": "some", "some": "bad"},
        {"tag": "none", "some": 1},
        {"tag": "unknown", "some": 1},
        {"tag": "some"},
        {"some": 1},
        None,
        1,
    ],
)
def test_invalid_tagged_options_are_rejected(data: object):
    with pytest.raises(ValidationError):
        TypeAdapter(Option[int]).validate_python(data)


def test_option_tagged_schema_has_discriminator():
    schema = TypeAdapter(Option[int]).json_schema()
    assert schema["discriminator"]["propertyName"] == "tag"
    assert set(schema["discriminator"]["mapping"]) == {"some", "none"}


def test_option_revalidates_existing_generic_payload():
    with pytest.raises(ValidationError):
        TypeAdapter(Option[int]).validate_python(Some("not an integer"))


def test_constructor_does_not_accept_a_tag():
    constructor: Any = Some
    with pytest.raises(TypeError):
        constructor(1, tag="none")


def test_option_container_is_not_awaitable():
    import inspect

    assert not inspect.isawaitable(Some(1))
    assert not inspect.isawaitable(Nothing())


def test_option_pipeline_defaults_preserve_payload_and_fallback_types():
    calls: list[str] = []

    def fallback() -> str:
        calls.append("fallback")
        return "missing"

    def consume(value: Option[int]) -> int | str:
        assert_type(value.pipe(option.default_value("missing")), int | str)
        assert_type(value.pipe(option.default_with(fallback)), int | str)
        return value.pipe(option.default_with(fallback))

    assert consume(Some(42)) == 42
    assert calls == []
    assert consume(Nothing()) == "missing"
    assert calls == ["fallback", "fallback"]
    assert_type(Some(None).pipe(option.default_with(fallback)), None)
    assert Some(None).pipe(option.default_with(fallback)) is None
    assert calls == ["fallback", "fallback"]


def test_option_pipeline_empty_channels_and_conversions():
    from expression.collections import Seq

    def absent(value: int) -> Nothing:
        return Nothing()

    def consume(value: Option[int]) -> None:
        assert_type(value.pipe(option.bind(absent)), Nothing)
        assert value.pipe(option.bind(absent)) is Nothing()
        assert_type(value.pipe(option.apply(Nothing())), Nothing)
        assert value.pipe(option.apply(Nothing())) is Nothing()
        assert_type(value.pipe(option.to_optional), int | None)
        assert_type(pipe(value, option.to_list), list[int])
        assert_type(pipe(value, option.to_seq), Seq[int])
        assert_type(option.to_list(value), list[int])
        values: list[int] = value.to_list()
        assert values == pipe(value, option.to_list)
        assert list(pipe(value, option.to_seq)) == values

    consume(Some(42))
    consume(Nothing())


def test_option_starmap_typed_callback_preserves_union_payload():
    def repeat(number: int, text: str) -> str:
        return text * number

    def consume(value: Option[tuple[int, str]]) -> Option[str]:
        assert_type(value.starmap(repeat), Option[str])
        assert_type(value.pipe(option.starmap(repeat)), Option[str])
        return value.starmap(repeat)

    assert consume(Some((3, "x"))) == Some("xxx")
    assert consume(Nothing()) is Nothing()
