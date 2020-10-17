from hypothesis import given, strategies as st
from fslash.core import compose, identity


@given(st.integers())
def test_compose_identity_implicit(x):
    fn = compose()

    assert fn(x) == x


@given(st.integers())
def test_compose_identity(x):
    fn = compose(identity)

    assert fn(x) == x


@given(st.integers())
def test_compose_1(x):
    fn = lambda x: x + 42
    gn = compose(fn)

    assert gn(x) == fn(x) == x + 42


@given(st.integers())
def test_compose_2(x):
    fn = lambda x: x + 42
    gn = lambda x: x - 3
    hn = compose(fn, gn)

    assert hn(x) == gn(fn(x))


@given(st.integers())
def test_compose_3(x):
    fn = lambda x: x + 42
    gn = lambda x: x - 3
    hn = lambda x: x * 2

    cn = compose(fn, gn, hn)

    assert cn(x) == hn(gn(fn(x)))


@given(st.integers())
def test_compose_associative(x):
    """Rearranging the parentheses in an expression will not change the result."""

    fn = lambda x: x + 42
    gn = lambda x: x - 3
    hn = lambda x: x * 2

    an = compose(fn, compose(gn, hn))
    bn = compose(compose(fn, gn), hn)

    assert an(x) == bn(x)


@given(st.integers())
def test_compose_many(x):
    fn = lambda x: x + 42
    gn = lambda x: x - 3
    hn = lambda x: x * 2

    cn = compose(fn, gn, hn, fn, hn, gn, fn)

    assert cn(x) == fn(gn(hn(fn(hn(gn(fn(x)))))))
