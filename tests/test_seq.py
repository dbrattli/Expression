from typing import Iterable
import pytest
from hypothesis import given, strategies as st
from fslash import Seq, seq, pipe
# from pampy import match, _


@given(st.lists(st.integers()))
def test_seq_yield(xs):
    def fn():
        for x in xs:
            yield x

    ys = seq(fn)

    assert(isinstance(ys, Iterable))
    assert([y for y in ys] == xs)


@given(st.lists(st.integers()))
def test_seq_pipe_map(xs):
    ys = pipe(xs, Seq.map(lambda x: x + 1))

    assert(isinstance(ys, Iterable))
    assert([y for y in ys] == [x+1 for x in xs])


@given(st.lists(st.integers(), min_size=1))
def test_seq_head_pipe(xs):
    value = pipe(xs, Seq.head())

    assert(value == xs[0])


def test_seq_head_empty_source():
    with pytest.raises(ValueError):
        pipe([], Seq.head())


@given(st.lists(st.integers(), min_size=1))
def test_seq_head_fluent(xs):
    value = Seq.of_list(xs).head()

    assert(value == xs[0])
