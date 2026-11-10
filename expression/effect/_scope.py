"""Invocation ownership for typed short-circuit computations."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from inspect import Signature, signature
from threading import get_ident
from typing import Generic, TypeVar

from expression.core.result import Error


_E = TypeVar("_E")
_F = TypeVar("_F", bound=Callable[..., object])


class Abort(BaseException):
    """A control signal handled only by its owning computation."""

    def __init__(self, owner: object) -> None:
        self.owner = owner


def _current_task() -> object:
    try:
        return asyncio.current_task()
    except RuntimeError:
        return None


class Invocation:
    """Track the lifetime and execution context of one computation."""

    def __init__(self) -> None:
        self.owner = object()
        self.active = True
        self.thread = get_ident()
        self.task = _current_task()

    def check(self) -> None:
        if not self.active:
            raise RuntimeError("The computation scope is no longer active")
        if self.thread != get_ident() or self.task is not _current_task():
            raise RuntimeError("The computation scope belongs to another execution context")

    def close(self) -> None:
        self.active = False


def hide_scope_parameter(wrapper: _F, body: Callable[..., object]) -> _F:
    """Expose external parameters without claiming the body's return type.

    Keep forward and local annotations unevaluated. The original return and
    scope annotations remain available on the body through ``__wrapped__``;
    the decorator's generic signature supplies the precise static return type.
    """
    body_signature = signature(body)
    parameters = tuple(body_signature.parameters.values())[1:]
    annotations = {
        parameter.name: parameter.annotation for parameter in parameters if parameter.annotation is not Signature.empty
    }
    setattr(wrapper, "__annotations__", annotations)
    setattr(wrapper, "__signature__", body_signature.replace(parameters=parameters, return_annotation=Signature.empty))
    return wrapper


class OptionInvocation(Invocation):
    def __init__(self) -> None:
        super().__init__()
        self.failed = False


class ResultInvocation(Invocation, Generic[_E]):
    def __init__(self) -> None:
        super().__init__()
        self.failure: Error[_E] | None = None
