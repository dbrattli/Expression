"""
Core abstractions such as pipes, options and results.
"""

from . import aiotools, option, result
from .builder import Builder
from .compose import compose
from .curry import curried
from .error import EffectError, failwith
from .fn import TailCall, TailCallResult, tailrec, tailrec_async
from .mailbox import AsyncReplyChannel, MailboxProcessor
from .match import Matchable, Matcher, Pattern, match
from .misc import flip, fst, identity, snd
from .option import Nothing, Nothing_, Option, Some
from .pipe import pipe, pipe2, pipe3
from .result import Error, Ok, Result

__all__ = [
    "aiotools",
    "AsyncReplyChannel",
    "Builder",
    "compose",
    "curried",
    "EffectError",
    "Error",
    "failwith",
    "flip",
    "fst",
    "identity",
    "MailboxProcessor",
    "match",
    "Matcher",
    "Matchable",
    "Nothing",
    "Nothing_",
    "Ok",
    "Option",
    "option",
    "Pattern",
    "pipe",
    "pipe2",
    "pipe3",
    "result",
    "Result",
    "snd",
    "Some",
    "TailCall",
    "TailCallResult",
    "tailrec",
    "tailrec_async",
]
