"""Contains extra functionality for core modules.

Pipelining i.e composition (kliesli) of result or option returning
functions.
"""

from . import option, result, pipe, async_result


__all__ = ["option", "result", "pipe", "async_result"]
