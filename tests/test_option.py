from typing import Any, Generator

import pytest
from expression import effect
from expression.core import Nothing, Option, Some, option, pipe, pipe2
from hypothesis import given
from hypothesis import strategies as st
from pampy import _, match

from tests.utils import CustomException


def test_option_some():
    xs = Some(42)

    assert isinstance(xs, Option)
    assert pipe(xs, option.is_some) is True
    assert pipe(xs, option.is_none) is False


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


@given(st.one_of(st.integers(), st.text(), st.floats()), st.one_of(st.integers(), st.text(), st.floats()))
def test_option_some_equals_some(a: Any, b: Any):
    xs = Some(a)
    ys = Some(b)

    assert xs == ys if a == b else xs != ys


def test_option_some_map_piped():
    xs = Some(42)
    ys: Option[int] = xs.pipe(option.map(lambda x: x + 1))

    for y in ys:
        assert y == 43
        break
    else:
        assert False


def test_option_none_map_piped():
    xs: Option[int] = Nothing
    map = option.map(lambda x: x + 1)
    ys = xs.pipe(map)
    assert ys.match(Some, lambda some: False, _, True)


def test_option_some_map_fluent():
    xs = Some(42)
    ys = xs.map(lambda x: x + 1)

    assert ys.match(Some, lambda some: some.value == 43, _, False)


def test_option_none_map():
    xs = Nothing
    ys = xs.map(lambda x: x + 1)

    assert match(ys, Some, lambda some: False, _, True)


@given(st.integers(), st.integers())
def test_option_some_map2_piped(x: int, y: int):
    xs = Some(x)
    ys = Some(y)
    zs = pipe2((xs, ys), option.map2(lambda x, y: x + y))

    assert zs.match(Some, lambda some: some.value, _, False) == x + y


def test_option_some_bind_fluent():
    xs = Some(42)
    ys = xs.bind(lambda x: Some(x + 1))

    assert ys.match(
        Some,
        lambda some: some.value == 43,
        _,
        False,
    )


def test_option_some_bind_none_fluent():
    xs = Some(42)
    ys = xs.bind(lambda x: Nothing)

    assert match(
        ys,
        Some,
        lambda some: False,
        _,
        True,
    )


def test_option_none_bind_none_fluent():
    xs = Nothing
    ys = xs.bind(lambda x: Nothing)

    assert ys.match(
        Some,
        lambda some: False,
        _,
        True,
    )


def test_option_some_bind_piped():
    xs = Some(42)
    ys = xs.pipe(
        option.bind(lambda x: Some(x + 1)),
    )

    assert ys.match(
        Some,
        lambda some: some.value == 43,
        _,
        False,
    )


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
    assert xs.match(
        Some,
        lambda some: False,
        _,
        True,
    )


def test_option_builder_yield_value():
    @effect.option
    def fn():
        yield 42

    xs = fn()
    assert (
        xs.match(
            Some,
            lambda some: some.value,
            _,
            None,
        )
        == 42
    )


def test_option_builder_yield_some_wrapped():
    @effect.option
    def fn() -> Generator[Option[int], Option[int], Option[int]]:
        x = yield Some(42)
        return x

    xs = fn()
    assert Some(42) == xs.match(
        Some,
        lambda some: some.value,
        _,
        None,
    )


def test_option_builder_return_some():
    @effect.option
    def fn() -> Generator[int, int, int]:
        x = yield 42
        return x

    xs = fn()
    assert 42 == xs.match(
        Some,
        lambda some: some.value,
        _,
        None,
    )


def test_option_builder_return_nothing_wrapped():
    @effect.option
    def fn():
        return Nothing
        yield

    xs = fn()
    for x in xs.to_list():
        assert x is Nothing
        break
    else:
        assert False


def test_option_builder_yield_from_some():
    @effect.option
    def fn() -> Generator[int, int, int]:
        x = yield from Some(42)
        return x + 1

    xs = fn()
    assert 43 == match(
        xs,
        Some,
        lambda some: some.value,
        _,
        None,
    )


def test_option_builder_yield_from_none():
    @effect.option
    def fn() -> Generator[int, int, int]:
        x = yield from Nothing
        return x

    xs = fn()
    assert (
        xs.match(
            Some,
            lambda some: some.value,
            _,
            None,
        )
        is None
    )


def test_option_builder_multiple_some():
    @effect.option
    def fn() -> Generator[int, int, int]:
        x = yield 42
        y = yield from Some(43)

        return x + y

    xs = fn()
    assert 85 == xs.match(Some, lambda some: some.value, _, None)


def test_option_builder_none_short_circuits():
    @effect.option
    def fn() -> Generator[int, int, int]:
        x = yield from Nothing
        y = yield from Some(43)

        return x + y

    xs = fn()
    assert xs.match(Some, lambda some: some.value, _, None) is None


def test_option_builder_throws():
    error = "do'h"

    @effect.option
    def fn():
        raise CustomException(error)
        yield

    with pytest.raises(CustomException) as ex:  # type: ignore
        fn()

    assert ex.value.message == error


"""
Idea: for applicative
def gather(a, b):
    return a


def test_option_builder_applicative():
    @effect.option
    def fn():
        x, y = yield from gather(Some(2), Some(43))

        return x + y

    xs = fn()
    assert match(
        xs,
        Some, lambda some: some.value,
        _, None
    ) is None
 """
