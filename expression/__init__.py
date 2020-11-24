"""
Expression aims to be a solid, type-safe, pragmatic, and high
performance library for practical functional programming in Python 3.8+.
By pragmatic we mean that the goal of the library is to use simple
abstractions to enable you to do practical and productive functional
programming in Python.

GitHub: https://github.com/dbrattli/Expression
"""

from . import collections, core, effect

__all__ = ["core", "collections", "effect"]

from ._version import get_versions

__version__ = get_versions()["version"]  # type: ignore
del get_versions
