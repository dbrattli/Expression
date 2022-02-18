from abc import ABC
from functools import wraps
from typing import Any, Callable, Coroutine, Generic, List, Optional, TypeVar, cast

from .error import EffectError

_TInner = TypeVar("_TInner")
_TOuter = TypeVar("_TOuter")
_TResult = TypeVar("_TResult")


class Builder(Generic[_TOuter, _TInner], ABC):
    """Effect builder."""

    def bind(self, xs: _TOuter, fn: Callable[[_TInner], _TOuter]) -> _TOuter:
        raise NotImplementedError("Builder does not implement a bind method")

    def return_(self, x: _TInner) -> _TOuter:
        raise NotImplementedError("Builder does not implement a return method")

    def return_from(self, xs: _TOuter) -> _TOuter:
        raise NotImplementedError("Builder does not implement a return from method")

    def combine(self, xs: _TOuter, ys: _TOuter) -> _TOuter:
        """Used for combining multiple statements in the effect."""
        raise NotImplementedError("Builder does not implement a combine method")

    def zero(self) -> _TOuter:
        """Called if the effect raises StopIteration without a value,
        i.e returns None"""
        raise NotImplementedError("Builder does not implement a zero method")

    def _send(
        self,
        gen: Coroutine[_TInner, Optional[_TInner], Optional[_TOuter]],
        done: List[bool],
        value: Optional[_TInner] = None,
    ) -> _TOuter:
        try:
            yielded = gen.send(value)
            return self.return_(yielded)
        except EffectError as error:
            # Effect errors (Nothing, Error, etc) short circuits the
            # processing so we set `done` to `True` here.
            done.append(True)
            return self.return_from(cast("_TOuter", error))
        except StopIteration as ex:
            done.append(True)
            if ex.value is not None:
                return self.return_(ex.value)
            raise

    def __call__(
        self,  # Ignored self parameter
        fn: Callable[..., Any],
    ) -> Callable[..., _TOuter]:
        """Option builder.

        Enables the use of computational expressions using coroutines.
        Thus inside the coroutine the keywords `yield` and `yield from`
        reassembles `yield` and `yield!` from F#.

        Args:
            fn: A function that contains a computational expression and
                returns either a coroutine, generator or an option.

        Returns:
            A `builder` function that can wrap coroutines into builders.
        """

        @wraps(fn)
        def wrapper(*args: Any, **kw: Any) -> _TOuter:
            gen = fn(*args, **kw)
            done: List[bool] = []

            result: Optional[_TOuter] = None
            try:
                result = self._send(gen, done)
                while not done:
                    binder: Callable[[Any], _TOuter] = lambda value: self._send(
                        gen, done, value
                    )
                    cont = self.bind(result, binder)
                    result = self.combine(result, cont)
            except StopIteration:
                pass

            # If anything returns `None` (i.e raises StopIteration
            # without a value) then we expect the effect to have a zero
            # method implemented.
            if result is None:
                result = self.zero()

            return result

        return wrapper


__all__ = ["Builder"]
