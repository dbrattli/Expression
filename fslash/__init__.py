"""
FSlash (F/) aims to be a solid library for practical functional programming in
Python 3.8+ inspired by [F#](https://fsharp.org). By practical we mean that the
goal of the library if to enable you to do meaningful and productive functional
programming in Python instead of being a [Monad
tutorial](https://github.com/dbrattli/OSlash).
"""

from . import core
from . import collections


__all__ = [
    'core', 'collections'
]

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
