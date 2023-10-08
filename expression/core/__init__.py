"""Core abstractions such as pipes, options and results."""

from . import aiotools, option, result
from .builder import Builder
from .choice import (
    Choice,
    Choice1of2,
    Choice1of3,
    Choice2,
    Choice2of2,
    Choice2of3,
    Choice3,
    Choice3of3,
)
from .compose import compose
from .curry import curry, curry_flip
from .error import EffectError, failwith
from .fn import TailCall, TailCallResult, tailrec, tailrec_async
from .mailbox import AsyncReplyChannel, MailboxProcessor
from .misc import flip, fst, identity, snd
from .option import Nothing, Nothing_, Option, Some, default_arg, is_none, is_some
from .pipe import PipeMixin, pipe, pipe2, pipe3
from .result import Error, Ok, Result, is_error, is_ok
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
from .union import SingleCaseUnion, Tag, TaggedUnion, tag


__all__ = [
    "aiotools",
    "AsyncReplyChannel",
    "Builder",
    "Choice",
    "Choice2",
    "Choice3",
    "Choice1of2",
    "Choice2of2",
    "Choice1of3",
    "Choice2of3",
    "Choice3of3",
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
    "Nothing_",
    "Ok",
    "Option",
    "option",
    "pipe",
    "pipe2",
    "pipe3",
    "PipeMixin",
    "result",
    "Result",
    "SingleCaseUnion",
    "snd",
    "Some",
    "Success",
    "SupportsLessThan",
    "SupportsGreaterThan",
    "SupportsMatch",
    "SupportsSum",
    "Tag",
    "TaggedUnion",
    "TailCall",
    "TailCallResult",
    "tailrec",
    "tailrec_async",
    "Try",
    "tag",
    "try_downcast",
    "upcast",
]
