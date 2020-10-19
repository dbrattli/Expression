from typing import Callable
from hypothesis import given, strategies as st
from fslash.core import compose, identity


@given(st.integers())
def test_compose_identity_implicit(x: int):
    fn = compose()

    assert fn(x) == x


@given(st.integers())
def test_compose_identity(x: int):
    fn = compose(identity)

    assert fn(x) == x


@given(st.integers())
def test_compose_1(x: int):
    fn: Callable[[int], int] = lambda x: x + 42
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
def test_compose_many(x):
    fn = lambda x: x + 42
    gn = lambda x: x - 3
    hn = lambda x: x * 2

    cn = compose(fn, gn, hn, fn, hn, gn, fn)

    assert cn(x) == fn(gn(hn(fn(hn(gn(fn(x)))))))


@given(st.integers())
def test_compose_rigth_identity(x):
    fn = lambda x: x + 42

    cn = compose(fn, identity)

    assert cn(x) == fn(x)


@given(st.integers())
def test_compose_left_identity(x):
    fn = lambda x: x + 42

    cn = compose(identity, fn)

    assert cn(x) == fn(x)


@given(st.integers(), st.integers(), st.integers())
def test_compose_associative(x, y, z):
    """Rearranging the parentheses in an expression will not change the result."""
    fn = lambda a: a + x
    gn = lambda b: b - y
    hn = lambda c: c * z

    cn = compose(fn, gn, hn)
    cn_ = lambda x: hn(gn(fn(x)))

    rn = compose(fn, compose(gn, hn))
    rn_ = lambda x: (lambda b: hn(gn(b)))(fn(x))  # right associative
    ln = compose(compose(fn, gn), hn)
    ln_ = lambda x: hn((lambda b: gn(fn(b)))(x))  # left associative

    assert cn(x) == cn_(x) == rn(x) == rn_(x) == ln(x) == ln_(x)
