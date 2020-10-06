from .compose import compose
from .pipe import pipe
from .curry import curried
from .option import Option as TOption, OptionModule as Option, Some, Nothing, option
from .result import Result as TResult, ResultModule as Result, Ok, Error, result


__all__ = [
    'compose', 'pipe', 'curried',
    'Option', 'TOption', 'Some', 'Nothing', 'option',
    'Result', 'TResult', 'Ok', 'Error', 'result',
]
