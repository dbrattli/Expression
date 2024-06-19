import functools
from builtins import list as list
from collections.abc import Callable
from typing import Any, List, Annotated

from hypothesis import given  # type: ignore
from hypothesis import strategies as st
from pydantic import BaseModel, Field, GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema

from expression import Nothing, Option, Some, pipe
from expression.collections import Block, block

Func = Callable[[int], int]


@given(st.integers(min_value=0, max_value=10000))  # type: ignore
def test_block_large_list(x: int):
    xs = block.of_seq(range(x))
    assert len(xs) == x


def test_block_is_null_after_cons_and_tail_fluent():
    xs: Block[int] = block.empty.cons(42).tail()
    assert xs.is_empty()


def test_block_not_null_after_cons_fluent():
    xs = block.empty.cons(42)
    assert not xs.is_empty()


def test_block_head_fluent():
    x = empty.cons(42).head()
    assert x == 42


def test_block_head_match() -> None:
    xs: Block[int] = empty.cons(42)
    match xs:
        case Block([head, *_]):
            assert head == 42
            return
        case _:
            assert False


def test_block_head_match_iterable() -> None:
    xs: Block[int] = empty.cons(42)

    match list(xs):
        case (head, *_):
            assert head == 42
            return
        case _:
            assert False


def test_block_head_match_list() -> None:
    xs: Block[int] = empty.cons(42)

    match list(xs):
        case (head, *_):
            assert head == 42
            return
        case _:
            assert False


@given(st.text(), st.text())  # type: ignore
def test_block_tail_head_fluent(a: str, b: str):
    xs = block.empty.cons(b).cons(a)
    assert a == xs.head()


def test_block_tail_tail_null_fluent():
    xs = empty.cons("b").cons("a")
    assert xs.tail().tail().is_empty()


def test_block_list_fluent():
    xs = block.empty.cons(empty.cons(42))
    assert 42 == xs.head().head()


def test_block_empty():
    xs = block.empty
    assert len(xs) == 0
    assert not xs
    assert pipe(xs, block.is_empty)


def test_block_non_empty():
    xs = block.singleton(42)
    assert len(xs) == 1
    assert xs
    assert not pipe(xs, block.is_empty)


@given(st.lists(st.integers()))  # type: ignore
def test_block_length(xs: List[int]):
    ys = block.of_seq(xs)
    assert len(xs) == len(ys)


@given(st.one_of(st.integers(), st.text()))  # type: ignore
def test_block_cons_head(value: Any):
    x = pipe(block.empty.cons(value), block.head)
    assert x == value


@given(st.lists(st.integers(), min_size=1), st.integers(min_value=0))  # type: ignore
def test_block_item(xs: List[int], index: int):
    ys = block.of_seq(xs)
    while index and index >= len(xs):
        index //= 2
    assert xs[index] == ys[index]


@given(st.lists(st.integers()))  # type: ignore
def test_block_pipe_map(xs: List[int]):
    def mapper(x: int):
        return x + 1

    ys = block.of_seq(xs)
    zs = ys.pipe(block.map(mapper))

    assert isinstance(zs, Block)
    assert [y for y in zs] == [mapper(x) for x in xs]


@given(st.lists(st.tuples(st.integers(), st.integers())))  # type: ignore
def test_seq_pipe_starmap(xs: List[tuple[int, int]]):
    mapper: Callable[[int, int], int] = lambda x, y: x + y
    ys = pipe(
        block.of_seq(xs),
        block.starmap(mapper),
    )

    assert isinstance(ys, Block)
    assert [y for y in ys] == [x + y for (x, y) in xs]


@given(st.lists(st.tuples(st.integers(), st.integers())))  # type: ignore
def test_seq_pipe_map2(xs: List[tuple[int, int]]):
    mapper: Callable[[int, int], int] = lambda x, y: x + y
    ys = pipe(
        block.of_seq(xs),
        block.map2(mapper),
    )

    assert isinstance(ys, Block)
    assert [y for y in ys] == [x + y for (x, y) in xs]


@given(st.lists(st.tuples(st.integers(), st.integers(), st.integers())))  # type: ignore
def test_seq_pipe_map3(xs: List[tuple[int, int, int]]):
    mapper: Callable[[int, int, int], int] = lambda x, y, z: x + y + z
    ys = pipe(
        block.of_seq(xs),
        block.map3(mapper),
    )

    assert isinstance(ys, Block)
    assert [y for y in ys] == [x + y + z for (x, y, z) in xs]


@given(st.lists(st.integers()))  # type: ignore
def test_block_pipe_mapi(xs: List[int]):
    def mapper(i: int, x: int):
        return x + i

    ys = block.of_seq(xs)
    zs = ys.pipe(block.mapi(mapper))

    assert isinstance(zs, Block)
    assert [z for z in zs] == [x + i for i, x in enumerate(xs)]


@given(st.lists(st.integers()))  # type: ignore
def test_block_len(xs: List[int]):
    ys = block.of_seq(xs)
    assert len(xs) == len(ys)


@given(st.lists(st.integers()), st.lists(st.integers()))  # type: ignore
def test_block_append(xs: List[int], ys: List[int]):
    expected = xs + ys
    fx = block.of_seq(xs)
    fy = block.of_seq(ys)
    fz = fx.append(fy)
    fh = fx + fy

    assert list(fz) == list(fh) == expected


@given(st.lists(st.integers()), st.integers(min_value=0))  # type: ignore
def test_block_take(xs: List[int], x: int):
    ys: Block[int]
    try:
        ys = block.of_seq(xs).take(x)
        assert list(ys) == xs[:x]
    except ValueError:
        assert x > len(xs)


@given(st.lists(st.integers()), st.integers(min_value=0))  # type: ignore
def test_block_take_last(xs: List[int], x: int):
    expected = xs[-x:]
    ys: Block[int]
    ys = block.of_seq(xs).take_last(x)
    assert list(ys) == expected


@given(st.lists(st.integers()), st.integers(min_value=0))  # type: ignore
def test_block_skip(xs: List[int], x: int):
    ys: Block[int]
    try:
        ys = block.of_seq(xs).skip(x)
        assert list(ys) == xs[x:]
    except ValueError:
        assert x > len(xs)


@given(st.lists(st.integers()), st.integers(min_value=0))  # type: ignore
def test_block_skip_last(xs: List[int], x: int):
    expected = xs[:-x]
    ys: Block[int]
    ys = block.of_seq(xs).skip_last(x)
    assert list(ys) == expected


@given(st.lists(st.integers()), st.integers(), st.integers())  # type: ignore
def test_block_slice(xs: List[int], x: int, y: int):
    expected = xs[x:y]

    ys: Block[int] = block.of_seq(xs)
    zs = ys[x:y]

    assert list(zs) == expected


@given(st.lists(st.integers(), min_size=1), st.integers(min_value=0))  # type: ignore
def test_block_index(xs: List[int], x: int):
    x = x % len(xs) if x > 0 else x
    expected = xs[x]

    ys: Block[int] = block.of_seq(xs)
    y = ys[x]

    item: Callable[[Block[int]], int] = block.item(x)
    h = ys.pipe(item)

    i = ys.item(x)

    assert y == h == i == expected


@given(st.lists(st.integers()))  # type: ignore
def test_block_indexed(xs: List[int]):
    expected = list(enumerate(xs))

    ys: Block[int] = block.of_seq(xs)
    zs = block.indexed(ys)

    assert list(zs) == expected


@given(st.lists(st.integers()))  # type: ignore
def test_block_fold(xs: List[int]):
    def folder(x: int, y: int) -> int:
        return x + y

    expected: int = functools.reduce(folder, xs, 0)

    ys: Block[int] = block.of_seq(xs)
    result = pipe(ys, block.fold(folder, 0))

    assert result == expected


@given(st.integers(max_value=100))  # type: ignore
def test_block_unfold(x: int):
    def unfolder(state: int) -> Option[tuple[int, int]]:
        if state < x:
            return Some((state, state + 1))
        return Nothing

    result: Block[int] = Block.unfold(unfolder, 0)

    assert list(result) == list(range(x))


@given(st.lists(st.integers()), st.integers())  # type: ignore
def test_block_filter(xs: List[int], limit: int):
    expected = filter(lambda x: x < limit, xs)

    ys: Block[int] = block.of_seq(xs)
    predicate: Callable[[int], bool] = lambda x: x < limit
    result = pipe(ys, block.filter(predicate))

    assert list(result) == list(expected)


@given(st.lists(st.integers()))  # type: ignore
def test_block_sort(xs: List[int]):
    expected = sorted(xs)
    ys: Block[int] = block.of_seq(xs)
    result = pipe(ys, block.sort())

    assert list(result) == list(expected)


@given(st.lists(st.text(min_size=2)))  # type: ignore
def test_block_sort_with(xs: List[str]):
    expected = sorted(xs, key=lambda x: x[1])
    ys: Block[str] = block.of_seq(xs)
    func: Callable[[str], str] = lambda x: x[1]
    result = pipe(
        ys,
        block.sort_with(func),
    )

    assert list(result) == list(expected)


def test_block_partition_works():
    xs = Block.range(10)
    ys, zs = xs.partition(lambda x: x > 5)

    assert ys == Block.range(6, 10)
    assert zs == Block.range(6)


rtn: Callable[[int], Block[int]] = block.singleton
empty: Block[Any] = block.empty


@given(st.integers(), st.integers())  # type: ignore
def test_block_monad_bind(x: int, y: int):
    m = rtn(x)
    f: Callable[[int], Block[int]] = lambda x: rtn(x + y)

    assert m.collect(f) == rtn(x + y)


@given(st.integers())  # type: ignore
def test_block_monad_empty_bind(value: int):
    m = empty
    f: Callable[[int], Block[int]] = lambda x: rtn(x + value)

    assert m.collect(f) == m


@given(st.integers())  # type: ignore
def test_block_monad_law_left_identity(value: int):
    """Monad law left identity.

    return x >>= f is the same thing as f x
    """
    f: Callable[[int], Block[int]] = lambda x: rtn(x + 42)

    assert rtn(value).collect(f) == f(value)


@given(st.integers())  # type: ignore
def test_block_monad_law_right_identity(value: int):
    r"""Monad law right identity.

    m >>= return is no different than just m.
    """
    m = rtn(value)

    assert m.collect(rtn) == m


@given(st.integers())  # type: ignore
def test_block_monad_law_associativity(value: int):
    r"""Monad law associativity.

    (m >>= f) >>= g is just like doing m >>= (\x -> f x >>= g)
    """
    f: Callable[[int], Block[int]] = lambda x: rtn(x + 10)
    g: Callable[[int], Block[int]] = lambda y: rtn(y * 42)

    m = rtn(value)
    assert m.collect(f).collect(g) == m.collect(lambda x: f(x).collect(g))


@given(st.integers())  # type: ignore
def test_block_monad_law_associativity_empty(value: int):
    # (m >>= f) >>= g is just like doing m >>= (\x -> f x >>= g)
    f: Callable[[int], Block[int]] = lambda x: rtn(x + 1000)
    g: Callable[[int], Block[int]] = lambda y: rtn(y * 42)

    # Empty list
    m = empty
    assert m.collect(f).collect(g) == m.collect(lambda x: f(x).collect(g))


@given(st.lists(st.integers()))  # type: ignore
def test_block_monad_law_associativity_iterable(xs: List[int]):
    # (m >>= f) >>= g is just like doing m >>= (\x -> f x >>= g)
    f: Callable[[int], Block[int]] = lambda x: rtn(x + 10)
    g: Callable[[int], Block[int]] = lambda y: rtn(y * 42)

    m = block.of_seq(xs)
    assert m.collect(f).collect(g) == m.collect(lambda x: f(x).collect(g))


PositiveInt = Annotated[int, Field(gt=0)]


class Username(str):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: GetCoreSchemaHandler) -> CoreSchema:
        return core_schema.no_info_after_validator_function(cls, handler(str))


class Model(BaseModel):
    one: Block[int]
    two: Block[str] = block.empty
    three: Block[float] = block.empty
    annotated_type: Block[PositiveInt] = block.empty
    annotated_type_empty: Block[PositiveInt] = block.empty

    custom_type: Block[Username] = block.empty
    custom_type_empty: Block[Username] = block.empty


def test_parse_block_works():
    obj = dict(one=[1, 2, 3], two=[], annotated_type=[1, 2, 3], custom_type=["a", "b", "c"])
    model = Model.model_validate(obj)
    assert isinstance(model.one, Block)
    assert model.one == Block([1, 2, 3])
    assert model.two == Block.empty()
    assert model.three == block.empty
    assert model.annotated_type == Block([1, 2, 3])
    assert model.annotated_type_empty == block.empty
    assert model.custom_type == Block(["a", "b", "c"])
    assert model.custom_type_empty == block.empty


def test_serialize_block_works():
    # arrange
    model = Model(one=Block([1, 2, 3]), two=Block.empty())

    # act
    json = model.model_dump_json()

    # assert
    model_ = Model.model_validate_json(json)
    assert model_.one == Block([1, 2, 3])
    assert model_.two == Block.empty()
    assert model_.three == block.empty
