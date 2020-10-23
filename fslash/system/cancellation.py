from abc import abstractmethod
from threading import RLock
from typing import Callable, Dict, Optional

from .disposable import Disposable, ObjectDisposedException


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

    @abstractmethod
    def __init__(self, cancelled: Optional[bool] = None, source: "Optional[CancellationTokenSource]" = None) -> None:
        """Should not be used directly. Create cancellation tokens using
        the `CancellationTokenSource` instead."""

        self._cancelled = False if cancelled is None else True
        self._source = CancellationTokenSource.cancelled_source() if source is None else source

    @property
    def is_cancellation_requested(self) -> bool:
        return self._source.is_cancellation_requested

    @property
    def can_be_cancelled(self) -> bool:
        return self._source is not None and self._source.is_cancellation_requested

    def throw_if_cancellation_requested(self):
        if self._source.is_cancellation_requested:
            raise ObjectDisposedException()

    def register(self, callback: Callable[[], None]) -> Disposable:
        return self._source.register_internal(callback)

    @staticmethod
    def none():
        return CancellationToken(False, CancellationTokenSource())


class CancellationTokenSource(Disposable):
    def __init__(self):
        self._lock = RLock()
        self._listeners: Dict[int, Callable[[], None]] = dict()
        self._id = 0

    @property
    def token(self):
        return CancellationToken(False, self)

    @property
    def is_cancellation_requested(self) -> bool:
        return self._disposed

    def cancel(self):
        if self._disposed:
            raise ObjectDisposedException()

        self._disposed = True
        for listener in self._listeners.values():
            listener()

    def register_internal(self, callback: Callable[[], None]):
        if self.is_cancellation_requested:
            raise ObjectDisposedException()

        with self._lock:
            current = self._id
            self._listeners[current] = callback
            self._id += 1

        def dispose():
            with self._lock:
                del self._listeners[current]

        return Disposable(dispose)

    @staticmethod
    def cancelled_source():
        source = CancellationTokenSource()
        source._disposed = True
        return source
