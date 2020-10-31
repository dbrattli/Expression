"""
Core abstractions such as pipes, options and results.
"""

from . import async_ as Async
from . import option as Option
from . import result as Result
from .builder import Builder
from .compose import compose
from .curry import curried
from .error import EffectError, failwith
from .mailbox import AsyncReplyChannel, MailboxProcessor
from .misc import flip, identity
from .option import Nothing, Nothing_
from .option import Option as Option_
from .option import Some
from .pipe import pipe, pipe2, pipe3
from .result import Error, Ok
from .result import Result as Result_

__all__ = [
    "Async",
    "AsyncReplyChannel",
    "Builder",
    "compose",
    "curried",
    "EffectError",
    "Error",
    "failwith",
    "flip",
    "identity",
    "MailboxProcessor",
    "Nothing",
    "Nothing_",
    "Ok",
    "Option",
    "Option_",
    "pipe",
    "pipe2",
    "pipe3",
    "Result",
    "Result_",
    "Some",
]
