"""
Core abstractions such as pipes, options and results.
"""

from . import option as Option
from . import result as Result

from .compose import compose
from .misc import identity, flip, ComputationalExpressionError
from .pipe import pipe, pipe2, pipe3
from .curry import curried
from .option import Option as Option_, Some, Nothing, Nothing_
from .result import Result as Result_, Ok, Error


__all__ = [
    'identity', 'flip', 'ComputationalExpressionError',
    'compose', 'pipe', 'pipe2', 'pipe3', 'curried',
    'Option', 'Option_', 'Some', 'Nothing', "Nothing_",
    'Result', 'Result_', 'Ok', 'Error',
]
