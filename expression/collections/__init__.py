"""
Collection abstractions.
"""
from . import asyncseq, frozenlist, map, seq
from .frozenlist import FrozenList
from .map import Map
from .seq import Seq

__all__ = [
    "FrozenList",
    "frozenlist",
    "Map",
    "map",
    "Seq",
    "seq",
]
