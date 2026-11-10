"""Typed short-circuit computations and sequence expressions."""

from .async_option import async_option, async_run_option
from .async_result import async_result, async_run_result, async_try
from .option import OptionScope, option, run_option
from .result import ResultScope, result, run_result, try_
from .seq import SeqBuilder as seq_builder


seq = seq_builder


__all__ = [
    "OptionScope",
    "ResultScope",
    "async_option",
    "async_result",
    "async_run_option",
    "async_run_result",
    "async_try",
    "option",
    "result",
    "run_option",
    "run_result",
    "seq",
    "try_",
]
