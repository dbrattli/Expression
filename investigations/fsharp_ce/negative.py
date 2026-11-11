"""Rejected CE uses; marker positions checked by check_typing.py."""

from expression import Error, Ok, Some
from investigations.fsharp_ce.computation import (
    OptionBody,
    ResultBody,
    YieldResultBody,
    computation,
    option,
    result,
    yield_result,
)


@result
def wrong_error() -> ResultBody[int, str]:
    yield from computation(Error(42))  # type-error
    return 1


@result
def wrong_family() -> ResultBody[int, str]:
    yield from computation(Some(42))  # type-error
    return 1


@option
def wrong_option_family() -> OptionBody[int]:
    yield from computation(Ok(42))  # type-error
    return 1


@result
def wrong_return() -> ResultBody[int, str]:
    value = yield from computation(Ok("text"))
    return value  # type-error


@result
def raw_yield() -> ResultBody[int, str]:
    yield 42  # type-error
    return 1


@result
def missing_return() -> ResultBody[int, str]:  # type-error
    yield from computation(Ok(42))


@result
def data_iteration_is_not_binding() -> ResultBody[int, str]:
    yield from Ok(42)  # type-error
    return 1


@yield_result
def legacy_wrong_error_for_disjoint_payload() -> YieldResultBody[str, str]:
    yield from computation(Error(42))  # type-error
    yield "value"


@yield_result
def legacy_wrong_output() -> YieldResultBody[str, str]:
    yield 42  # type-error


@result
def takes_number(number: int) -> ResultBody[int, str]:
    return (yield from computation(Ok(number)))


takes_number("wrong")  # type-error
