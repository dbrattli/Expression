from .compose import compose
from .pipe import pipe
from .option import Option as TOption, OptionModule as Option, Some, Nothing, option
from .result import Result, Ok, Error, result
from .seq import SeqModule as Seq, seq


__all__ = [
    'compose', 'pipe',
    'Option', 'TOption', 'Some', 'Nothing', 'option',
    'Result', 'Ok', 'Error', 'result',
    'Seq', 'seq'
]

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
