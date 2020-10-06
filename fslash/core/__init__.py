"""
Core abstractions such as pipes, options and results.
"""

from .compose import compose
from .pipe import pipe, pipe2, pipe3
from .curry import curried
from .option import Option as TOption, OptionModule as Option, Some, Nothing
from .result import Result as TResult, ResultModule as Result, Ok, Error


__all__ = [
    'compose', 'pipe', 'pipe2', 'pipe3', 'curried',
    'Option', 'TOption', 'Some', 'Nothing',
    'Result', 'TResult', 'Ok', 'Error',
]
