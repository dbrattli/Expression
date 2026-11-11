"""Intentional caller errors; scripts/check_typing.py verifies each marked line."""

from typing import Generic, Literal, TypeAlias, TypeVar, final

from expression import Error, Nothing, Option, Result, Some, TaggedUnion, case, tag


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
missing_payload = Some()  # type-error
contradictory_tag = Some(1, tag="none")  # type-error


class Extra(Some[int]):  # type-error
    pass


_T = TypeVar("_T", covariant=True)


@final
@case
class CustomValue(Generic[_T]):
    value: _T
    tag: Literal["value"] = tag("value")


@final
@case
class CustomEmpty:
    tag: Literal["empty"] = tag("empty")


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
class CustomWrongDeclaration:
    tag: Literal["expected"] = tag("different")  # type-error


@final
@case(kw_only=True)
class CustomKeyword:
    value: int
    tag: Literal["keyword"] = tag("keyword")


custom_positional_keyword_only = CustomKeyword(1)  # type-error


empty_class_is_not_a_value: Option[int] = Nothing  # type-error


class ExtraNothing(Nothing):  # type-error
    pass
