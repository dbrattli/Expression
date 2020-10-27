from abc import abstractmethod
from threading import RLock
from typing import Any, Callable

from .error import ObjectDisposedException


class Disposable:
    """A disposable class with a context manager. Must implement the
    dispose method. Will dispoose on exit."""

    @abstractmethod
    def dispose(self) -> None:
        raise NotImplementedError

    def __enter__(self):
        """Enter context management."""
        pass

    def __exit__(self, type: Any, value: Any, traceback: Any):
        """Exit context management."""

        self.dispose()
        return False

    @staticmethod
    def create(action: Callable[[], None]):
        """Create disposable from action. Will call action when
        disposed."""
        return AnonymousDisposable(action)


class AnonymousDisposable(Disposable):
    def __init__(self, action: Callable[[], None]):
        self._is_disposed = False
        self._action = action
        self._lock = RLock()

    def dispose(self) -> None:
        """Performs the task of cleaning up resources."""

        dispose = False
        with self._lock:
            if not self._is_disposed:
                dispose = True
                self._is_disposed = True

        if dispose:
            self._action()

    def __enter__(self):
        if self._is_disposed:
            raise ObjectDisposedException()


class AsyncDisposable:
    """A disposable class with a context manager. Must implement the
    `adispose` method. Will dispose on exit."""

    @abstractmethod
    async def adispose(self):
        return NotImplemented

    async def __aenter__(self):
        """Enter context management."""
        return self

    async def __aexit__(self, type: Any, value: Any, traceback: Any) -> None:
        """Exit context management."""
        await self.adispose()
