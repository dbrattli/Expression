"""
A collection of computational expression effects.
"""
from .option import option_effect as option
from .result import result_effect as result
from .seq import seq_effect as seq

__all__ = ["option", "result", "seq"]
