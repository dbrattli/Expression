from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING, Any

import pytest

from expression import Ok, Some, option, pipe, result
from expression.core.option import BaseOption
from expression.core.result import BaseResult
from expression.extra.option import apply as option_apply
from expression.extra.option.apply import main as option_main
from expression.extra.result import apply as result_apply
from expression.extra.result.apply import main as result_main

if TYPE_CHECKING:
    from collections.abc import Callable

RESULT = "result"
DUMMY = "dummy"


def _no_params() -> tuple[()]:
    return ()


def _only_positional(a: int, b: str, /) -> tuple[int, str]:
    return (a, b)


def _slash_and_keyword(a: int, b: str, /, c: bytes) -> tuple[int, str, bytes]:
    return (a, b, c)


def _asterisk_and_keyword(a: int, b: str, *, c: bytes) -> tuple[int, str, bytes]:
    return (a, b, c)


def _args(*args: int) -> tuple[int, ...]:
    return args


def _kwargs(**kwargs: int) -> dict[str, int]:
    return kwargs


def _args_and_kwargs(
    *args: int,
    **kwargs: int,
) -> tuple[tuple[int, ...], dict[str, int]]:
    return (args, kwargs)


ONLY_POSITIONAL_FUNCS = (
    _no_params,
    _only_positional,
    _args,
)
WITH_KEYWORD_FUNCS = (
    _slash_and_keyword,
    _asterisk_and_keyword,
    _kwargs,
    _args_and_kwargs,
)


def test_option_var():
    value = 1
    var = option_apply.of_obj(value)

    assert isinstance(var, option_main.Var)
    assert pipe(var.value, option.is_some) is True
    assert pipe(var.value, option.is_none) is False
    assert var.value.default_value(0) == value


def test_option_seq():
    value = (1, "q", 3)
    seq = option_apply.of_iterable(*value)

    assert isinstance(seq, option_main.Seq)
    assert pipe(seq.value, option.is_some) is True
    assert pipe(seq.value, option.is_none) is False
    assert seq.value.default_value((-1, "w", 10)) == value


def test_option_func():
    func = option_apply.func(_func_two)

    assert isinstance(func, option_main.Func)
    assert pipe(func.value, option.is_some) is True
    assert pipe(func.value, option.is_none) is False
    assert func.value.default_value(_other_func_two) is _func_two


def test_call_option_func():
    func = option_apply.func(_func_zero)

    var_0 = func * option_apply.call
    var_1 = option_apply.call * func

    for var in (var_0, var_1):
        assert isinstance(var, BaseOption)
        assert var.default_value(DUMMY) == RESULT


def test_option_var_to_seq():
    value_0, value_1 = 1, "q"
    dummy_0, dummy_1 = (2, "w"), ("a", -1)
    var_0, var_1 = option_apply.of_obj(value_0), option_apply.of_obj(value_1)
    seq_0, seq_1 = var_0 * var_1, var_1 * var_0

    for seq in seq_0, seq_1:
        assert isinstance(seq, option_main.Seq)
    assert seq_0.value.default_value(dummy_0) == (value_0, value_1)
    assert seq_1.value.default_value(dummy_1) == (value_1, value_0)


def test_option_var_func():
    value = 1
    dummy = -100
    output = _func_one(value)
    assert dummy != output

    var = option_apply.of_obj(value)
    assert isinstance(var, option_main.Var)
    func_0 = _func_one * var
    func_1 = option_apply.func(_func_one) * var
    var_0, var_1 = func_0 * option_apply.call, func_1 * option_apply.call

    for var in (var_0, var_1):
        assert isinstance(var, BaseOption)
        assert var.default_value(dummy) == output


def test_option_seq_func():
    values = (1, "q")
    dummy = (-100, "a")
    output = _func_two(*values)
    assert dummy != output

    seq = option_apply.of_iterable(*values)
    assert isinstance(seq, option_main.Seq)

    func = option_apply.func(_func_two) * seq
    var = func * option_apply.call

    assert isinstance(var, BaseOption)
    assert var.default_value(dummy) == output


def test_option_func_arg_order():
    value_0, value_1 = 1, "q"
    dummy = (-100, "a")
    output = _func_two(value_0, value_1)
    assert dummy != output

    var_0, var_1 = option_apply.of_obj(value_0), option_apply.of_obj(value_1)
    func = option_apply.func(_func_two)

    result_0 = func * var_0 * var_1 * option_apply.call
    result_1 = var_0 * func * var_1 * option_apply.call
    result_2 = var_0 * var_1 * func * option_apply.call

    for sub_result in result_0, result_1, result_2:
        assert isinstance(sub_result, BaseOption)
        assert sub_result.default_value(dummy) == output


def test_result_var():
    value = 1
    var = result_apply.of_obj(value)

    assert isinstance(var, result_main.Var)
    assert pipe(var.value, result.is_ok) is True
    assert pipe(var.value, result.is_error) is False
    assert var.value.default_value(0) == value


def test_result_seq():
    value = (1, "q", 3)
    seq = result_apply.of_iterable(*value)

    assert isinstance(seq, result_main.Seq)
    assert pipe(seq.value, result.is_ok) is True
    assert pipe(seq.value, result.is_error) is False
    assert seq.value.default_value((-1, "w", 10)) == value


def test_result_func():
    func = result_apply.func(_func_two)

    assert isinstance(func, result_main.Func)
    assert pipe(func.value, result.is_ok) is True
    assert pipe(func.value, result.is_error) is False
    assert func.value.default_value(_other_func_two) is _func_two


def test_call_result_func():
    func = result_apply.func(_func_zero)

    var_0 = func * result_apply.call
    var_1 = result_apply.call * func

    for var in (var_0, var_1):
        assert isinstance(var, BaseResult)
        assert var.default_value(DUMMY) == RESULT


def test_result_var_to_seq():
    value_0, value_1 = 1, "q"
    dummy_0, dummy_1 = (2, "w"), ("a", -1)
    var_0, var_1 = result_apply.of_obj(value_0), result_apply.of_obj(value_1)
    seq_0, seq_1 = var_0 * var_1, var_1 * var_0

    for seq in seq_0, seq_1:
        assert isinstance(seq, result_main.Seq)
    assert seq_0.value.default_value(dummy_0) == (value_0, value_1)
    assert seq_1.value.default_value(dummy_1) == (value_1, value_0)


def test_result_var_func():
    value = 1
    dummy = -100
    output = _func_one(value)
    assert dummy != output

    var = result_apply.of_obj(value)
    assert isinstance(var, result_main.Var)
    func_0 = _func_one * var
    func_1 = result_apply.func(_func_one) * var
    var_0, var_1 = func_0 * result_apply.call, func_1 * result_apply.call

    for var in (var_0, var_1):
        assert isinstance(var, BaseResult)
        assert var.default_value(dummy) == output


def test_result_seq_func():
    values = (1, "q")
    dummy = (-100, "a")
    output = _func_two(*values)
    assert dummy != output

    seq = result_apply.of_iterable(*values)
    assert isinstance(seq, result_main.Seq)

    func = result_apply.func(_func_two) * seq
    var = func * result_apply.call

    assert isinstance(var, BaseResult)
    assert var.default_value(dummy) == output


def test_result_func_arg_order():
    value_0, value_1 = 1, "q"
    dummy = (-100, "a")
    output = _func_two(value_0, value_1)
    assert dummy != output

    var_0, var_1 = result_apply.of_obj(value_0), result_apply.of_obj(value_1)
    func = result_apply.func(_func_two)

    result_0 = func * var_0 * var_1 * result_apply.call
    result_1 = var_0 * func * var_1 * result_apply.call
    result_2 = var_0 * var_1 * func * result_apply.call

    for sub_result in result_0, result_1, result_2:
        assert isinstance(sub_result, BaseResult)
        assert sub_result.default_value(dummy) == output


def test_option_partial_func():
    value_0, value_1, value_2 = 0, "q", b"w"
    func = option_apply.func(_func_three)

    var_0, var_1, var_2 = (
        option_apply.of_obj(value_0),
        option_apply.of_obj(value_1),
        option_apply.of_obj(value_2),
    )
    partial_one_func = option_main.Func(Some(partial(_func_three, value_0)))

    result_0 = func * var_0 * var_1 * var_2 * option_apply.call
    result_1 = partial_one_func * var_1 * var_2 * option_apply.call
    assert result_0 == result_1

    seq = option_apply.of_iterable(value_0, value_1)
    assert seq == var_0 * var_1
    partial_two_func = option_main.Func(Some(partial(_func_three, value_0, value_1)))

    result_2 = func * seq * var_2 * option_apply.call
    result_3 = partial_two_func * var_2 * option_apply.call
    assert result_2 == result_3


def test_result_partial_func():
    value_0, value_1, value_2 = 0, "q", b"w"
    func = result_apply.func(_func_three)

    var_0, var_1, var_2 = (
        result_apply.of_obj(value_0),
        result_apply.of_obj(value_1),
        result_apply.of_obj(value_2),
    )
    _partial_one_func: Ok[Callable[[str, bytes], tuple[int, str, bytes]], Any] = Ok(
        partial(_func_three, value_0),
    )
    partial_one_func = result_main.Func(_partial_one_func)

    result_0 = func * var_0 * var_1 * var_2 * result_apply.call
    result_1 = partial_one_func * var_1 * var_2 * result_apply.call
    assert result_0 == result_1

    seq = result_apply.of_iterable(value_0, value_1)
    assert seq == var_0 * var_1
    _partial_two_func: Ok[Callable[[bytes], tuple[int, str, bytes]], Any] = Ok(
        partial(_func_three, value_0, value_1),
    )
    partial_two_func = result_main.Func(_partial_two_func)

    result_2 = func * seq * var_2 * result_apply.call
    result_3 = partial_two_func * var_2 * result_apply.call
    assert result_2 == result_3


def test_option_func_call():
    func = option_apply.func(_func_one)
    value = 1
    var = option_apply.of_obj(value)
    assert func(value) == func * var * option_apply.call

    func = option_apply.func(_func_two)
    values = 1, "q"
    seq = option_apply.of_iterable(*values)
    assert func(*values) == func * seq * option_apply.call


def test_result_func_call():
    func = result_apply.func(_func_one)
    value = 1
    var = result_apply.of_obj(value)
    assert func(value) == func * var * result_apply.call

    func = result_apply.func(_func_two)
    values = 1, "q"
    seq = result_apply.of_iterable(*values)
    assert func(*values) == func * seq * result_apply.call


@pytest.mark.parametrize("func", ONLY_POSITIONAL_FUNCS)
def test_create_func_object(func: Callable[..., Any]):
    option_apply.func(func)
    result_apply.func(func)


@pytest.mark.parametrize("func", WITH_KEYWORD_FUNCS)
def test_error_create_func_object(func: Callable[..., Any]):
    pytest.raises(TypeError, option_apply.func, func)
    pytest.raises(TypeError, result_apply.func, func)


def _func_zero() -> str:
    return RESULT


def _func_one(a: int) -> int:
    return a + 1


def _func_two(a: int, b: str) -> tuple[int, str]:
    return (a, b)


def _other_func_two(a: int, b: str) -> tuple[int, str]:
    return (a, b)


def _func_three(a: int, b: str, c: bytes) -> tuple[int, str, bytes]:
    return (a, b, c)
