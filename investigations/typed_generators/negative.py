"""Expected type errors; checked by check_typing.py, never executed."""

from typing import Never

from expression import NOTHING, Error, Ok, Some
from investigations.typed_generators.adapter import OptionComputation, ResultComputation, bind, option, result


@result
def wrong_error() -> ResultComputation[int, str]:
    yield from bind(Error(42))  # type-error
    return 1


@result
def wrong_family() -> ResultComputation[int, str]:
    yield from bind(Some(42))  # type-error
    return 1


@result
def wrong_empty_family() -> ResultComputation[int, str]:
    yield from bind(NOTHING)  # type-error
    return 1


@option
def wrong_option_family() -> OptionComputation[int]:
    yield from bind(Ok(42))  # type-error
    return 1


@result
def wrong_return() -> ResultComputation[int, str]:
    text = yield from bind(Ok("text"))
    return text  # type-error


@result
def raw_yield() -> ResultComputation[int, str]:
    yield 42  # type-error
    return 1


@result
def wrong_direct_error() -> ResultComputation[int, str]:
    yield Error(42)  # type-error
    return 1


@result
def direct_iteration() -> ResultComputation[int, str]:
    yield from Ok(42)  # type-error
    return 1


@result
def wrong_payload_operation() -> ResultComputation[int, str]:
    text = yield from bind(Ok("text"))
    return text + 1  # type-error


@result
def bare_yield_has_no_payload() -> ResultComputation[int, str]:
    number: int = yield Ok(42)  # type-error
    return number


@result
def takes_number(number: int) -> ResultComputation[int, str]:
    return (yield from bind(Ok(number)))


takes_number("wrong")  # type-error


@result  # type-error
def plain_body() -> int:
    return 42


# Checker limitation: yield-from of a Never-returning adapter is not considered
# terminating control flow. Annotate the intended successful type instead.
def error_only_never() -> ResultComputation[Never, str]:  # type-error
    yield from bind(Error("failed"))
