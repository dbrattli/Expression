"""Consumer contracts checked by Pyright alongside the runtime tests."""

from typing import Never, assert_never, assert_type

from expression import Error, Nothing, NothingType, Ok, Option, Result, Some, effect, option, result


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
