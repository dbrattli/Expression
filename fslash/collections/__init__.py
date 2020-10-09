"""
Collection abstractions.
"""
from . import seq as Seq
from . import list as List

from .seq import Seq as Seq_
from .list import List as List_, Cons, Nil


__all__ = [
    'Seq', 'Seq_',
    'List', 'List_', 'Cons', 'Nil'
]
