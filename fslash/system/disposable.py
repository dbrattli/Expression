from threading import RLock
from typing import Any, Callable


class ObjectDisposedException(Exception):
    def __init__(self):
        super().__init__("The operation was canceled")


class Disposable:
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

    def __exit__(self, type: Any, value: Any, traceback: Any):
        self.dispose()
        return False
