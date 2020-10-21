"""
Core abstractions such as pipes, options and results.
"""

from . import option as Option
from . import result as Result
from . import async_ as Async

from .compose import compose
from .misc import identity, flip
from .pipe import pipe, pipe2, pipe3
from .curry import curried
from .option import Option as Option_, Some, Nothing, Nothing_
from .result import Result as Result_, Ok, Error
from .error import EffectError, failwith
from .builder import Builder


__all__ = [
    "Async",
    "identity",
    "flip",
    "compose",
    "pipe",
    "pipe2",
    "pipe3",
    "curried",
    "Option",
    "Option_",
    "Some",
    "Nothing",
    "Nothing_",
    "Result",
    "Result_",
    "Ok",
    "Error",
    "Builder",
    "failwith",
    "EffectError",
]
