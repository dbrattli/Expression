"""
A collection of computational expression builders.
"""
from .option import option_builder as option
from .result import result_builder as result
from .seq import seq

__all__ = ["option", "result", "seq"]
