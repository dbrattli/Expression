"""A collection of computational expression effects."""

from .option import OptionBuilder as option
from .result import ResultBuilder as result
from .result import TryBuilder as try_
from .seq import SeqBuilder as seq_builder
from .async_result import AsyncResultBuilder as async_result
from .async_result import AsyncTryBuilder as async_try


seq = seq_builder


__all__ = ["option", "result", "seq", "try_", "async_result", "async_try"]
