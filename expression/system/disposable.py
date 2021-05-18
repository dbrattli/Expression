from __future__ import annotations

from abc import ABC, abstractmethod
from asyncio import iscoroutinefunction
from threading import RLock
from types import TracebackType
from typing import Awaitable, Callable, Optional, Type

from .error import ObjectDisposedException


class Disposable(ABC):
    """A disposable class with a context manager. Must implement the
    dispose method. Will dispose on exit."""

    @abstractmethod
    def dispose(self) -> None:
        raise NotImplementedError

    def __enter__(self) -> Disposable:
        """Enter context management."""
        return self

    def __exit__(
        self, exctype: Optional[Type[BaseException]], excinst: Optional[BaseException], exctb: Optional[TracebackType]
    ):
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
    `dispose_async` method. Will dispose on exit."""

    @abstractmethod
    async def dispose_async(self) -> None:
        raise NotImplementedError

    async def __aenter__(self) -> AsyncDisposable:
        """Enter context management."""
        return self

    async def __aexit__(
        self, exctype: Optional[Type[BaseException]], excinst: Optional[BaseException], exctb: Optional[TracebackType]
    ) -> None:
        """Exit context management."""
        await self.dispose_async()

    @staticmethod
    def create(action: Callable[[], Awaitable[None]]) -> AsyncDisposable:
        return AsyncAnonymousDisposable(action)

    @staticmethod
    def composite(*disposables: AsyncDisposable) -> AsyncDisposable:
        return AsyncCompositeDisposable(*disposables)

    @staticmethod
    def empty() -> AsyncDisposable:
        async def anoop() -> None:
            pass

        return AsyncAnonymousDisposable(anoop)


class AsyncAnonymousDisposable(AsyncDisposable):
    def __init__(self, action: Callable[[], Awaitable[None]]) -> None:
        if action:
            assert iscoroutinefunction(action)
        self._is_disposed = False
        self._action = action

    async def dispose_async(self) -> None:
        if self._is_disposed:
            return

        self._is_disposed = True
        await self._action()

    async def __aenter__(self) -> AsyncDisposable:
        if self._is_disposed:
            raise ObjectDisposedException()
        return self


class AsyncCompositeDisposable(AsyncDisposable):
    def __init__(self, *disposables: AsyncDisposable) -> None:
        self._disposables = disposables

    async def dispose_async(self) -> None:
        for disposable in self._disposables:
            await disposable.dispose_async()


__all__ = [
    "Disposable",
    "AnonymousDisposable",
    "AsyncDisposable",
    "AsyncAnonymousDisposable",
    "AsyncCompositeDisposable",
]
