"""Consumer contracts checked by Pyright alongside the runtime tests."""

from __future__ import annotations

from dataclasses import field
from typing import Generic, Literal, Never, TypeAlias, TypeVar, assert_never, assert_type, final

from expression import (
    Error,
    Nothing,
    NothingType,
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


def option_contract(value: Option[int]) -> None:
    assert_type(Some(42), Some[int])
    assert_type(Nothing, NothingType)
    assert_type(value.map(str), Option[str])
    assert_type(Nothing.or_else(Some(42)), Some[int])
    assert_type(value.pipe(option.map(str)), Option[str])
    items: list[int] = value.to_list()
    assert_type(items, list[int])
    if option.is_some(value):
        assert_type(value.some, int)
    match value:
        case Some(payload):
            assert_type(payload, int)
        case NothingType():
            pass
        case _:
            assert_never(value)


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


@effect.result
def workflow(scope: effect.ResultScope[str], number: int, *, suffix: str = "!") -> bool:
    value = scope.bind(Ok(number))
    text = scope.bind(Some(str(value)).to_result("missing"))
    assert_type(value, int)
    assert_type(text, str)
    return text.endswith(suffix)


@effect.option
def optional_workflow(scope: effect.OptionScope, value: Option[int]) -> str:
    number = scope.bind(value)
    text = scope.bind(Some(str(number)))
    assert_type(number, int)
    assert_type(text, str)
    return text


@effect.async_result
async def asynchronous_workflow(scope: effect.ResultScope[str], value: Result[int, str]) -> bool:
    number = scope.bind(value)
    assert_type(number, int)
    return number > 0


def decorated_contracts() -> None:
    assert_type(workflow(1, suffix="?"), Result[bool, str])
    assert_type(optional_workflow(Some(42)), Option[str])


def direct_failure(scope: effect.ResultScope[str]) -> Never:
    scope.bind(Error("failed"))


async def asynchronous_contract() -> None:
    assert_type(await asynchronous_workflow(Ok(1)), Result[bool, str])


_T = TypeVar("_T", covariant=True)


@final
@case
class Circle:
    radius: float
    tag: Literal["circle"] = tag("circle")


@final
@case
class Rectangle:
    width: float
    height: float
    label: str = field(default="", kw_only=True)
    tag: Literal["rectangle"] = tag("rectangle")


Shape: TypeAlias = TaggedUnion[Circle | Rectangle]


@final
@case
class Just(Generic[_T]):
    value: _T
    tag: Literal["just"] = tag("just")


@final
@case
class Missing:
    tag: Literal["missing"] = tag("missing")


Maybe: TypeAlias = TaggedUnion[Just[_T] | Missing]


@final
@case(kw_only=True)
class Request:
    path: str
    retries: int = 3
    tag: Literal["request"] = tag("request")


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
    tag: Literal["branch"] = tag("branch")


@final
@case
class Leaf:
    value: int
    tag: Literal["leaf"] = tag("leaf")


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
