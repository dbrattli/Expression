"""
Collection abstractions.
"""
from . import frozenlist, seq
from .frozenlist import Cons, FrozenList, Nil
from .seq import Seq

__all__ = ["Seq", "seq", "FrozenList", "frozenlist", "Cons", "Nil"]
