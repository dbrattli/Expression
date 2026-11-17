"""Private asynchronous functional helpers for Result."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Generic, Never, overload

from typing_extensions import TypeVar

from .result import Error, Ok, Result


# Defaults preserve inference on Python 3.12, which cannot express them using
# type-parameter syntax. Keep case-specific overloads for pipe/apipe inference.
_A = TypeVar("_A", default=object)
_U = TypeVar("_U", default=Never)
_F = TypeVar("_F", default=Never)
_R = TypeVar("_R", bound="Ok[object] | Error[object]", default=Never)


class _AsyncMap(Generic[_A, _U]):
    def __init__(self, mapper: Callable[[_A], Awaitable[_U]]) -> None:
        self._mapper = mapper

    @overload
    async def __call__(self, source: Ok[_A]) -> Ok[_U]: ...

    @overload
    async def __call__(self, source: Error[_F]) -> Error[_F]: ...

    @overload
    async def __call__(self, source: Result[_A, _F]) -> Result[_U, _F]: ...

    async def __call__(self, source: Result[_A, _F]) -> Result[_U, _F]:
        return await source.amap(self._mapper)


def amap(mapper: Callable[[_A], Awaitable[_U]]) -> _AsyncMap[_A, _U]:
    """Create an async mapping stage for pipe or apipe.

    Await the returned stage's coroutine to map Ok, preserving Error without
    invoking the callback. Exceptions and cancellation propagate.
    """
    return _AsyncMap(mapper)


class _AsyncBind(Generic[_A, _R]):
    def __init__(self, mapper: Callable[[_A], Awaitable[_R]]) -> None:
        self._mapper = mapper

    @overload
    async def __call__(self, source: Ok[_A]) -> _R: ...

    @overload
    async def __call__(self, source: Error[_F]) -> Error[_F]: ...

    @overload
    async def __call__(self, source: Result[_A, _F]) -> _R | Error[_F]: ...

    async def __call__(self, source: Result[_A, _F]) -> _R | Error[_F]:
        return await source.abind(self._mapper)


def abind(mapper: Callable[[_A], Awaitable[_R]]) -> _AsyncBind[_A, _R]:
    """Create an async binding stage that retains both possible error channels.

    Await the stage's coroutine to bind Ok, preserving Error without invoking the
    callback. Exceptions and cancellation propagate.
    """
    return _AsyncBind(mapper)
