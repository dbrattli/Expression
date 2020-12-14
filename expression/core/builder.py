from abc import ABC
from functools import wraps
from typing import Any, Callable, Coroutine, Generic, List, Optional, TypeVar, cast

from .error import EffectError

TInner = TypeVar("TInner")
TOuter = TypeVar("TOuter")
TResult = TypeVar("TResult")


class Builder(Generic[TOuter, TInner], ABC):
    """Effect builder."""

    def bind(self, xs: TOuter, fn: Callable[[TInner], TOuter]) -> TOuter:
        raise NotImplementedError("Builder does not implement a bind method")

    def return_(self, x: TInner) -> TOuter:
        raise NotImplementedError("Builder does not implement a return method")

    def return_from(self, xs: TOuter) -> TOuter:
        raise NotImplementedError("Builder does not implement a return from method")

    def combine(self, xs: TOuter, ys: TOuter) -> TOuter:
        """Used for combining multiple statements in the effect."""
        raise NotImplementedError("Builder does not implement a combine method")

    def zero(self) -> TOuter:
        """Called if the effect raises StopIteration without a value,
        i.e returns None"""
        raise NotImplementedError("Builder does not implement a zero method")

    def _send(
        self,
        gen: Coroutine[TInner, Optional[TInner], Optional[TOuter]],
        done: List[bool],
        value: Optional[TInner] = None,
    ) -> TOuter:
        try:
            yielded = gen.send(value)
            return self.return_(yielded)
        except EffectError as error:
            # Effect errors (Nothing, Error, etc) short circuits the
            # processing so we set `done` to `True` here.
            done.append(True)
            return self.return_from(cast("TOuter", error))
        except StopIteration as ex:
            done.append(True)
            if ex.value is not None:
                return self.return_(ex.value)
            raise

    def __call__(
        self,  # Ignored self parameter
        fn: Callable[..., Any],
    ) -> Callable[..., TOuter]:
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
        def wrapper(*args: Any, **kw: Any) -> TOuter:
            gen = fn(*args, **kw)
            done: List[bool] = []

            result: Optional[TOuter] = None
            try:
                result = self._send(gen, done)
                while not done:
                    binder: Callable[[Any], TOuter] = lambda value: self._send(gen, done, value)
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
