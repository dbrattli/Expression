from hypothesis import given, strategies as st
from fslash.core import pipe, pipe2


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


@given(st.integers(), st.integers())
def test_pipe2_id(x, y):
    value = pipe2((x, y))
    assert value == (x, y)


@given(st.integers(), st.integers())
def test_pipe2_fn(x, y):
    value = pipe2((x, y), lambda x, y: x + y)
    assert value == x + y


@given(st.integers(), st.integers(), st.integers())
def test_pipe2_fn_gn(x, y, z):
    gn = lambda g: g * y
    fn = lambda x, y: x + y
    value = pipe2((x, y), fn, gn)

    assert value == gn(fn(x, y))
