from typing import Callable, Dict, ItemsView, Iterable, List, Tuple

from hypothesis import given  # type: ignore
from hypothesis import strategies as st

from expression import Some, pipe
from expression.collections import Block, Map, map
from expression.core.option import Some


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
def test_map_create(xs: Dict[str, int]):
    items: Iterable[Tuple[str, int]] = xs.items()
    m = map.create(items)
    assert len(m) == len(xs)


@given(st.dictionaries(keys=st.text(), values=st.integers()))
def test_map_of_seq(xs: Dict[str, int]):
    items: ItemsView[str, int] = xs.items()
    m = map.of_seq(items)
    assert len(m) == len(xs)


@given(st.dictionaries(keys=st.text(), values=st.integers()))
def test_map_to_list_fluent(xs: Dict[str, int]):
    items: ItemsView[str, int] = xs.items()
    ys = map.of_seq(items).to_list()
    assert sorted(xs.items()) == sorted(ys)


@given(st.dictionaries(keys=st.text(), values=st.integers()))
def test_map_to_seq(xs: Dict[str, int]):
    items: List[Tuple[str, int]] = list(xs.items())
    ys = map.of_list(items)
    zs = pipe(ys, map.to_seq)
    assert sorted(list(items)) == list(zs)


@given(st.dictionaries(keys=st.text(), values=st.integers()))
def test_map_remove_fluent(xs: Dict[str, int]):
    items: ItemsView[str, int] = xs.items()
    m = Map.of_seq(items)

    keys = xs.keys()
    count = len(m)
    for key in keys:
        m = m.remove(key)
        count -= 1
    assert len(m) == count == 0


@given(st.dictionaries(keys=st.text(), values=st.integers()))
def test_map_remove(xs: Dict[str, int]):
    items: ItemsView[str, int] = xs.items()
    m = Map.of_seq(items)

    keys = xs.keys()
    count = len(m)
    for key in keys:
        m = pipe(m, map.remove(key))
        count -= 1
    assert len(m) == count == 0


@given(st.dictionaries(keys=st.text(), values=st.integers()))
def test_map_to_seq_fluent(xs: Dict[str, int]):
    items: ItemsView[str, int] = xs.items()
    ys = map.of_seq(items).to_seq()

    assert sorted(list(items)) == list(ys)


@given(st.dictionaries(keys=st.text(), values=st.integers()))
def test_map_to_list(xs: Dict[str, int]):
    items = Block(xs.items())
    ys = map.of_block(items).to_seq()

    assert sorted(list(items)) == list(ys)


@given(st.dictionaries(keys=st.text(), values=st.integers()))
def test_map_map(xs: Dict[str, int]):
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
def test_map_count(xs: Dict[str, int]):
    ys: Map[str, int] = map.of(**xs)

    assert len(ys) == len(xs) == map.count(ys)


@given(st.dictionaries(keys=st.text(), values=st.integers()))
def test_map_iterate(xs: Dict[str, int]):
    ys = [k for k in map.of(**xs)]

    assert sorted(ys) == sorted(list(xs.keys()))


def test_map_change_empty():
    xs = (  # type: ignore
        Map.empty()
        .change(1, lambda _: Some(1))  # type: ignore
        .change(2, lambda _: Some(2))  # type: ignore
        .change(3, lambda _: Some(3))  # type: ignore
    )  # type: ignore

    assert xs == Map.of_seq([(1, 1), (2, 2), (3, 3)])


def test_expression_change_non_empty():
    m: Map[str, int] = Map.empty()
    m = m.add("1", 1).add("2", 2).add("3", 3).add("4", 4)
    m = m.change("2", lambda x: Some(0))  # <- works cause "2" is second added item
    m = m.change("1", lambda x: Some(42))
    m = m.change("3", lambda x: x)

    assert m == Map.of_list([("1", 42), ("2", 0), ("3", 3), ("4", 4)])


def test_map_change():
    d_1 = {"a": 1, "b": 3}
    d_2 = {"some": 0, "values": -1}
    key_1 = "1"
    key_2 = "2"
    m: Map[str, Dict[str, int]] = Map.empty()
    m = (
        m.add(key_1, d_1)
        .add(key_2, d_2)
        .add("3", {})
        .add("4", {})
        .add("5", {})
        .add("6", {})
        .add("7", {})
    )
    m = m.change(key_2, lambda x: Some({**x.value, "other": 42}))
    m = m.change(key_1, lambda x: Some({**x.value, "some key": 5}))

    def verify(
        original: Dict[str, int], map_key: str, override_key: str, override_value: int
    ):
        value = m.get(map_key)
        assert value
        assert override_key in value
        for k, v in value.items():
            if k == override_key:
                assert v == override_value
            else:
                assert v == original[k]

    verify(d_1, key_1, "some key", 5)
    verify(d_2, key_2, "other", 42)
