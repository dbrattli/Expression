from hypothesis import given, strategies as st
from fslash.core import pipe


@given(st.integers())
def test_pipe_id(x):
    value = pipe(x)
    assert value == x


@given(st.integers())
def test_pipe_fn(x):
    value = pipe(x, lambda x: x + 1)
    assert value == x + 1


@given(st.integers(), st.integers(), st.integers())
def test_pipe_fn_gn(x, y, z):
    gn = lambda g: g * y
    fn = lambda x: x + z
    value = pipe(x, fn, gn)

    assert value == gn(fn(x))
