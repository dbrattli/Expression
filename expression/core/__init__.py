"""Core abstractions such as pipes, options and results."""

from . import aiotools, option, result
from .builder import Builder
from .compose import compose
from .curry import curry, curry_flip
from .error import EffectError, failwith
from .fn import TailCall, TailCallResult, tailrec, tailrec_async
from .mailbox import AsyncReplyChannel, MailboxProcessor
from .misc import flip, fst, identity, snd
from .option import Nothing, Option, Some, default_arg, is_none, is_some
from .pipe import PipeMixin, pipe, pipe2, pipe3
from .result import Error, Ok, Result, is_error, is_ok
from .tagged_union import case, tag, tagged_union
from .try_ import Failure, Success, Try
from .typing import (
    SupportsGreaterThan,
    SupportsLessThan,
    SupportsMatch,
    SupportsSum,
    downcast,
    try_downcast,
    upcast,
)


__all__ = [
    "aiotools",
    "AsyncReplyChannel",
    "Builder",
    "compose",
    "curry",
    "curry_flip",
    "default_arg",
    "downcast",
    "EffectError",
    "Error",
    "Failure",
    "failwith",
    "flip",
    "fst",
    "identity",
    "is_error",
    "is_none",
    "is_ok",
    "is_some",
    "MailboxProcessor",
    "Nothing",
    "Ok",
    "Option",
    "option",
    "pipe",
    "pipe2",
    "pipe3",
    "PipeMixin",
    "result",
    "Result",
    "tagged_union",
    "snd",
    "Some",
    "Success",
    "SupportsLessThan",
    "SupportsGreaterThan",
    "SupportsMatch",
    "SupportsSum",
    "tag",
    "case",
    "TailCall",
    "TailCallResult",
    "tailrec",
    "tailrec_async",
    "Try",
    "tag",
    "try_downcast",
    "upcast",
]
