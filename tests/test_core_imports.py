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


def test_callable_stages_unpickle_from_original_public_modules():
    import asyncio
    import pickle

    from expression import NOTHING, Ok, Some

    # Protocol-0 fixtures produced before the extraction, including class paths.
    fallback = pickle.loads(
        b'ccopy_reg\n_reconstructor\np0\n(cexpression.core.option\n_DefaultValue\np1\n'
        b'c__builtin__\nobject\np2\nNtp3\nRp4\n(dp5\nV_value\np6\nI7\nsb.'
    )
    mapping = pickle.loads(
        b'ccopy_reg\n_reconstructor\np0\n(cexpression.core.result\n_Map\np1\n'
        b'c__builtin__\nobject\np2\nNtp3\nRp4\n(dp5\nV_mapper\np6\nc__builtin__\nunicode\np7\nsb.'
    )
    async_mapping = pickle.loads(
        b'ccopy_reg\n_reconstructor\np0\n(cexpression.core.option\n_AsyncMap\np1\n'
        b'c__builtin__\nobject\np2\nNtp3\nRp4\n(dp5\nV_mapper\np6\ncexpression.core.aiotools\nsingleton\np7\nsb.'
    )
    async_binding = pickle.loads(
        b'ccopy_reg\n_reconstructor\np0\n(cexpression.core.result\n_AsyncBind\np1\n'
        b'c__builtin__\nobject\np2\nNtp3\nRp4\n(dp5\nV_mapper\np6\ncexpression.core.aiotools\nsingleton\np7\nsb.'
    )
    assert fallback(NOTHING) == 7
    assert mapping(Ok(1)) == Ok("1")
    assert asyncio.run(async_mapping(Some(1))) == Some(1)
    assert asyncio.run(async_binding(Ok(Ok(1)))) == Ok(1)
