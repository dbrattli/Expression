from typing import Iterable
import pytest
import itertools
from hypothesis import given, strategies as st

from fslash.core import pipe
from fslash.collections import Seq
from fslash.builders import seq


@given(st.lists(st.integers()))
def test_seq_yield(xs):
    @seq
    def fn():
        for x in xs:
            yield x

    ys = fn()

    assert isinstance(ys, Iterable)
    assert [y for y in ys] == xs


@given(st.lists(st.integers()))
def test_seq_pipe_map(xs):
    ys = pipe(xs, Seq.map(lambda x: x + 1))

    assert isinstance(ys, Iterable)
    assert [y for y in ys] == [x + 1 for x in xs]


@given(st.lists(st.integers(), min_size=1))
def test_seq_head_pipe(xs):
    value = pipe(xs, Seq.head)

    assert value == xs[0]


def test_seq_head_empty_source():
    with pytest.raises(ValueError):
        pipe([], Seq.head)


@given(st.lists(st.integers(), min_size=1))
def test_seq_head_fluent(xs):
    value = Seq.of_list(xs).head()

    assert value == xs[0]


@given(st.lists(st.integers(), min_size=1), st.integers())
def test_seq_fold_pipe(xs, s):
    value = pipe(Seq.of_list(xs), Seq.fold(lambda s, v: s + v, s))

    assert value == sum(xs) + s


@given(st.lists(st.integers(), min_size=1), st.integers())
def test_seq_fold_fluent(xs, s):
    value = Seq.of_list(xs).fold(lambda s, v: s + v, s)

    assert value == sum(xs) + s


@given(st.lists(st.integers(), min_size=1), st.integers())
def test_seq_scan_pipe(xs, s):
    func = lambda s, v: s + v
    value = pipe(Seq.of_list(xs), Seq.scan(func, s))

    assert list(value) == list(itertools.accumulate(xs, func, initial=s))


@given(st.lists(st.integers(), min_size=1), st.integers())
def test_seq_scan_fluent(xs, s):
    func = lambda s, v: s + v
    value = Seq.of_list(xs).scan(func, s)

    assert list(value) == list(itertools.accumulate(xs, func, initial=s))


@given(st.lists(st.integers()), st.lists(st.integers()))
def test_seq_concat_pipe(xs, ys):
    value = pipe((xs, ys), Seq.concat())

    assert list(value) == xs + ys


@given(st.lists(st.integers()), st.lists(st.integers()))
def test_seq_concat_pipe2(xs, ys):
    value = pipe([xs], Seq.concat(ys))

    assert list(value) == ys + xs


@given(st.lists(st.integers()), st.lists(st.integers()), st.lists(st.integers()))
def test_seq_concat_pipe3(xs, ys, zs):
    value = pipe([xs, ys], Seq.concat(zs))

    assert list(value) == zs + xs + ys
