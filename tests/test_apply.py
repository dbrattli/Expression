from expression import option, pipe, result
from expression.core.option import BaseOption
from expression.core.result import BaseResult
from expression.extra.option import apply as option_apply
from expression.extra.result import apply as result_apply

RESULT = "result"
DUMMY = "dummy"


def test_option_var():
    value = 1
    var = option_apply.of_obj(value)

    assert isinstance(var, option_apply.Var)
    assert pipe(var.value, option.is_some) is True
    assert pipe(var.value, option.is_none) is False
    assert var.value.default_value(0) == value


def test_option_seq():
    value = (1, "q", 3)
    seq = option_apply.of_iterable(*value)

    assert isinstance(seq, option_apply.Seq)
    assert pipe(seq.value, option.is_some) is True
    assert pipe(seq.value, option.is_none) is False
    assert seq.value.default_value((-1, "w", 10)) == value


def test_option_func():
    func = option_apply.func(_func_two)

    assert isinstance(func, option_apply.Func)
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
        assert isinstance(seq, option_apply.Seq)
    assert seq_0.value.default_value(dummy_0) == (value_0, value_1)
    assert seq_1.value.default_value(dummy_1) == (value_1, value_0)


def test_option_var_func():
    value = 1
    dummy = -100
    output = _func_one(value)
    assert dummy != output

    var = option_apply.of_obj(value)
    assert isinstance(var, option_apply.Var)
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
    assert isinstance(seq, option_apply.Seq)
    func_0 = _func_two * seq
    func_1 = option_apply.func(_func_two) * seq
    var_0, var_1 = func_0 * option_apply.call, func_1 * option_apply.call

    for var in (var_0, var_1):
        assert isinstance(var, BaseOption)
        assert var.default_value(dummy) == output


def test_option_func_arg_order():
    value_0, value_1 = 1, "q"
    dummy = (-100, "a")
    output = _func_two(value_0, value_1)
    assert dummy != output

    var_0, var_1 = option_apply.of_obj(value_0), option_apply.of_obj(value_1)

    result_0 = _func_two * var_0 * var_1 * option_apply.call
    result_1 = var_0 * _func_two * var_1 * option_apply.call
    result_2 = var_0 * var_1 * _func_two * option_apply.call

    for sub_result in result_0, result_1, result_2:
        assert isinstance(sub_result, BaseOption)
        assert sub_result.default_value(dummy) == output


def test_result_var():
    value = 1
    var = result_apply.of_obj(value)

    assert isinstance(var, result_apply.Var)
    assert pipe(var.value, result.is_ok) is True
    assert pipe(var.value, result.is_error) is False
    assert var.value.default_value(0) == value


def test_result_seq():
    value = (1, "q", 3)
    seq = result_apply.of_iterable(*value)

    assert isinstance(seq, result_apply.Seq)
    assert pipe(seq.value, result.is_ok) is True
    assert pipe(seq.value, result.is_error) is False
    assert seq.value.default_value((-1, "w", 10)) == value


def test_result_func():
    func = result_apply.func(_func_two)

    assert isinstance(func, result_apply.Func)
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
        assert isinstance(seq, result_apply.Seq)
    assert seq_0.value.default_value(dummy_0) == (value_0, value_1)
    assert seq_1.value.default_value(dummy_1) == (value_1, value_0)


def test_result_var_func():
    value = 1
    dummy = -100
    output = _func_one(value)
    assert dummy != output

    var = result_apply.of_obj(value)
    assert isinstance(var, result_apply.Var)
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
    assert isinstance(seq, result_apply.Seq)
    func_0 = _func_two * seq
    func_1 = result_apply.func(_func_two) * seq
    var_0, var_1 = func_0 * result_apply.call, func_1 * result_apply.call

    for var in (var_0, var_1):
        assert isinstance(var, BaseResult)
        assert var.default_value(dummy) == output


def test_result_func_arg_order():
    value_0, value_1 = 1, "q"
    dummy = (-100, "a")
    output = _func_two(value_0, value_1)
    assert dummy != output

    var_0, var_1 = result_apply.of_obj(value_0), result_apply.of_obj(value_1)

    result_0 = _func_two * var_0 * var_1 * result_apply.call
    result_1 = var_0 * _func_two * var_1 * result_apply.call
    result_2 = var_0 * var_1 * _func_two * result_apply.call

    for sub_result in result_0, result_1, result_2:
        assert isinstance(sub_result, BaseResult)
        assert sub_result.default_value(dummy) == output


def _func_zero() -> str:
    return RESULT


def _func_one(a: int) -> int:
    return a + 1


def _func_two(a: int, b: str) -> tuple[int, str]:
    return (a, b)


def _other_func_two(a: int, b: str) -> tuple[int, str]:
    return (a, b)
