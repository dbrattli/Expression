from collections.abc import Callable
from typing import TypeVar

from hypothesis import given  # type: ignore
from hypothesis import strategies as st

from expression import pipe, pipe2
from expression.core.pipe import starpipe, starid

_A = TypeVar("_A")
_B = TypeVar("_B")
_C = TypeVar("_C")


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
    value = pipe2((x, y), lambda x: lambda y: x + y)
    assert value == x + y


@given(st.integers(), st.integers())
def test_pipe2_fn_gn(x: int, y: int):
    gn: Callable[[int], int] = lambda g: g * y
    fn: Callable[[int], Callable[[int], int]] = lambda x: lambda y: x + y
    value = pipe2((x, y), fn, gn)

    assert value == gn(fn(x)(y))


def test_starid_simple():
    assert starid(1) == (1,)
    assert starid(1, 2) == (1, 2)
    assert starid(1, 2, 3) == (1, 2, 3)
    assert starid(1, 2, 3, 4) == (1, 2, 3, 4)


def fn(a: _A, b: _B) -> tuple[_A, _B]:
    return a, b


def gn(a: _A, b: _B) -> tuple[_B, _A]:
    return b, a


def yn(a: _A, b: _B) -> tuple[_A, _B, int]:
    return a, b, 3


def test_starpipe_simple():
    assert starpipe((1, 2), fn) == fn(1, 2)


def test_starpipe_id():
    assert starpipe((1, 2), starid) == (1, 2)


def test_starpipe_fn_gn():
    assert starpipe((1, 2), fn, gn) == gn(*fn(1, 2))


def test_starpipe_fn_gn_yn():
    assert starpipe((1, 2), fn, gn, yn) == yn(*gn(*fn(1, 2)))
