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
    "AsyncReplyChannel",
    "Builder",
    "EffectError",
    "Error",
    "Failure",
    "MailboxProcessor",
    "Nothing",
    "Ok",
    "Option",
    "PipeMixin",
    "Result",
    "Some",
    "Success",
    "SupportsGreaterThan",
    "SupportsLessThan",
    "SupportsMatch",
    "SupportsSum",
    "TailCall",
    "TailCallResult",
    "Try",
    "aiotools",
    "case",
    "compose",
    "curry",
    "curry_flip",
    "default_arg",
    "downcast",
    "failwith",
    "flip",
    "fst",
    "identity",
    "is_error",
    "is_none",
    "is_ok",
    "is_some",
    "option",
    "pipe",
    "pipe2",
    "pipe3",
    "result",
    "snd",
    "tag",
    "tag",
    "tagged_union",
    "tailrec",
    "tailrec_async",
    "try_downcast",
    "upcast",
]
