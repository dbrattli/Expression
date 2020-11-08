"""
Core abstractions such as pipes, options and results.
"""

from . import aio, option, result
from .builder import Builder
from .compose import compose
from .curry import curried
from .error import EffectError, failwith
from .fn import TailCall, recursive, recursive_async
from .mailbox import AsyncReplyChannel, MailboxProcessor
from .misc import flip, identity
from .option import Nothing, Nothing_, Option, Some
from .pipe import pipe, pipe2, pipe3
from .result import Error, Ok, Result

__all__ = [
    "aio",
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
    "option",
    "pipe",
    "pipe2",
    "pipe3",
    "recursive",
    "recursive_async",
    "result",
    "Result",
    "Some",
    "TailCall",
]
