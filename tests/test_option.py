from hypothesis import given, strategies as st
from pampy import match, _

from fslash.core import Option, TOption, Some, Nothing, pipe, option


def test_option_some():
    xs = Some(42)

    assert isinstance(xs, TOption)
    assert pipe(xs, Option.is_some()) is True
    assert pipe(xs, Option.is_none()) is False


def test_option_none():
    xs = Nothing

    assert isinstance(xs, TOption)
    assert pipe(xs, Option.is_some()) is False
    assert pipe(xs, Option.is_none()) is True


def test_option_none_equals_none():
    xs = Nothing
    ys = Nothing

    assert(xs == ys)


def test_option_none_not_equals_some():
    xs = Some(42)
    ys = Nothing

    assert(xs != ys)


@given(st.one_of(st.integers(), st.text(), st.floats()), st.one_of(st.integers(), st.text(), st.floats()))
def test_option_some_equals_some(a, b):
    xs = Some(a)
    ys = Some(b)

    assert(xs == ys if a == b else xs != ys)


def test_option_some_map_piped():
    xs = Some(42)
    ys = pipe(xs, Option.map(lambda x: x + 1))

    assert match(
        ys,
        Some, lambda some: some.value == 43,
        _, False
    )


def test_option_none_map_piped():
    xs = Nothing
    map = Option.map(lambda x: x + 1)
    ys = pipe(xs, map)
    assert match(
        ys,
        Some, lambda some: False,
        _, True
    )


def test_option_some_map_fluent():
    xs = Some(42)
    ys = xs.map(lambda x: x + 1)

    assert match(
        ys,
        Some, lambda some: some.value == 43,
        _, False
    )


def test_option_none_map():
    xs = Nothing
    ys = xs.map(lambda x: x + 1)

    assert match(
        ys,
        Some, lambda some: False,
        _, True
    )


def test_option_some_bind_fluent():
    xs = Some(42)
    ys = xs.bind(lambda x: Some(x + 1))

    assert match(
        ys,
        Some, lambda some: some.value == 43,
        _, False
    )


def test_option_some_bind_none_fluent():
    xs = Some(42)
    ys = xs.bind(lambda x: Nothing)

    assert match(
        ys,
        Some, lambda some: False,
        _, True
    )


def test_option_none_bind_none_fluent():
    xs = Nothing
    ys = xs.bind(lambda x: Nothing)

    assert match(
        ys,
        Some, lambda some: False,
        _, True
    )


def test_option_some_bind_piped():
    xs = Some(42)
    ys = pipe(xs, Option.bind(lambda x: Some(x + 1)))

    assert match(
        ys,
        Some, lambda some: some.value == 43,
        _, False
    )


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


def test_option_builder_zero():
    @option
    def fn():
        yield

    xs = fn()
    assert match(
        xs,
        Some, lambda some: False,
        _, True
    )


def test_option_builder_yield_some():
    @option
    def fn():
        yield 42

    xs = fn()
    assert 42 == match(
        xs,
        Some, lambda some: some.value,
        _, None
    )


def test_option_builder_return_some():
    @option
    def fn():
        x = yield 42
        return x

    xs = fn()
    assert 42 == match(
        xs,
        Some, lambda some: some.value,
        _, None
    )


def test_option_builder_return_none():
    """FIXME: result should be Some(Nothing)"""
    @option
    def fn():
        return Nothing

    xs = fn()
    assert match(
        xs,
        Some, lambda some: some.value,
        _, None
    ) is None


def test_option_builder_yield_from_some():
    @option
    def fn():
        x = yield from Some(42)
        return x + 1

    xs = fn()
    assert 43 == match(
        xs,
        Some, lambda some: some.value,
        _, None
    )


def test_option_builder_yield_from_none():
    @option
    def fn():
        x = yield from Nothing
        return x

    xs = fn()
    assert match(
        xs,
        Some, lambda some: some.value,
        _, None
    ) is None


def test_option_builder_multiple_some():
    @option
    def fn():
        x = yield 42
        y = yield from Some(43)

        return x + y

    xs = fn()
    assert 85 == match(
        xs,
        Some, lambda some: some.value,
        _, None
    )


def test_option_builder_none_short_circuits():
    @option
    def fn():
        x = yield from Nothing
        y = yield from Some(43)

        return x + y

    xs = fn()
    assert match(
        xs,
        Some, lambda some: some.value,
        _, None
    ) is None
