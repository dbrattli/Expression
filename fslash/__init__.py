"""
FSlash (F/) is a ...
"""

from .compose import compose
from .pipe import pipe
from .curry import curried
from .option import Option as TOption, OptionModule as Option, Some, Nothing, option
from .result import Result as TResult, ResultModule as Result, Ok, Error, result
from .seq import Seq as TSeq, SeqModule as Seq, seq


__all__ = [
    'compose', 'pipe', 'curried',
    'Option', 'TOption', 'Some', 'Nothing', 'option',
    'Result', 'TResult', 'Ok', 'Error', 'result',
    'Seq', 'TSeq', 'seq'
]

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
