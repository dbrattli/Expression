"""Public Option/Result imports must survive private helper module extraction."""

import subprocess
import sys

import pytest


@pytest.mark.parametrize(
    "first_import",
    [
        "expression.core.option",
        "expression.core.result",
        "expression.core._option_sync",
        "expression.core._option_async",
        "expression.core._result_sync",
        "expression.core._result_async",
    ],
)
def test_value_modules_initialize_in_fresh_interpreter(first_import: str):
    # A subprocess catches partial initialization that cached imports would hide.
    script = '''
import asyncio
import importlib
import pickle
import sys

importlib.import_module(sys.argv[1])
from expression import NOTHING, Error, Nothing, Ok, Option, Result, Some, apipe, option, pipe, result
from expression.core.option import amap as option_amap, bind as option_bind
from expression.core.result import abind as result_abind, map as result_map

assert option.amap is option_amap
assert result.abind is result_abind
assert Some.__module__ == Nothing.__module__ == "expression.core.option"
assert Ok.__module__ == Error.__module__ == "expression.core.result"
assert pickle.loads(pickle.dumps(NOTHING)) is NOTHING
assert pickle.loads(pickle.dumps(Ok(Some(1)))) == Ok(Some(1))
assert pipe(Some(1), option_bind(lambda x: Some(x + 1))) == Some(2)
assert pipe(Ok(1), result_map(str)) == Ok("1")

# Pickles written before extraction still resolve their public helper paths.
assert pickle.loads(b"cexpression.core.option\\nis_some\\n.") is option.is_some
assert pickle.loads(b"cexpression.core.result\\nis_ok\\n.") is result.is_ok

async def stringify(value: int) -> str:
    return str(value)

async def wrap(value: int) -> Result[str, str]:
    return Ok(str(value))

async def check():
    assert await apipe(Some(1), option_amap(stringify)) == Some("1")
    assert await apipe(Ok(1), result_abind(wrap)) == Ok("1")
    assert await option_amap(stringify)(NOTHING) is NOTHING
    error = Error("failure")
    assert await result_abind(wrap)(error) is error

asyncio.run(check())
'''
    completed = subprocess.run([sys.executable, "-c", script, first_import], capture_output=True, text=True, timeout=30)
    assert completed.returncode == 0, completed.stdout + completed.stderr
