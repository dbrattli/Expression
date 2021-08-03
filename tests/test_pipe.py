from typing import Callable

from hypothesis import given
from hypothesis import strategies as st

from expression import pipe, pipe2


@given(st.integers())
def test_pipe_id(x: int):
    value = pipe(x)
    assert value == x


@given(st.integers())
def test_pipe_fn(x: int):
    value = pipe(x, lambda x: x + 1)
    assert value == x + 1


@given(st.integers(), st.integers(), st.integers())
def test_pipe_fn_gn(x: int, y: int, z: int):
    gn: Callable[[int], int] = lambda g: g * y
    fn: Callable[[int], int] = lambda x: x + z
    value = pipe(x, fn, gn)

    assert value == gn(fn(x))


@given(st.integers(), st.integers())
def test_pipe2_id(x: int, y: int):
    value = pipe2((x, y))
    assert value == (x, y)


@given(st.integers(), st.integers())
def test_pipe2_fn(x: int, y: int):
    value = pipe2((x, y), lambda x, y: x + y)
    assert value == x + y


@given(st.integers(), st.integers())
def test_pipe2_fn_gn(x: int, y: int):
    gn: Callable[[int], int] = lambda g: g * y
    fn: Callable[[int, int], int] = lambda x, y: x + y
    value = pipe2((x, y), fn, gn)

    assert value == gn(fn(x, y))
