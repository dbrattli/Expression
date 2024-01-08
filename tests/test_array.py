import functools
from collections.abc import Callable
from typing import Any

import pytest
from hypothesis import given  # type: ignore
from hypothesis import strategies as st

from expression import Nothing, Option, Some, pipe
from expression.collections import TypedArray, array


Func = Callable[[int], int]


@given(st.integers(min_value=0, max_value=10000))  # type: ignore
def test_array_large_list(x: int):
    xs = array.of_seq(range(x))
    assert len(xs) == x


def test_array_empty():
    xs = array.empty()
    assert len(xs) == 0
    assert not xs
    assert pipe(xs, array.is_empty)


def test_array_non_empty():
    xs = array.singleton(42)
    assert len(xs) == 1
    assert xs
    assert not pipe(xs, array.is_empty)


def test_array_create_bytes():
    xs = TypedArray[int](b"test")

    assert xs.typecode == array.TypeCode.Byte
    assert len(xs) == 4


def test_array_map_int_to_str():
    xs = array.of_seq([1, 2, 3])
    assert len(xs) == 3

    ys: TypedArray[str] = pipe(xs, array.map(str))
    assert len(ys) == 3
    assert ys.typecode == array.TypeCode.Any
    assert ys == TypedArray(["1", "2", "3"])


def test_array_map_str_to_uint8():
    xs = array.of_seq(["1", "2", "3"])
    assert len(xs) == 3

    mapper: Callable[[str], array.uint8] = array.uint8  # type: ignore
    ys: TypedArray[array.uint8] = pipe(xs, array.map(mapper))
    assert len(ys) == 3
    assert ys.typecode == array.TypeCode.Uint8
    assert ys == TypedArray([1, 2, 3], typecode=array.TypeCode.Uint8)


def test_array_map_str_to_uint16():
    xs = array.of_seq(["1", "2", "3"])
    assert len(xs) == 3

    mapper: Callable[[str], array.uint16] = array.uint16  # type: ignore
    ys: TypedArray[array.uint16] = pipe(xs, array.map(mapper))
    assert len(ys) == 3
    assert ys.typecode == array.TypeCode.Uint16
    assert ys == TypedArray([1, 2, 3], typecode=array.TypeCode.Uint16)


def test_array_map_str_to_uint32():
    xs = array.of_seq(["1", "2", "3"])
    assert len(xs) == 3

    mapper: Callable[[str], array.uint32] = array.uint32  # type: ignore
    ys: TypedArray[array.uint32] = pipe(xs, array.map(mapper))
    assert len(ys) == 3
    assert ys.typecode == array.TypeCode.Uint32
    assert ys == TypedArray([1, 2, 3], typecode=array.TypeCode.Uint32)


def test_array_map_str_to_float32():
    xs = array.of_seq(["1", "2", "3"])
    assert len(xs) == 3

    mapper: Callable[[str], array.float32] = array.float32  # type: ignore
    ys: TypedArray[array.float32] = pipe(xs, array.map(mapper))
    assert len(ys) == 3
    assert ys.typecode == array.TypeCode.Float
    assert ys == TypedArray([1, 2, 3], typecode=array.TypeCode.Float)


def test_array_filter_preserves_type():
    mapper: Callable[[int], array.int16] = array.int16  # type: ignore
    xs: TypedArray[array.int16] = array.of_seq([1, 2, 3]).pipe(array.map(mapper))
    assert len(xs) == 3

    ys: TypedArray[array.int16] = pipe(xs, array.filter(lambda x: x < 2))
    assert len(ys) == 1
    assert ys.typecode == array.TypeCode.Int16
    assert ys == TypedArray([1], typecode=array.TypeCode.Int16)


@given(st.lists(st.integers()))  # type: ignore
def test_array_length(xs: list[int]):
    ys = array.of_seq(xs)
    assert len(xs) == len(ys)


def test_array_uint8_overflow():
    with pytest.raises(OverflowError):
        TypedArray([256], typecode=array.TypeCode.Uint8)


def test_array_sum_works():
    xs = TypedArray([1.0, 2.0])
    ys = pipe(xs, array.sum)
    assert ys == 3.0


def test_array_sum_by_works():
    xs = TypedArray([1.0, 2.0])
    ys = pipe(xs, array.sum_by(lambda x: x * 2.0))
    assert ys == 6.0


def test_array_head_fluent():
    x = array.singleton(42).head()
    assert x == 42


def test_array_head_match_list():
    xs: TypedArray[int] = array.singleton(42)
    match xs:
        case [head, *_]:
            assert head == 42
        case _:
            assert False


@given(st.lists(st.integers(), min_size=1), st.integers(min_value=0))  # type: ignore
def test_array_item(xs: list[int], index: int):
    ys = array.of_seq(xs)
    while index and index >= len(xs):
        index //= 2
    assert xs[index] == ys[index]


@given(st.lists(st.integers()))  # type: ignore
def test_array_pipe_map(xs: list[int]):
    def mapper(x: int):
        return x + 1

    ys = array.of_seq(xs)
    zs = ys.pipe(array.map(mapper))

    assert isinstance(zs, TypedArray)
    assert [y for y in zs] == [mapper(x) for x in xs]


# @given(st.lists(st.tuples(st.integers(), st.integers())))  # type: ignore
# def test_seq_pipe_starmap(xs: List[Tuple[int, int]]):
#     mapper: Callable[[int, int], int] = lambda x, y: x + y
#     ys = pipe(
#         frozenlist.of_seq(xs),
#         frozenlist.starmap(mapper),
#     )

#     assert isinstance(ys, Block)
#     assert [y for y in ys] == [x + y for (x, y) in xs]


# @given(st.lists(st.tuples(st.integers(), st.integers())))  # type: ignore
# def test_seq_pipe_map2(xs: List[Tuple[int, int]]):
#     mapper: Callable[[int, int], int] = lambda x, y: x + y
#     ys = pipe(
#         frozenlist.of_seq(xs),
#         frozenlist.map2(mapper),
#     )

#     assert isinstance(ys, Block)
#     assert [y for y in ys] == [x + y for (x, y) in xs]


# @given(st.lists(st.tuples(st.integers(), st.integers(), st.integers())))  # type: ignore
# def test_seq_pipe_map3(xs: List[Tuple[int, int, int]]):
#     mapper: Callable[[int, int, int], int] = lambda x, y, z: x + y + z
#     ys = pipe(
#         frozenlist.of_seq(xs),
#         frozenlist.map3(mapper),
#     )

#     assert isinstance(ys, Block)
#     assert [y for y in ys] == [x + y + z for (x, y, z) in xs]


# @given(st.lists(st.integers()))  # type: ignore
# def test_array_pipe_mapi(xs: List[int]):
#     def mapper(i: int, x: int):
#         return x + i

#     ys = array.of_seq(xs)
#     zs = ys.pipe(array.mapi(mapper))

#     assert isinstance(zs, TypedArray)
#     assert [z for z in zs] == [x + i for i, x in enumerate(xs)]


@given(st.lists(st.integers()))  # type: ignore
def test_array_len(xs: list[int]):
    ys = array.of_seq(xs)
    assert len(xs) == len(ys)


# @given(st.lists(st.integers()), st.lists(st.integers()))  # type: ignore
# def test_array_append(xs: List[int], ys: List[int]):
#     expected = xs + ys
#     fx = array.of_seq(xs)
#     fy = array.of_seq(ys)
#     fz = fx.append(fy)
#     fh = fx + fy

#     assert list(fz) == list(fh) == expected


@given(st.lists(st.integers()), st.integers(min_value=0))  # type: ignore
def test_array_take(xs: list[int], x: int):
    ys: TypedArray[int]
    try:
        ys = array.of_seq(xs).take(x)
        assert list(ys) == xs[:x]
    except ValueError:
        assert x > len(xs)


@given(st.lists(st.integers()), st.integers(min_value=0))  # type: ignore
def test_array_take_last(xs: list[int], x: int):
    expected = xs[-x:]
    ys: TypedArray[int]
    ys = array.of_seq(xs).take_last(x)
    assert list(ys) == expected


@given(st.lists(st.integers()), st.integers(min_value=0))  # type: ignore
def test_array_skip(xs: list[int], x: int):
    ys: TypedArray[int]
    try:
        ys = array.of_seq(xs).skip(x)
        assert list(ys) == xs[x:]
    except ValueError:
        assert x > len(xs)


@given(st.lists(st.integers()), st.integers(min_value=0))  # type: ignore
def test_array_skip_last(xs: list[int], x: int):
    expected = xs[:-x]
    ys: TypedArray[int]
    ys = array.of_seq(xs).skip_last(x)
    assert list(ys) == expected


# @given(st.lists(st.integers()), st.integers(), st.integers())  # type: ignore
# def test_array_slice(xs: List[int], x: int, y: int):
#     expected = xs[x:y]

#     ys: Block[int] = frozenlist.of_seq(xs)
#     zs = ys[x:y]

#     assert list(zs) == expected


@given(st.lists(st.integers(), min_size=1), st.integers(min_value=0))  # type: ignore
def test_array_index(xs: list[int], x: int):
    x = x % len(xs) if x > 0 else x
    expected = xs[x]

    ys: TypedArray[int] = array.of_seq(xs)
    y = ys[x]

    item: Callable[[TypedArray[int]], int] = array.item(x)
    h = ys.pipe(item)

    i = ys.item(x)

    assert y == h == i == expected


@given(st.lists(st.integers()))  # type: ignore
def test_array_indexed(xs: list[int]):
    expected = list(enumerate(xs))

    ys: TypedArray[int] = array.of_seq(xs)
    zs = pipe(ys, array.indexed(0))

    assert list(zs) == expected


@given(st.lists(st.integers()))  # type: ignore
def test_array_fold(xs: list[int]):
    def folder(x: int, y: int) -> int:
        return x + y

    expected: int = functools.reduce(folder, xs, 0)

    ys: TypedArray[int] = array.of_seq(xs)
    result = pipe(ys, array.fold(folder, 0))

    assert result == expected


@given(st.integers(max_value=100))  # type: ignore
def test_array_unfold(x: int):
    def unfolder(state: int) -> Option[tuple[int, int]]:
        if state < x:
            return Some((state, state + 1))
        return Nothing

    result = TypedArray.unfold(unfolder, 0)

    assert list(result) == list(range(x))


@given(st.lists(st.integers()), st.integers())  # type: ignore
def test_array_filter(xs: list[int], limit: int):
    expected = filter(lambda x: x < limit, xs)

    ys: TypedArray[int] = array.of_seq(xs)
    predicate: Callable[[int], bool] = lambda x: x < limit
    result = pipe(ys, array.filter(predicate))

    assert list(result) == list(expected)


# @given(st.lists(st.integers()))  # type: ignore
# def test_array_sort(xs: List[int]):
#     expected = sorted(xs)
#     ys: TypedArray[int] = array.of_seq(xs)
#     result = pipe(ys, array.sort())

#     assert list(result) == list(expected)


# @given(st.lists(st.text(min_size=2)))  # type: ignore
# def test_array_sort_with(xs: List[str]):
#     expected = sorted(xs, key=lambda x: x[1])
#     ys: Block[str] = frozenlist.of_seq(xs)
#     func: Callable[[str], str] = lambda x: x[1]
#     result = pipe(ys, frozenlist.sort_with(func))

#     assert list(result) == list(expected)


rtn: Callable[[int], TypedArray[int]] = array.singleton
empty: TypedArray[Any] = array.empty()


@given(st.integers(), st.integers())  # type: ignore
def test_array_monad_bind(x: int, y: int):
    m = rtn(x)
    f: Callable[[int], TypedArray[int]] = lambda x: rtn(x + y)

    assert m.collect(f) == rtn(x + y)


@given(st.integers())  # type: ignore
def test_array_monad_empty_bind(value: int):
    m = empty
    f: Callable[[int], TypedArray[int]] = lambda x: rtn(x + value)

    assert m.collect(f) == m


@given(st.integers())  # type: ignore
def test_array_monad_law_left_identity(value: int):
    """Monad law left identity.

    return x >>= f is the same thing as f x
    """
    f: Callable[[int], TypedArray[int]] = lambda x: rtn(x + 42)

    assert rtn(value).collect(f) == f(value)


@given(st.integers())  # type: ignore
def test_array_monad_law_right_identity(value: int):
    r"""Monad law right identity.

    m >>= return is no different than just m.
    """
    m = rtn(value)

    assert m.collect(rtn) == m


@given(st.integers())  # type: ignore
def test_array_monad_law_associativity(value: int):
    r"""Monad law associativity.

    (m >>= f) >>= g is just like doing m >>= (\x -> f x >>= g)
    """
    f: Callable[[int], TypedArray[int]] = lambda x: rtn(x + 10)
    g: Callable[[int], TypedArray[int]] = lambda y: rtn(y * 42)

    m = rtn(value)
    assert m.collect(f).collect(g) == m.collect(lambda x: f(x).collect(g))


@given(st.integers())  # type: ignore
def test_array_monad_law_associativity_empty(value: int):
    # (m >>= f) >>= g is just like doing m >>= (\x -> f x >>= g)
    f: Callable[[int], TypedArray[int]] = lambda x: rtn(x + 1000)
    g: Callable[[int], TypedArray[int]] = lambda y: rtn(y * 42)

    # Empty list
    m = empty
    assert m.collect(f).collect(g) == m.collect(lambda x: f(x).collect(g))


@given(st.lists(st.integers()))  # type: ignore
def test_array_monad_law_associativity_iterable(xs: list[int]):
    # (m >>= f) >>= g is just like doing m >>= (\x -> f x >>= g)
    f: Callable[[int], TypedArray[int]] = lambda x: rtn(x + 10)
    g: Callable[[int], TypedArray[int]] = lambda y: rtn(y * 42)

    m = array.of_seq(xs)
    assert m.collect(f).collect(g) == m.collect(lambda x: f(x).collect(g))
