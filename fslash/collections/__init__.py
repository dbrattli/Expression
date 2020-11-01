"""
Collection abstractions.
"""
from . import list, seq
from .list import Cons, List, Nil
from .seq import Seq

__all__ = ["Seq", "seq", "List", "list", "Cons", "Nil"]
