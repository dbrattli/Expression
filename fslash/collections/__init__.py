"""
Collection abstractions.
"""

from .seq import Seq as TSeq, SeqModule as Seq
from .list import List as TList, ListModule as List, Cons, Nil


__all__ = [
    'Seq', 'TSeq',
    'List', 'TList', 'Cons', 'Nil'
]
