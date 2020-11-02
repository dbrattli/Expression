from typing import Callable

from expression.core import compose, identity
from hypothesis import given
from hypothesis import strategies as st

Func = Callable[[int], int]


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
def test_compose_2(x: int):
    fn: Func = lambda x: x + 42
    gn: Func = lambda x: x - 3
    hn = compose(fn, gn)

    assert hn(x) == gn(fn(x))


@given(st.integers())
def test_compose_3(x: int):
    fn: Func = lambda x: x + 42
    gn: Func = lambda x: x - 3
    hn: Func = lambda x: x * 2

    cn = compose(fn, gn, hn)

    assert cn(x) == hn(gn(fn(x)))


@given(st.integers())
def test_compose_many(x: int):
    fn: Func = lambda x: x + 42
    gn: Func = lambda x: x - 3
    hn: Func = lambda x: x * 2

    cn = compose(fn, gn, hn, fn, hn, gn, fn)

    assert cn(x) == fn(gn(hn(fn(hn(gn(fn(x)))))))


@given(st.integers())
def test_compose_rigth_identity(x: int):
    fn: Func = lambda x: x + 42

    cn = compose(fn, identity)

    assert cn(x) == fn(x)


@given(st.integers())
def test_compose_left_identity(x: int):
    fn: Func = lambda x: x + 42

    cn = compose(identity, fn)

    assert cn(x) == fn(x)


@given(st.integers(), st.integers(), st.integers())
def test_compose_associative(x: int, y: int, z: int):
    """Rearranging the parentheses in an expression will not change the result."""
    fn: Func = lambda a: a + x
    gn: Func = lambda b: b - y
    hn: Func = lambda c: c * z

    cn = compose(fn, gn, hn)
    cn_: Func = lambda x: hn(gn(fn(x)))

    rn = compose(fn, compose(gn, hn))
    rn_: Func = lambda x: (lambda b: hn(gn(b)))(fn(x))  # right associative
    ln = compose(compose(fn, gn), hn)
    ln_: Func = lambda x: hn((lambda b: gn(fn(b)))(x))  # left associative

    assert cn(x) == cn_(x) == rn(x) == rn_(x) == ln(x) == ln_(x)
