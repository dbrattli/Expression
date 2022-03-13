"""
A collection of computational expression effects.
"""
from .option import OptionBuilder as option
from .result import ResultBuilder as result
from .result import TryBuilder as try_
from .seq import SeqBuilder as seq

__all__ = ["option", "result", "seq", "try_"]
