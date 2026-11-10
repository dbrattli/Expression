"""Strict consumer typing contracts for the experimental adapter."""

from typing import assert_type

from expression import NOTHING, Error, Ok, Option, Result, Some
from investigations.typed_generators.adapter import OptionComputation, ResultComputation, bind, option, result


@result
def workflow(value: Result[int, str], *, suffix: str = "!") -> ResultComputation[bool, str]:
    number = yield from bind(value)
    text = yield from bind(Ok(str(number)))
    assert_type(number, int)
    assert_type(text, str)
    return text + suffix == "42!"


@option
def optional_workflow(value: Option[int]) -> OptionComputation[str]:
    number = yield from bind(value)
    text = yield from bind(Some(str(number)))
    assert_type(number, int)
    assert_type(text, str)
    return text


@result
def direct_error() -> ResultComputation[int, str]:
    return (yield from bind(Error("failed")))


@option
def direct_absence() -> OptionComputation[int]:
    return (yield from bind(NOTHING))


@result
def bare_yield() -> ResultComputation[None, str]:
    # A direct yield can check an effect, but cannot receive its payload.
    received = yield Ok(42)
    assert_type(received, None)
    return received


assert_type(workflow(Ok(42), suffix="?"), Result[bool, str])
assert_type(optional_workflow(Some(42)), Option[str])
assert_type(direct_error(), Result[int, str])
assert_type(direct_absence(), Option[int])
