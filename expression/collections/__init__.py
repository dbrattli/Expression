"""
Collection abstractions.
"""
from . import asyncseq, block, map, seq
from .block import Block
from .map import Map
from .seq import Seq

__all__ = [
    "asyncseq",
    "Block",
    "block",
    "Map",
    "map",
    "Seq",
    "seq",
]
