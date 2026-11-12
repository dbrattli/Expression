"""Intentional caller errors; scripts/check_typing.py verifies each marked line."""

from collections.abc import Awaitable, Callable
from typing import Generic, Literal, TypeAlias, TypeVar, final

from expression import Error, MailboxProcessor, Nothing, Option, Result, Some, TaggedUnion, apipe, case, tag
from expression.collections import Block, Map, TypedArray
from expression.extra import async_result
from expression.extra.result import catch


def unchecked(value: Option[int]) -> None:
    _ = value.some  # type-error


def incomplete(value: Option[int]) -> None:
    match value:  # type-error
        case Some(number):
            _ = number


def unchecked_result(value: Result[int, str]) -> None:
    _ = value.ok  # type-error
    _ = value.error  # type-error


def wrong_case(value: Option[int]) -> None:
    if value.tag == "none":
        _ = value.some  # type-error


wrong_payload: Option[int] = Some("wrong")  # type-error
wrong_error_payload: Result[int, str] = Error(42)  # type-error
wrong_block_items: Block[int] = Block.of("wrong")  # type-error
wrong_array_items: TypedArray[int] = TypedArray.of("wrong")  # type-error
wrong_map_values: Map[str, int] = Map.create([("key", "wrong")])  # type-error
missing_payload = Some()  # type-error
contradictory_tag = Some(1, tag="none")  # type-error


class Extra(Some[int]):  # type-error
    pass


_T = TypeVar("_T", covariant=True)


@final
@case
class CustomValue(Generic[_T]):
    value: _T
    tag: Literal["value"] = tag()


@final
@case
class CustomEmpty:
    tag: Literal["empty"] = tag()


Custom: TypeAlias = TaggedUnion[CustomValue[_T] | CustomEmpty]
Untagged: TypeAlias = TaggedUnion[int]  # type-error
PartlyUntagged: TypeAlias = TaggedUnion[CustomValue[int] | int]  # type-error


custom_wrong_payload: Custom[int] = CustomValue("wrong")  # type-error
custom_missing_payload = CustomValue()  # type-error
custom_wrong_generic = CustomValue[int]("wrong")  # type-error
custom_wrong_tag = CustomValue(1, tag="empty")  # type-error
custom_extra_position = CustomValue(1, "value")  # type-error
custom_unit_payload = CustomEmpty(1)  # type-error


def custom_wrong_access(value: Custom[int]) -> None:
    _ = value.value  # type-error
    if value.tag == "empty":
        _ = value.value  # type-error


def custom_incomplete(value: Custom[int]) -> None:
    match value:  # type-error
        case CustomValue(payload):
            _ = payload


def custom_mutation(value: CustomValue[int]) -> None:
    value.value = 2  # type-error
    value.tag = "value"  # type-error


class CustomExtra(CustomValue[int]):  # type-error
    pass


@final
@case
class CustomExplicitTag:
    tag: Literal["explicit"] = tag("explicit")  # type-error


@final
@case(kw_only=True)
class CustomKeyword:
    value: int
    tag: Literal["keyword"] = tag()


custom_positional_keyword_only = CustomKeyword(1)  # type-error


empty_class_is_not_a_value: Option[int] = Nothing  # type-error


class ExtraNothing(Nothing):  # type-error
    pass


async def integer_mailbox_body(inbox: MailboxProcessor[int]) -> None:
    await inbox.receive()


def invalid_mailbox_message() -> None:
    agent = MailboxProcessor.start(integer_mailbox_body)
    agent.post("wrong")  # type-error


# Asynchronous composition must reject incompatible stages and error channels.


async def numeric_stage(value: int) -> int:
    return value + 1


def string_stage(value: str) -> str:
    return value.upper()


async def wrong_async_stage() -> None:
    await apipe(1, numeric_stage, string_stage)  # type-error


async def integer_error(value: int) -> Result[str, int]:
    return Error(42)


StringErrorBind = Callable[[Result[int, str]], Awaitable[Result[str, str]]]
wrong_async_bind: StringErrorBind = async_result.bind(integer_error)  # type-error


# Exception-catching decorators retain positional and keyword parameter types.


def catch_source(value: int, *, suffix: str) -> str:
    return f"{value}{suffix}"


caught_direct = catch(catch_source, exception=ValueError)
caught_decorated = catch(exception=ValueError)(catch_source)
caught_direct("wrong", suffix="!")  # type-error
caught_decorated(1, suffix=2)  # type-error
caught_direct(1, "!")  # type-error
caught_decorated(1)  # type-error
catch(ValueError)  # type-error


# Collection element types and summation projections remain checked.
integers = TypedArray[int]([1, 2])
integers[0] = "wrong"  # type-error
integers[:] = ["wrong"]  # type-error
integers["wrong"]  # type-error
Block([1]).sum_by(str)  # type-error
