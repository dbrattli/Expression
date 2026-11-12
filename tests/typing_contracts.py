"""Consumer contracts checked by Pyright alongside the runtime tests."""

from __future__ import annotations

from collections.abc import Generator, Iterable
from dataclasses import field
from typing import Generic, Literal, TypeAlias, TypeVar, assert_never, assert_type, cast, final

from expression import (
    NOTHING,
    Error,
    Nothing,
    Ok,
    Option,
    Result,
    Some,
    TaggedUnion,
    case,
    effect,
    option,
    result,
    tag,
)
from expression.collections import Block, Map, Seq, TypedArray


def collection_factory_contract() -> None:
    assert_type(Block.of("a", "b"), Block[str])
    assert_type(Block.singleton(42), Block[int])
    assert_type(Block.of_option(Some(42)), Block[int])
    assert_type(TypedArray.of(1, 2), TypedArray[int])
    assert_type(TypedArray.of_seq([1, 2]), TypedArray[int])
    pairs: list[tuple[str, int]] = [("a", 1)]
    assert_type(Map.create(pairs), Map[str, int])
    entries: Block[tuple[str, int]] = Block.of(("a", 1))
    assert_type(Map.of_block(entries), Map[str, int])
    assert_type(Seq.delay(lambda: [1, 2]), Iterable[int])
    assert_type(Seq.of_iterable([1, 2]), Seq[int])

    def generate(state: int) -> Option[tuple[str, int]]:
        return Some((str(state), state + 1)) if state < 3 else NOTHING

    assert_type(Block.unfold(generate, 0), Block[str])
    assert_type(TypedArray.unfold(generate, 0), TypedArray[str])
    assert_type(Seq.unfold(generate, 0), Iterable[str])


def option_contract(value: Option[int]) -> None:
    assert_type(Some(42), Some[int])
    assert_type(Nothing(), Nothing)
    assert_type(NOTHING, Nothing)
    nothing_ = Nothing()
    assert_type(nothing_, Nothing)
    assert_type(value.map(str), Option[str])
    assert_type(Nothing().or_else(Some(42)), Some[int])
    assert_type(value.pipe(option.map(str)), Option[str])
    items: list[int] = value.to_list()
    assert_type(items, list[int])
    if option.is_some(value):
        assert_type(value.some, int)
    match value:
        case Some(payload):
            assert_type(payload, int)
        case Nothing():
            pass
        case _:
            assert_never(value)


def modern_generic_option_contract[T](value: T) -> Option[T]:
    present = Some(value)
    widened: Option[object] = present
    assert_type(widened, Some[T])
    assert_type(present.map(lambda item: (item,)), Some[tuple[T]])

    def wrap(item: T) -> tuple[T]:
        return (item,)

    assert_type(present.pipe(option.map(wrap)), Option[tuple[T]])
    return present


def result_contract(value: Result[int, str]) -> None:
    assert_type(Ok(42), Ok[int])
    assert_type(Error("failure"), Error[str])
    assert_type(value.map(str), Result[str, str])
    assert_type(value.map_error(len), Result[int, int])
    assert_type(value.bind(lambda number: Error(number + 1)), Error[int] | Error[str])
    assert_type(value.pipe(result.map(str)), Result[str, str])
    if result.is_ok(value):
        assert_type(value.ok, int)
    match value:
        case Ok(payload):
            assert_type(payload, int)
        case Error(error):
            assert_type(error, str)
        case _:
            assert_never(value)


_T = TypeVar("_T", covariant=True)


@final
@case
class Circle:
    radius: float
    tag: Literal["circle"] = tag()


@final
@case
class Rectangle:
    width: float
    height: float
    label: str = field(default="", kw_only=True)
    tag: Literal["rectangle"] = tag()


Shape: TypeAlias = TaggedUnion[Circle | Rectangle]


@final
@case
class Just(Generic[_T]):
    value: _T
    tag: Literal["just"] = tag()


@final
@case
class Missing:
    tag: Literal["missing"] = tag()


Maybe: TypeAlias = TaggedUnion[Just[_T] | Missing]


@final
@case(kw_only=True)
class Request:
    path: str
    retries: int = 3
    tag: Literal["request"] = tag()


def custom_case_construction() -> None:
    assert_type(Circle(2.0), Circle)
    assert_type(Rectangle(2.0, 3.0, label="box"), Rectangle)
    assert_type(Just(42), Just[int])
    assert_type(Just[int](42), Just[int])
    assert_type(Missing(), Missing)
    assert_type(Request(path="/items"), Request)


def custom_case_match(value: Shape) -> float:
    match value:
        case Circle(radius):
            assert_type(radius, float)
            return radius
        case Rectangle(width, height):
            assert_type(width, float)
            assert_type(height, float)
            return width * height
        case _:
            assert_never(value)


def custom_generic_match(value: Maybe[int]) -> int:
    match value:
        case Just(payload):
            assert_type(payload, int)
            return payload
        case Missing():
            return 0
        case _:
            assert_never(value)


def custom_tag_narrowing(value: Maybe[int]) -> int:
    if value.tag == "just":
        assert_type(value, Just[int])
        return value.value
    assert_type(value, Missing)
    return 0


@final
@case
class Branch:
    children: tuple[Tree, ...]
    tag: Literal["branch"] = tag()


@final
@case
class Leaf:
    value: int
    tag: Literal["leaf"] = tag()


Tree: TypeAlias = TaggedUnion[Branch | Leaf]


def custom_recursive_match(value: Tree) -> int:
    match value:
        case Branch(children):
            assert_type(children, tuple[Tree, ...])
            return sum(custom_recursive_match(child) for child in children)
        case Leaf(payload):
            assert_type(payload, int)
            return payload
        case _:
            assert_never(value)


@effect.option[int]()
def optional_computation(value: Option[int]) -> Generator[int, int, int]:
    # Pyright #11881: unions of iterable classes lose the return type.
    number = cast(int, (yield from value))
    direct = yield from Some(1)
    assert_type(direct, int)
    return number + direct


@effect.result[int, str]()
def result_computation(value: Result[int, str]) -> Generator[int, int, int]:
    number = cast(int, (yield from value))
    direct = yield from Ok(1)
    assert_type(direct, int)
    return number + direct


def computation_contracts() -> None:
    assert_type(optional_computation(Some(1)), Option[int])
    assert_type(result_computation(Ok(1)), Result[int, str])


async def await_contracts(option_value: Option[int], result_value: Result[int, str]) -> None:
    assert_type(await option_value, int)
    assert_type(await result_value, int)


def collection_sum_and_index_contract() -> None:
    from collections.abc import MutableSequence

    from expression.collections import array, block, seq

    def length(value: str) -> int:
        return len(value)

    def as_float(value: int) -> float:
        return float(value)

    words = Block(["one", "two"])
    assert_type(words.sum_by(len), int)
    assert_type(block.sum_by(length)(words), int)
    assert_type(Block[int]().sum_by(float), float | Literal[0])
    assert_type(Seq[int]().sum_by(float), float | Literal[0])
    assert_type(seq.sum_by(float)([]), float | Literal[0])
    assert_type(TypedArray[int]().sum_by(float), float | Literal[0])
    assert_type(array.sum_by(as_float)(TypedArray[int]()), float | Literal[0])
    assert_type(Seq[float]().sum(), float | Literal[0])
    assert_type(TypedArray[float]().sum(), float | Literal[0])
    values = TypedArray[int]([1, 2])
    assert_type(values[0], int)
    assert_type(values[:], MutableSequence[int])
    values[0] = 3
    values[:] = [4, 5]
