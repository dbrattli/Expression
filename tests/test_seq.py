import functools
from itertools import accumulate
from typing import Callable, Generator, Iterable, List

import pytest
from expression import effect
from expression.collections import Seq, seq
from expression.core import pipe
from hypothesis import given
from hypothesis import strategies as st


def test_seq_empty():
    @effect.seq
    def fn() -> Generator[None, None, None]:
        while False:
            yield

    ys = fn()

    assert isinstance(ys, Iterable)
    assert list(ys) == []


def test_seq_yield():
    @effect.seq
    def fn():
        yield 42

    ys = fn()

    assert list(ys) == [42]


@given(st.lists(st.integers(), max_size=10))
def test_seq_yield_for_in(xs: List[int]):
    @effect.seq
    def fn():
        for x in xs:
            yield x

    ys = fn()

    assert list(ys) == xs


# @given(st.lists(st.integers(), min_size=1, max_size=10))
# def test_seq_yield_from(xs):
#     @seq
#     def fn():
#         x = yield from xs
#         print(x)
#         return x + 1

#     ys = fn()

#     assert list(ys) == [x + 1 for x in xs]


@given(st.lists(st.integers()))
def test_seq_pipe_map(xs: List[int]):
    mapper: Callable[[int], int] = lambda x: x + 1
    ys = pipe(xs, seq.map(mapper))

    assert isinstance(ys, Iterable)
    assert [y for y in ys] == [x + 1 for x in xs]


@given(st.lists(st.integers(), min_size=1))
def test_seq_head_pipe(xs: List[int]):
    value = pipe(xs, seq.head)

    assert value == xs[0]


def test_seq_head_empty_source():
    with pytest.raises(ValueError):
        pipe([], seq.head)


@given(st.lists(st.integers(), min_size=1))
def test_seq_head_fluent(xs: List[int]):
    value = seq.of(xs).head()

    assert value == xs[0]


@given(st.lists(st.integers(), min_size=1), st.integers())
def test_seq_fold_pipe(xs: List[int], s: int):
    folder: Callable[[int, int], int] = lambda s, v: s + v
    value = pipe(seq.of(xs), seq.fold(folder, s))

    assert value == sum(xs) + s


@given(st.lists(st.integers(), min_size=1), st.integers())
def test_seq_fold_fluent(xs: List[int], s: int):
    value = seq.of(xs).fold(lambda s, v: s + v, s)

    assert value == sum(xs) + s


@given(st.lists(st.integers(), min_size=1), st.integers())
def test_seq_scan_pipe(xs: List[int], s: int):
    func: Callable[[int, int], int] = lambda s, v: s + v
    value = pipe(seq.of(xs), seq.scan(func, s))

    assert list(value) == list(accumulate(xs, func, initial=s))


@given(st.lists(st.integers(), min_size=1), st.integers())
def test_seq_scan_fluent(xs: List[int], s: int):
    func: Callable[[int, int], int] = lambda s, v: s + v
    value = seq.of(xs).scan(func, s)

    assert list(value) == list(accumulate(xs, func, initial=s))


@given(st.lists(st.integers()))
def test_seq_concat_pipe(xs: List[int]):
    value = seq.concat(xs)

    assert list(value) == xs


@given(st.lists(st.integers()), st.lists(st.integers()))
def test_seq_concat_pipe2(xs: List[int], ys: List[int]):
    value = seq.concat(xs, ys)

    assert list(value) == xs + ys


@given(st.lists(st.integers()), st.lists(st.integers()), st.lists(st.integers()))
def test_seq_concat_pipe3(xs: List[int], ys: List[int], zs: List[int]):
    value = seq.concat(xs, ys, zs)

    assert list(value) == xs + ys + zs


@given(st.lists(st.integers()))
def test_seq_collect(xs: List[int]):
    ys = pipe(xs, seq.collect(seq.singleton))

    assert list(xs) == list(ys)


@given(st.lists(st.integers()))
def test_seq_pipeline(xs: List[int]):
    ys = seq.of(xs).pipe(
        seq.map(lambda x: x * 10),
        seq.filter(lambda x: x > 100),
        seq.fold(lambda s, x: s + x, 0),
    )
    assert ys == functools.reduce(lambda s, x: s + x, filter(lambda x: x > 100, map(lambda x: x * 10, xs)), 0)


@given(st.lists(st.integers()))
def test_seq_infinite(xs: List[int]):
    ys = pipe(xs, seq.zip(seq.infinite()))

    expected = list(enumerate(xs))
    assert expected == list(ys)


rtn: Callable[[int], Seq[int]] = seq.singleton
empty: Seq[int] = seq.empty


@given(st.integers(), st.integers())
def test_seq_monad_bind(x: int, y: int):
    m = rtn(x)
    f: Callable[[int], Seq[int]] = lambda x: rtn(x + y)

    assert list(m.collect(f)) == list(rtn(x + y))


@given(st.integers())
def test_seq_monad_empty_bind(value: int):
    m: Seq[int] = empty
    f: Callable[[int], Seq[int]] = lambda x: rtn(x + value)

    assert list(m.collect(f)) == list(m)


@given(st.integers())
def test_seq_monad_law_left_identity(value: int):
    """Monad law left identity.

    return x >>= f is the same thing as f x
    """

    f: Callable[[int], Seq[int]] = lambda x: rtn(x + 42)

    assert list(rtn(value).collect(f)) == list(f(value))


@given(st.integers())
def test_seq_monad_law_right_identity(value: int):
    r"""Monad law right identit.

    m >>= return is no different than just m.
    """
    m = rtn(value)

    assert list(m.collect(rtn)) == list(m)


@given(st.integers())
def test_seq_monad_law_associativity(value: int):
    r"""Monad law associativity.

    (m >>= f) >>= g is just like doing m >>= (\x -> f x >>= g)
    """
    f: Callable[[int], Seq[int]] = lambda x: rtn(x + 10)
    g: Callable[[int], Seq[int]] = lambda y: rtn(y * 42)

    m = rtn(value)
    assert list(m.collect(f).collect(g)) == list(m.collect(lambda x: f(x).collect(g)))


@given(st.integers())
def test_seq_monad_law_associativity_empty(value: int):
    # (m >>= f) >>= g is just like doing m >>= (\x -> f x >>= g)
    f: Callable[[int], Seq[int]] = lambda x: rtn(x + 1000)
    g: Callable[[int], Seq[int]] = lambda y: rtn(y * 42)

    # Empty list
    m = empty
    assert list(m.collect(f).collect(g)) == list(m.collect(lambda x: f(x).collect(g)))
