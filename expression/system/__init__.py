"""The system module.

Contains tools and utilities for dealing with (async) disposables and
cancellation tokens.
"""
from .cancellation import CancellationToken, CancellationTokenSource
from .disposable import (
    AnonymousDisposable,
    AsyncAnonymousDisposable,
    AsyncCompositeDisposable,
    AsyncDisposable,
    Disposable,
)
from .error import ObjectDisposedException, OperationCanceledError

__all__ = [
    "AsyncDisposable",
    "AsyncAnonymousDisposable",
    "AsyncCompositeDisposable",
    "CancellationToken",
    "CancellationTokenSource",
    "Disposable",
    "AnonymousDisposable",
    "ObjectDisposedException",
    "OperationCanceledError",
]
