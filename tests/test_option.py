from typing import Any, Callable, Generator

import pytest
from hypothesis import given
from hypothesis import strategies as st

from expression import Nothing, Option, Some, effect, match, option, pipe, pipe2
from expression.extra.option import pipeline
from tests.utils import CustomException


def test_option_some():
    xs = Some(42)

    assert isinstance(xs, Option)
    assert pipe(xs, option.is_some) is True
    assert pipe(xs, option.is_none) is False


def test_option_some_match():
    xs = Some(42)

    with match(xs) as case:
        for x in case(Some[int]):
            assert x == 42

        while case.default():
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

    with match(xs) as case:
        for _ in case(Some[int]):
            assert False

        while case(Nothing):
            assert True

        while case.default():
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


def test_option_none_default_value():
    xs = Nothing

    zs = xs.default_value(42)

    assert zs == 42


def test_option_some_default_value():
    xs: Option[int] = Some(42)
    zs = xs.default_value(0)

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
    st.one_of(st.integers(), st.text(), st.floats()), st.one_of(st.integers(), st.text(), st.floats())  # type: ignore
)
def test_option_some_equals_some(a: Any, b: Any):
    xs = Some(a)
    ys = Some(b)

    assert xs == ys if a == b else xs != ys


def test_option_some_map_piped():
    xs = Some(42)
    mapper: Callable[[int], int] = lambda x: x + 1
    ys: Option[int] = xs.pipe(option.map(mapper))

    for y in ys.match(Some):
        assert y == 43
        break
    else:
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

    for value in ys.match(Some):
        assert value == 43
        break
    else:
        assert False


def test_option_none_map():
    xs = Nothing
    ys = xs.map(lambda x: x + 1)

    assert ys is Nothing


@given(st.integers(), st.integers())
def test_option_some_map2_piped(x: int, y: int):
    xs = Some(x)
    ys = Some(y)
    mapper: Callable[[int, int], int] = lambda x, y: x + y
    zs = pipe2((xs, ys), option.map2(mapper))

    for value in zs.match(Some):
        assert value == x + y
        break
    else:
        assert False


def test_option_some_bind_fluent():
    xs = Some(42)
    ys = xs.bind(lambda x: Some(x + 1))

    for value in ys.match(Some):
        assert value == 43
        break
    else:
        assert False


def test_option_some_bind_none_fluent():
    xs = Some(42)
    ys = xs.bind(lambda x: Nothing)

    for _ in ys.match(Nothing):
        assert True
        break
    else:
        assert False


def test_option_none_bind_none_fluent():
    xs = Nothing
    ys = xs.bind(lambda x: Nothing)

    for _ in ys.match(Some):
        assert False
    else:
        assert True


def test_option_some_bind_piped():
    binder: Callable[[int], Option[int]] = lambda x: Some(x + 1)
    xs = Some(42)
    ys = xs.pipe(
        option.bind(binder),
    )

    for value in ys.match(Some):
        assert value == 43
        break
    else:
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


def test_option_builder_zero():
    @effect.option
    def fn():
        while False:
            yield

    xs = fn()
    assert xs is Nothing


def test_option_builder_yield_value():
    @effect.option
    def fn():
        yield 42

    xs = fn()
    for value in xs.match(Some):
        assert value == 42
        break
    else:
        assert False


def test_option_builder_yield_value_async():
    @effect.option
    def fn():
        yield 42

    xs = fn()
    for value in xs.match(Some):
        assert value == 42
        break
    else:
        assert False


def test_option_builder_yield_some_wrapped():
    @effect.option
    def fn() -> Generator[Option[int], Option[int], Option[int]]:
        x = yield Some(42)
        return x

    xs = fn()
    for value in xs.match(Some):
        assert value == Some(42)
        break
    else:
        assert False


def test_option_builder_return_some():
    @effect.option
    def fn() -> Generator[int, int, int]:
        x = yield 42
        return x

    xs = fn()
    for value in xs.match(Some):
        assert value == 42
        break
    else:
        assert False


def test_option_builder_return_nothing_wrapped():
    @effect.option
    def fn():
        return Nothing
        yield

    xs = fn()
    for value in xs.match(Some):
        assert value is Nothing
        break
    else:
        assert False


def test_option_builder_yield_from_some():
    @effect.option
    def fn() -> Generator[int, int, int]:
        x = yield from Some(42)
        return x + 1

    xs = fn()
    for value in xs.match(Some):
        assert value == 43
        break
    else:
        assert False


def test_option_builder_yield_from_none():
    @effect.option
    def fn() -> Generator[int, int, int]:
        x: int
        x = yield from Nothing
        return x

    xs = fn()
    assert xs is Nothing


def test_option_builder_multiple_some():
    @effect.option
    def fn() -> Generator[int, int, int]:
        x = yield 42
        y = yield from Some(43)

        return x + y

    xs = fn()
    for value in xs.match(Some):
        assert value == 85
        break
    else:
        assert False


def test_option_builder_none_short_circuits():
    @effect.option
    def fn() -> Generator[int, int, int]:
        x: int
        x = yield from Nothing
        y = yield from Some(43)

        return x + y

    xs = fn()
    assert xs is Nothing


def test_option_builder_throws():
    error = "do'h"

    @effect.option
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
