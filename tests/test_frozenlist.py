from builtins import list as pylist
from typing import Any, Callable
from typing import List as PyList

from expression.collections import Cons, FrozenList, Nil, frozenlist
from expression.core import pipe
from hypothesis import given
from hypothesis import strategies as st

Func = Callable[[int], int]


def test_list_nil():
    assert isinstance(Nil, FrozenList)


def test_list_cons():
    xs = Cons(42, Nil)
    assert isinstance(xs, FrozenList)


@given(st.integers(min_value=0, max_value=10000))
def test_list_large_list(x: int):
    xs = frozenlist.of_seq(range(x))
    assert len(xs) == x


def test_list_is_null_after_cons_and_tail_fluent():
    xs: FrozenList[int] = frozenlist.empty.cons(42).tail()
    assert xs.is_empty()


def test_list_not_null_after_cons_fluent():
    xs = frozenlist.empty.cons(42)
    assert not xs.is_empty()


def test_list_head_fluent():
    x = empty.cons(42).head()
    assert x == 42


@given(st.text(), st.text())
def test_list_tail_head_fluent(a: str, b: str):
    xs = frozenlist.empty.cons(b).cons(a)
    assert a == xs.head()


def test_list_tail_tail_null_fluent():
    xs = empty.cons("b").cons("a")
    assert xs.tail().tail().is_empty()


def test_list_list_fluent():
    xs = frozenlist.empty.cons(empty.cons(42))
    assert 42 == xs.head().head()


def test_list_length_empty():
    xs = frozenlist.empty
    assert len(xs) == 0


def test_list_length_non_empty():
    xs = frozenlist.singleton(42)
    assert len(xs) == 1


@given(st.lists(st.integers()))
def test_list_length(xs: PyList[int]):
    ys = frozenlist.of_seq(xs)
    assert len(xs) == len(ys)


@given(st.one_of(st.integers(), st.text()))
def test_list_cons_head(value: Any):
    x = pipe(Cons(value, Nil), frozenlist.head)
    assert x == value


@given(st.lists(st.integers(), min_size=1), st.integers(min_value=0))
def test_list_item(xs: PyList[int], index: int):
    ys = frozenlist.of_seq(xs)
    while index and index >= len(xs):
        index //= 2
    assert xs[index] == ys[index]


@given(st.lists(st.integers()))
def test_list_pipe_map(xs: PyList[int]):
    def mapper(x: int):
        return x + 1

    ys = frozenlist.of_seq(xs)
    zs = ys.pipe(frozenlist.map(mapper))

    assert isinstance(zs, FrozenList)
    assert [y for y in zs] == [mapper(x) for x in xs]


@given(st.lists(st.integers()))
def test_list_len(xs: PyList[int]):
    ys = frozenlist.of_seq(xs)
    assert len(xs) == len(ys)


@given(st.lists(st.integers()), st.integers(min_value=0))
def test_list_take(xs: PyList[int], x: int):
    ys: FrozenList[int]
    try:
        ys = frozenlist.of_seq(xs).take(x)
        assert pylist(ys) == xs[:x]
    except ValueError:
        assert x > len(xs)


@given(st.lists(st.integers()), st.integers(min_value=0))
def test_list_take_last(xs: PyList[int], x: int):
    expected = xs[-x:] if x else []
    ys: FrozenList[int]
    try:
        ys = frozenlist.of_seq(xs).take_last(x)
        assert pylist(ys) == expected
    except ValueError:
        assert x > len(xs)


@given(st.lists(st.integers()), st.integers(min_value=0))
def test_list_skip(xs: PyList[int], x: int):
    ys: FrozenList[int]
    try:
        ys = frozenlist.of_seq(xs).skip(x)
        assert pylist(ys) == xs[x:]
    except ValueError:
        assert x > len(xs)


@given(st.lists(st.integers()), st.integers(min_value=0))
def test_list_skip_last(xs: PyList[int], x: int):
    expected = xs[:-x] if x else xs
    ys: FrozenList[int]
    try:
        ys = frozenlist.of_seq(xs).skip_last(x)
        assert pylist(ys) == expected
    except ValueError:
        assert x > len(xs)


@given(st.lists(st.integers()), st.integers(), st.integers())
def test_list_slice(xs: PyList[int], x: int, y: int):
    expected = xs[x:y]

    ys: FrozenList[int]
    ys = frozenlist.of_seq(xs)[x:y]

    assert pylist(ys) == expected


rtn: Callable[[int], FrozenList[int]] = frozenlist.singleton
empty: FrozenList[Any] = frozenlist.empty


@given(st.integers(), st.integers())
def test_list_monad_bind(x: int, y: int):
    m = rtn(x)
    f: Callable[[int], FrozenList[int]] = lambda x: rtn(x + y)

    assert m.collect(f) == rtn(x + y)


@given(st.integers())
def test_list_monad_empty_bind(value: int):
    m = empty
    f: Callable[[int], FrozenList[int]] = lambda x: rtn(x + value)

    assert m.collect(f) == m


@given(st.integers())
def test_list_monad_law_left_identity(value: int):
    """Monad law left identity.

    return x >>= f is the same thing as f x
    """

    f: Callable[[int], FrozenList[int]] = lambda x: rtn(x + 42)

    assert rtn(value).collect(f) == f(value)


@given(st.integers())
def test_list_monad_law_right_identity(value: int):
    r"""Monad law right identit.

    m >>= return is no different than just m.
    """
    m = rtn(value)

    assert m.collect(rtn) == m


@given(st.integers())
def test_list_monad_law_associativity(value: int):
    r"""Monad law associativity.

    (m >>= f) >>= g is just like doing m >>= (\x -> f x >>= g)
    """
    f: Callable[[int], FrozenList[int]] = lambda x: rtn(x + 10)
    g: Callable[[int], FrozenList[int]] = lambda y: rtn(y * 42)

    m = rtn(value)
    assert m.collect(f).collect(g) == m.collect(lambda x: f(x).collect(g))


@given(st.integers())
def test_list_monad_law_associativity_empty(value: int):
    # (m >>= f) >>= g is just like doing m >>= (\x -> f x >>= g)
    f: Callable[[int], FrozenList[int]] = lambda x: rtn(x + 1000)
    g: Callable[[int], FrozenList[int]] = lambda y: rtn(y * 42)

    # Empty list
    m = empty
    assert m.collect(f).collect(g) == m.collect(lambda x: f(x).collect(g))


@given(st.lists(st.integers()))
def test_list_monad_law_associativity_iterable(xs: PyList[int]):
    # (m >>= f) >>= g is just like doing m >>= (\x -> f x >>= g)
    f: Callable[[int], FrozenList[int]] = lambda x: rtn(x + 10)
    g: Callable[[int], FrozenList[int]] = lambda y: rtn(y * 42)

    m = frozenlist.of_seq(xs)
    assert m.collect(f).collect(g) == m.collect(lambda x: f(x).collect(g))
