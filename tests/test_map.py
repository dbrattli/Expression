from collections.abc import Callable, ItemsView, Iterable

from hypothesis import given  # type: ignore
from hypothesis import strategies as st

from expression import Some, pipe
from expression.collections import Block, Map, map


def test_map_empty():
    m: Map[str, int] = map.empty
    assert map.is_empty(m)
    assert len(m) == 0
    assert not m


def test_map_non_empty():
    m: Map[str, int] = map.empty.add("test", 42)
    assert not map.is_empty(m)
    assert len(m) == 1
    assert m


@given(st.dictionaries(keys=st.text(), values=st.integers()))
def test_map_create(xs: dict[str, int]):
    items: Iterable[tuple[str, int]] = xs.items()
    m = map.create(items)
    assert len(m) == len(xs)


@given(st.dictionaries(keys=st.text(), values=st.integers()))
def test_map_of_seq(xs: dict[str, int]):
    items: ItemsView[str, int] = xs.items()
    m = map.of_seq(items)
    assert len(m) == len(xs)


@given(st.dictionaries(keys=st.text(), values=st.integers()))
def test_map_to_list_fluent(xs: dict[str, int]):
    items: ItemsView[str, int] = xs.items()
    ys = map.of_seq(items).to_list()
    assert sorted(xs.items()) == sorted(ys)


@given(st.dictionaries(keys=st.text(), values=st.integers()))
def test_map_to_seq(xs: dict[str, int]):
    items: list[tuple[str, int]] = list(xs.items())
    ys = map.of_list(items)
    zs = pipe(ys, map.to_seq)
    assert sorted(list(items)) == list(zs)


@given(st.dictionaries(keys=st.text(), values=st.integers()))
def test_map_remove_fluent(xs: dict[str, int]):
    items: ItemsView[str, int] = xs.items()
    m = Map.of_seq(items)

    keys = xs.keys()
    count = len(m)
    for key in keys:
        m = m.remove(key)
        count -= 1
    assert len(m) == count == 0


@given(st.dictionaries(keys=st.text(), values=st.integers()))
def test_map_remove(xs: dict[str, int]):
    items: ItemsView[str, int] = xs.items()
    m = Map.of_seq(items)

    keys = xs.keys()
    count = len(m)
    for key in keys:
        m = pipe(m, map.remove(key))
        count -= 1
    assert len(m) == count == 0


@given(st.dictionaries(keys=st.text(), values=st.integers()))
def test_map_to_seq_fluent(xs: dict[str, int]):
    items: ItemsView[str, int] = xs.items()
    ys = map.of_seq(items).to_seq()

    assert sorted(list(items)) == list(ys)


@given(st.dictionaries(keys=st.text(), values=st.integers()))
def test_map_to_list(xs: dict[str, int]):
    items = Block(xs.items())
    ys = map.of_block(items).to_seq()

    assert sorted(list(items)) == list(ys)


@given(st.dictionaries(keys=st.text(), values=st.integers()))
def test_map_map(xs: dict[str, int]):
    items = Block(xs.items())

    mapper: Callable[[str, int], int] = lambda k, v: v * 20
    ys = map.of_block(items).map(mapper)

    expected = [(k, mapper(k, v)) for k, v in sorted(list(items))]
    assert expected == list(ys.to_list())


def test_map_pipe_fluent():
    xs = map.of(a=1, b=2)
    mapper: Callable[[str, int], int] = lambda k, v: v * 10
    ys = xs.pipe(map.map(mapper))

    assert ys == map.of(a=10, b=20)


@given(st.dictionaries(keys=st.text(), values=st.integers()))
def test_map_count(xs: dict[str, int]):
    ys: Map[str, int] = map.of(**xs)

    assert len(ys) == len(xs) == map.count(ys)


@given(st.dictionaries(keys=st.text(), values=st.integers()))
def test_map_iterate(xs: dict[str, int]):
    ys = [k for k in map.of(**xs)]

    assert sorted(ys) == sorted(list(xs.keys()))


def test_map_change():
    xs = (
        Map.empty()
        .change(1, lambda _: Some(1))  # type: ignore
        .change(2, lambda _: Some(2))  # type: ignore
        .change(3, lambda _: Some(3))  # type: ignore
    )  # type: ignore

    assert xs == Map.of_seq([(1, 1), (2, 2), (3, 3)])


def test_map_try_get_value():
    values: list[int] = []
    xs = Map.of(a=1, b=2)
    assert xs.try_get_value("a", values) is True
    assert xs.try_get_value("b", values) is True
    assert xs.try_get_value("c", values) is False
    assert values == [1, 2]

def test_expression_issue_105():
    m = Map[str, int].empty()
    m = m.add("1", 1).add("2", 2).add("3", 3).add("4", 4)
    m = m.change("2", lambda x: x)
    m = m.change("3", lambda x: x)