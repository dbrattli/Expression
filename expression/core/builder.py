from abc import ABC
from collections.abc import Callable, Generator
from functools import wraps
from typing import Any, Generic, TypeVar, cast

from typing_extensions import ParamSpec

from .error import EffectError


_T = TypeVar("_T")  # for value type
_M = TypeVar("_M")  # for monadic type
_P = ParamSpec("_P")


class BuilderState(Generic[_T]):
    """Encapsulates the state of a builder computation."""

    def __init__(self):
        self.is_done = False


class Builder(Generic[_T, _M], ABC):  # Corrected Generic definition
    """Effect builder."""

    # Required methods
    def bind(self, xs: _M, fn: Callable[[_T], _M]) -> _M:  # Use concrete types for Callable input and output
        raise NotImplementedError("Builder does not implement a `bind` method")

    def return_(self, x: _T) -> _M:
        raise NotImplementedError("Builder does not implement a `return` method")

    def return_from(self, xs: _M) -> _M:
        raise NotImplementedError("Builder does not implement a `return` from method")

    def combine(self, xs: _M, ys: _M) -> _M:
        """Used for combining multiple statements in the effect."""
        raise NotImplementedError("Builder does not implement a `combine` method")

    def zero(self) -> _M:
        """Zero effect.

        Called if the effect raises StopIteration without a value, i.e
        returns None.
        """
        raise NotImplementedError("Builder does not implement a `zero` method")

    # Optional methods for control flow
    def delay(self, fn: Callable[[], _M]) -> _M:
        """Delay the computation.

        Default implementation is to return the result of the function.
        """
        return fn()

    def run(self, computation: _M) -> _M:
        """Run a computation.

        Default implementation is to return the computation as is.
        """
        return computation

    # Internal implementation
    def _send(
        self,
        gen: Generator[Any, Any, Any],
        state: BuilderState[_T],  # Use BuilderState
        value: _T,
    ) -> _M:
        try:
            yielded = gen.send(value)
            return self.return_(yielded)
        except EffectError as error:
            # Effect errors (Nothing, Error, etc) short circuits
            state.is_done = True
            return self.return_from(cast("_M", error.args[0]))
        except StopIteration as ex:
            state.is_done = True

            # Return of a value in the generator produces StopIteration with a value
            if ex.value is not None:
                return self.return_(ex.value)

            raise  # Raise StopIteration with no value

        except RuntimeError:
            state.is_done = True
            return self.zero()  # Return zero() to handle generator runtime errors instead of raising StopIteration

    def __call__(
        self,
        fn: Callable[
            _P,
            Generator[_T | None, _T, _T | None] | Generator[_T | None, None, _T | None],
        ],
    ) -> Callable[_P, _M]:
        """The builder decorator."""

        @wraps(fn)
        def wrapper(*args: _P.args, **kw: _P.kwargs) -> _M:
            gen = fn(*args, **kw)
            state = BuilderState[_T]()  # Initialize BuilderState
            result: _M = self.zero()  # Initialize result
            value: _M

            def binder(value: Any) -> _M:
                ret = self._send(gen, state, value)  # Pass state to _send
                return self.delay(lambda: ret)  # Delay every bind call

            try:
                # Initialize co-routine with None to start the generator and get the
                # first value
                result = value = binder(None)

                while not state.is_done:  # Loop until coroutine is exhausted
                    value: _M = self.bind(value, binder)  # Send value to coroutine
                    result = self.combine(result, value)  # Combine previous result with new value

            except StopIteration:
                # This will happens if the generator exits by returning None
                pass

            return self.run(result)  # Run the result

        return wrapper
