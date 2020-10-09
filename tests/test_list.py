from hypothesis import given, strategies as st

from fslash.core import pipe
from fslash.collections import List_, list as List, Nil, Cons


def test_list_nil():
    assert isinstance(Nil, List_)


def test_list_cons():
    xs = Cons(42, Nil)
    assert isinstance(xs, List_)


@given(st.one_of(st.integers(), st.text()))
def test_list_cons_head(value):
    x = pipe(
        Cons(value, Nil),
        List.head
    )
    assert x == value


@given(st.lists(st.integers()))
def test_list_pipe_map(xs):
    def mapper(x):
        return x + 1

    ys = List.of_seq(xs)
    zs = pipe(ys, List.map(mapper))

    assert isinstance(zs, List_)
    assert [y for y in zs] == [mapper(x) for x in xs]


@given(st.lists(st.integers()))
def test_list_len(xs):
    ys = List.of_seq(xs)
    assert len(xs) == len(ys)


rtn = List.singleton
empty = List.empty


@given(st.integers(), st.integers())
def test_list_monad_bind(x, y):
    m = rtn(x)
    f = lambda x: rtn(x + y)

    assert m.collect(f) == rtn(x + y)


@given(st.integers())
def test_list_monad_empty_bind(value):
    m = empty
    f = lambda x: rtn(x + value)

    assert m.collect(f) == m


@given(st.integers())
def test_list_monad_law_left_identity(value):
    # return x >>= f is the same thing as f x

    f = lambda x: rtn(x + 42)

    assert rtn(value).collect(f) == f(value)


@given(st.integers())
def test_list_monad_law_right_identity(value):
    # m >>= return is no different than just m.

    m = rtn(value)

    assert m.collect(rtn) == m


@given(st.integers())
def test_list_monad_law_associativity(value):
    # (m >>= f) >>= g is just like doing m >>= (\x -> f x >>= g)
    f = lambda x: rtn(x + 10)
    g = lambda y: rtn(y * 42)

    m = rtn(value)
    assert m.collect(f).collect(g) == m.collect(lambda x: f(x).collect(g))


@given(st.integers())
def test_list_monad_law_associativity_empty(value):
    # (m >>= f) >>= g is just like doing m >>= (\x -> f x >>= g)
    f = lambda x: rtn(x + 1000)
    g = lambda y: rtn(y * 42)

    # Empty list
    m = empty
    assert m.collect(f).collect(g) == m.collect(lambda x: f(x).collect(g))


@given(st.lists(st.integers()))
def test_list_monad_law_associativity_iterable(xs):
    # (m >>= f) >>= g is just like doing m >>= (\x -> f x >>= g)
    f = lambda x: rtn(x + 10)
    g = lambda y: rtn(y * 42)

    m = List.of_seq(xs)
    assert m.collect(f).collect(g) == m.collect(lambda x: f(x).collect(g))
