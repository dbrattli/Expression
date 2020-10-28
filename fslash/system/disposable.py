from abc import ABC, abstractmethod
from asyncio import iscoroutinefunction
from threading import RLock
from typing import Any, Awaitable, Callable

from .error import ObjectDisposedException


class Disposable(ABC):
    """A disposable class with a context manager. Must implement the
    dispose method. Will dispoose on exit."""

    @abstractmethod
    def dispose(self) -> None:
        raise NotImplementedError

    def __enter__(self) -> "Disposable":
        """Enter context management."""
        return self

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

    def __enter__(self) -> Disposable:
        if self._is_disposed:
            raise ObjectDisposedException()
        return self


class AsyncDisposable(ABC):
    """A disposable class with a context manager. Must implement the
    `adispose` method. Will dispose on exit."""

    @abstractmethod
    async def adispose(self) -> None:
        return NotImplemented

    async def __aenter__(self) -> "AsyncDisposable":
        """Enter context management."""
        return self

    async def __aexit__(self, type: Any, value: Any, traceback: Any) -> None:
        """Exit context management."""
        await self.adispose()

    @staticmethod
    def create(action: Callable[[], Awaitable[None]]):
        return AsyncAnonymousDisposable(action)


class AsyncAnonymousDisposable(AsyncDisposable):
    def __init__(self, action: Callable[[], Awaitable[None]]) -> None:
        if action:
            assert iscoroutinefunction(action)
        self._is_disposed = False
        self._action = action

    async def adispose(self) -> None:
        if not self._is_disposed:
            self._is_disposed = True

            await self._action()

    async def __aenter__(self) -> AsyncDisposable:
        if self._is_disposed:
            raise ObjectDisposedException()
        return self


class AsyncCompositeDisposable(AsyncDisposable):
    def __init__(self, *disposables: AsyncDisposable) -> None:
        self._disposables = disposables

    async def adispose(self) -> None:
        for disposable in self._disposables:
            await disposable.adispose()


__all__ = [
    "Disposable",
    "AnonymousDisposable",
    "AsyncDisposable",
    "AsyncAnonymousDisposable",
    "AsyncCompositeDisposable",
]
