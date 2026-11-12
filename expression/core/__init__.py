"""Core abstractions such as pipes, options and results."""

from . import aiotools, option, result, tagged_union
from .apipe import apipe
from .builder import Builder
from .compose import compose
from .curry import curry, curry_flip, pipeable
from .error import EffectError, failwith
from .fn import TailCall, TailCallResult, tailrec, tailrec_async
from .mailbox import AsyncReplyChannel, MailboxProcessor
from .misc import flip, fst, identity, snd
from .option import NOTHING, Nothing, Option, Some, default_arg, is_none, is_some
from .pipe import PipeMixin, pipe, pipe2, pipe3
from .result import Error, Ok, Result, is_error, is_ok
from .tagged_union import TaggedUnion, case, tag
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
    "NOTHING",
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
    "TaggedUnion",
    "TailCall",
    "TailCallResult",
    "Try",
    "aiotools",
    "apipe",
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
    "pipeable",
    "result",
    "snd",
    "tag",
    "tagged_union",
    "tailrec",
    "tailrec_async",
    "try_downcast",
    "upcast",
]
