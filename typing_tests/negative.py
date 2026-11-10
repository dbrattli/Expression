"""Intentional caller errors; scripts/check_typing.py verifies each marked line."""

from expression import Error, Nothing, Ok, Option, Result, Some, effect


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


@effect.result
def wrong_error(scope: effect.ResultScope[str]) -> None:
    scope.bind(Error(42))  # type-error


@effect.result
def wrong_family(scope: effect.ResultScope[str]) -> None:
    scope.bind(Nothing)  # type-error


@effect.option
def wrong_option_family(scope: effect.OptionScope) -> None:
    scope.bind(Ok(42))  # type-error


@effect.result
def wrong_return(scope: effect.ResultScope[str]) -> int:
    return scope.bind(Ok("wrong"))  # type-error


@effect.result
def takes_number(scope: effect.ResultScope[str], number: int) -> bool:
    return scope.bind(Ok(number)) > 0


takes_number("wrong")  # type-error
