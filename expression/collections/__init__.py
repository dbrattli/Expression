"""
Collection abstractions.
"""
from . import frozenlist, map, seq
from .frozenlist import Cons, FrozenList, Nil
from .map import Map
from .seq import Seq

__all__ = [
    "Cons",
    "FrozenList",
    "frozenlist",
    "Map",
    "map",
    "Nil",
    "Seq",
    "seq",
]
