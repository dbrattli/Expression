"""Type contracts for let!, return, and tail return! on computation values."""

from typing import Never, assert_type

from expression import NOTHING, Error, Ok, Option, Result, Some
from investigations.fsharp_ce.computation import (
    OptionBody,
    OptionComputation,
    ResultBody,
    ResultComputation,
    computation,
    option,
    result,
)


def parse_number(text: str) -> ResultComputation[int, str]:
    return computation(Ok(int(text)) if text.isdigit() else Error("invalid number"))


@result
def describe(text: str) -> ResultBody[str, str]:
    number = yield from parse_number(text)
    label = yield from computation(Ok("items"))
    assert_type(number, int)
    assert_type(label, str)
    return f"{number} {label}"


@result
def forward(text: str) -> ResultBody[str, str]:
    return (yield from describe(text))


@option
def optional(value: Option[int]) -> OptionBody[str]:
    number = yield from computation(value)
    assert_type(number, int)
    return str(number)


assert_type(describe("3"), ResultComputation[str, str])
assert_type(describe("3").run(), Result[str, str])
assert_type(optional(Some(3)), OptionComputation[str])
assert_type(optional(Some(3)).run(), Option[str])
assert_type(computation(NOTHING), OptionComputation[Never])
