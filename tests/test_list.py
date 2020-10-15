from hypothesis import given, strategies as st

from fslash.core import pipe
from fslash.collections import List_, list as List, Nil, Cons


def test_list_nil():
    assert isinstance(Nil, List_)


def test_list_cons():
    xs = Cons(42, Nil)
    assert isinstance(xs, List_)


@given(st.integers(min_value=0, max_value=10000))
def test_list_large_list(x):
    xs = List.of_seq(range(x))
    assert len(xs) == x


def test_list_is_null_after_cons_and_tail_fluent():
    xs = List.empty.cons(42).tail()
    assert xs.is_empty()


def test_list_not_null_after_cons_fluent():
    xs = List.empty.cons(42)
    assert not xs.is_empty()


def test_list_head_fluent():
    x = empty.cons(42).head()
    assert x == 42


@given(st.text(), st.text())
def test_list_tail_head_fluent(a, b):
    xs = List.empty.cons(b).cons(a)
    assert a == xs.head()


def test_list_tail_tail_null_fluent():
    xs = empty.cons("b").cons("a")
    assert xs.tail().tail().is_empty()


def test_list_list_fluent():
    xs = List.empty.cons(empty.cons(42))
    assert 42 == xs.head().head()


def test_list_length_empty():
    xs = List.empty
    assert len(xs) == 0


def test_list_length_non_empty():
    xs = List.singleton(42)
    assert len(xs) == 1


@given(st.lists(st.integers()))
def test_list_length(xs):
    ys = List.of_seq(xs)
    assert len(xs) == len(ys)


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
    zs = ys.pipe(List.map(mapper))

    assert isinstance(zs, List_)
    assert [y for y in zs] == [mapper(x) for x in xs]


@given(st.lists(st.integers()))
def test_list_len(xs):
    ys = List.of_seq(xs)
    assert len(xs) == len(ys)


@given(st.lists(st.integers()), st.integers(min_value=0))
def test_list_take(xs, x):
    ys: List_
    try:
        ys = List.of_seq(xs).take(x)
        assert list(ys) == xs[:x]

    except ValueError:
        assert x > len(xs)


@given(st.lists(st.integers()), st.integers(min_value=0))
def test_list_take_last(xs, x):
    expected = xs[-x:] if x else []
    ys: List_
    try:
        ys = List.of_seq(xs).take_last(x)
        assert list(ys) == expected
    except ValueError:
        assert x > len(xs)


@given(st.lists(st.integers()), st.integers(min_value=0))
def test_list_skip(xs, x):
    ys: List_
    try:
        ys = List.of_seq(xs).skip(x)
        assert list(ys) == xs[x:]

    except ValueError:
        assert x > len(xs)


@given(st.lists(st.integers()), st.integers(min_value=0))
def test_list_skip_last(xs, x):
    expected = xs[:-x] if x else xs
    ys: List_
    try:
        ys = List.of_seq(xs).skip_last(x)
        assert list(ys) == expected

    except ValueError:
        assert x > len(xs)


@given(st.lists(st.integers()), st.integers(), st.integers())
def test_list_slice(xs, x, y):
    expected = xs[x:y]

    ys: List_
    ys = List.of_seq(xs)[x:y]

    assert list(ys) == expected


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
    """Monad law left identity.

    return x >>= f is the same thing as f x
    """

    f = lambda x: rtn(x + 42)

    assert rtn(value).collect(f) == f(value)


@given(st.integers())
def test_list_monad_law_right_identity(value):
    r"""Monad law right identit.

    m >>= return is no different than just m.
    """
    m = rtn(value)

    assert m.collect(rtn) == m


@given(st.integers())
def test_list_monad_law_associativity(value):
    r"""Monad law associativity.

    (m >>= f) >>= g is just like doing m >>= (\x -> f x >>= g)
    """
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
