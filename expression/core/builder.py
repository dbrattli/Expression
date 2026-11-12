import inspect
from abc import ABC
from collections.abc import Callable, Generator
from dataclasses import dataclass
from functools import wraps
from typing import Any, cast

from .error import EffectError


class BuilderState[T]:
    """Legacy computation state, retained for import compatibility."""

    def __init__(self) -> None:
        self.is_done = False


@dataclass(frozen=True)
class _Produced[M]:
    value: M
    is_terminal: bool = False


@dataclass(frozen=True)
class _Completed:
    pass


class Builder[T, M](ABC):
    """Eager generator effect builder.

    Each bind must invoke its continuation exactly once, synchronously.
    Deferred and branching effects require a different execution model.
    The builder owns the generator and closes it when execution exits.
    """

    # Required methods
    def bind(self, xs: M, fn: Callable[[T], M]) -> M:
        raise NotImplementedError("Builder does not implement a `bind` method")

    def return_(self, x: T) -> M:
        raise NotImplementedError("Builder does not implement a `return` method")

    def return_from(self, xs: M) -> M:
        raise NotImplementedError("Builder does not implement a `return` from method")

    def combine(self, xs: M, ys: M) -> M:
        """Used for combining multiple statements in the effect."""
        raise NotImplementedError("Builder does not implement a `combine` method")

    def zero(self) -> M:
        """Zero effect.

        Called if the effect raises StopIteration without a value, i.e
        returns None.
        """
        raise NotImplementedError("Builder does not implement a `zero` method")

    # Optional methods for control flow
    def delay(self, fn: Callable[[], M]) -> M:
        """Delay the computation.

        Default implementation is to return the result of the function.
        """
        return fn()

    def run(self, computation: M) -> M:
        """Run a computation.

        Default implementation is to return the computation as is.
        """
        return computation

    # Internal implementation
    def _send(self, gen: Generator[Any, Any, Any], value: Any) -> _Produced[M] | _Completed:
        # Only generator advancement may signal completion or effect failure.
        # Exceptions from builder hooks must propagate unchanged.
        try:
            yielded = gen.send(value)
        except EffectError as error:
            return _Produced(self.return_from(cast("M", error.args[0])), is_terminal=True)
        except StopIteration as ex:
            if ex.value is None:
                return _Completed()
            return _Produced(self.return_(ex.value), is_terminal=True)
        return _Produced(self.return_(yielded))

    def _advance(self, gen: Generator[Any, Any, Any], current: M) -> tuple[M, _Produced[M] | _Completed]:
        """Perform one bind while enforcing ownership of its continuation."""
        active = True
        called = False
        step: _Produced[M] | _Completed = _Completed()

        def binder(sent: Any) -> M:
            nonlocal called, step
            if not active or called:
                raise RuntimeError("Builder requires a synchronous, single-use bind continuation")
            called = True
            step = self._send(gen, sent)
            if isinstance(step, _Completed):
                return current
            produced = step.value
            return self.delay(lambda: produced)

        try:
            bound = self.bind(current, binder)
        finally:
            active = False
        if not called:
            raise RuntimeError("Builder.bind must invoke its continuation exactly once synchronously")
        return bound, step

    def _evaluate_generator(self, gen: Generator[Any, Any, Any]) -> M:
        """Accumulate eager steps without growing the Python call stack."""
        initial = self._send(gen, None)
        if isinstance(initial, _Completed):
            return self.zero()

        result = value = self.delay(lambda: initial.value)
        terminal = initial.is_terminal
        while not terminal:
            value, step = self._advance(gen, value)
            if isinstance(step, _Completed):
                break
            result = self.combine(result, value)
            terminal = step.is_terminal
        return result

    def _run_generator(self, gen: Generator[Any, Any, Any]) -> M:
        """Own generator cleanup through evaluation and the final run hook."""
        try:
            return self.run(self._evaluate_generator(gen))
        finally:
            gen.close()

    def __call__[**P](
        self,
        fn: Callable[
            P,
            Generator[T | None, T, T | None] | Generator[T | None, None, T | None] | T | None,
        ],
    ) -> Callable[P, M]:
        """The builder decorator.

        A body without a `yield` statement is a plain function. Its return
        value is treated like a `return` statement (F# `return`): a value is
        lifted with `return_`, and a `None` return value maps to `zero()`.
        """

        @wraps(fn)
        def wrapper(*args: P.args, **kw: P.kwargs) -> M:
            body = fn(*args, **kw)

            if not inspect.isgenerator(body):
                # A body without a `yield` statement is a plain function.
                # Treat its return value like a `return` statement: a value
                # maps to return_(value), a None return value maps to zero().
                result_value = cast("T | None", body)
                if result_value is None:
                    return self.run(self.zero())
                return self.run(self.return_(result_value))

            return self._run_generator(cast("Generator[Any, Any, Any]", body))

        return wrapper
