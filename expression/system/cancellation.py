from __future__ import annotations

from threading import RLock
from typing import Callable, Dict, Optional

from .disposable import Disposable
from .error import ObjectDisposedException


class CancellationToken:
    """A `CancellationToken` enables cooperative cancellation between
    threads, thread pool work items, or Task objects. You create a
    cancellation token by instantiating a `CancellationTokenSource`
    object, which manages cancellation tokens retrieved from its
    CancellationTokenSource.Token property. You then pass the
    cancellation token to any number of threads, tasks, or operations
    that should receive notice of cancellation. The token cannot be used
    to initiate cancellation. When the owning object calls
    `CancellationTokenSource.cancel`, the `is_cancellation_requested`
    property on every copy of the cancellation token is set to true. The
    objects that receive the notification can respond in whatever manner
    is appropriate."""

    def __init__(self, cancelled: bool = True, source: Optional[CancellationTokenSource] = None) -> None:
        """Should not be used directly. Create cancellation tokens using
        the `CancellationTokenSource` instead."""

        self._cancelled = cancelled
        self._source = CancellationTokenSource.cancelled_source() if source is None else source

    @property
    def is_cancellation_requested(self) -> bool:
        return not self._cancelled and self._source.is_cancellation_requested

    @property
    def can_be_canceled(self) -> bool:
        return not self._cancelled

    def throw_if_cancellation_requested(self):
        if self.is_cancellation_requested:
            raise ObjectDisposedException()

    def register(self, callback: Callable[[], None]) -> Disposable:
        return self._source.register_internal(callback)

    @staticmethod
    def none():
        return CancellationToken(True, None)


class CancellationTokenSource(Disposable):
    def __init__(self):
        self._is_disposed = False
        self._lock = RLock()
        self._listeners: Dict[int, Callable[[], None]] = dict()
        self._id = 0

    @property
    def token(self) -> CancellationToken:
        return CancellationToken(False, self)

    @property
    def is_cancellation_requested(self) -> bool:
        return self._is_disposed

    def cancel(self) -> None:
        self.dispose()

    def dispose(self) -> None:
        """Performs the task of cleaning up resources."""

        dispose = False
        with self._lock:
            if not self._is_disposed:
                dispose = True

        if dispose:
            self._is_disposed = True
            for listener in self._listeners.values():
                listener()

    def register_internal(self, callback: Callable[[], None]) -> Disposable:
        if self._is_disposed:
            raise ObjectDisposedException()

        with self._lock:
            current = self._id
            self._listeners[current] = callback
            self._id += 1

        def dispose():
            with self._lock:
                del self._listeners[current]

        return Disposable.create(dispose)

    def __enter__(self) -> CancellationToken:
        if self._is_disposed:
            raise ObjectDisposedException()
        return self.token

    @staticmethod
    def cancelled_source() -> CancellationTokenSource:
        source = CancellationTokenSource()
        source.cancel()
        return source
