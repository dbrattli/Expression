"""Expression library.

Expression aims to be a solid, type-safe, pragmatic, and high
performance library for practical functional programming in Python 3.9+.
By pragmatic we mean that the goal of the library is to use simple
abstractions to enable you to do practical and productive functional
programming in Python.

GitHub: https://github.com/cognitedata/Expression
"""

from . import collections, core, effect
from ._version import __version__
from .core import (
    AsyncReplyChannel,
    Builder,
    EffectError,
    Error,
    Failure,
    MailboxProcessor,
    Nothing,
    Ok,
    Option,
    Result,
    Some,
    Success,
    TailCall,
    TailCallResult,
    Try,
    case,
    compose,
    curry,
    curry_flip,
    default_arg,
    downcast,
    failwith,
    flip,
    fst,
    identity,
    is_error,
    is_none,
    is_ok,
    is_some,
    option,
    pipe,
    pipe2,
    pipe3,
    result,
    snd,
    tag,
    tagged_union,
    tailrec,
    tailrec_async,
    try_downcast,
    upcast,
)


curry_flipped = curry_flip
"""Deprecated.

Will be removed in next major version. Use curry_flip instead.
"""

__all__ = [
    "AsyncReplyChannel",
    "Builder",
    "case",
    "collections",
    "compose",
    "core",
    "curry",
    "curry_flip",
    "curry_flipped",
    "default_arg",
    "downcast",
    "effect",
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
    "option",
    "Option",
    "pipe",
    "pipe2",
    "pipe3",
    "result",
    "Result",
    "snd",
    "Some",
    "Success",
    "tagged_union",
    "TailCall",
    "TailCallResult",
    "tailrec",
    "tailrec_async",
    "Try",
    "tag",
    "try_downcast",
    "upcast",
    "__version__",
]
