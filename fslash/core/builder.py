from typing import Generic, Optional, TypeVar, Callable, Coroutine, List, Any, cast
from fslash.core import EffectError

TInner = TypeVar("TInner")
TOuter = TypeVar("TOuter")
TOuter2 = TypeVar("TOuter2")
TResult = TypeVar("TResult")


class Builder(Generic[TOuter, TInner]):
    def bind(self, xs: TOuter, fn: Callable[[TInner], TOuter2]) -> TOuter2:
        raise NotImplementedError("Builder does not implement a bind method")

    def return_(self, x):
        raise NotImplementedError("Builder does not implement a return method")

    def return_from(self, xs):
        raise NotImplementedError("Builder does not implement a return from method")

    def combine(self, xs, ys):
        raise NotImplementedError("Builder does not implement a combine method")

    def zero(self):
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
            done.append(True)
            return self.return_from(error)
        except StopIteration as ex:
            done.append(True)
            if ex.value is not None:
                return self.return_(ex.value)

            raise EffectError()
        except Exception:
            raise

    def __call__(
        self,  # Ignored self parameter
        fn: Callable[..., Any],
    ) -> Callable[..., TOuter]:
        """Option builder.

        Enables the use of computational expressions using coroutines.
        Thus inside the coroutine the keywords `yield` and `yield from`
        reasembles `yield` and `yield!` from F#.

        Args:
            fn: A function that contains a computational expression and
                returns either a coroutine, generator or an option.

        Returns:
            A `builder` function that can wrap coroutines into builders.
        """

        def wrapper(*args: Any, **kw: Any) -> TOuter:
            gen = fn(*args, **kw)
            done: List[bool] = []

            result: Optional[TOuter] = None
            try:
                result = self._send(gen, done)
                while not done and not isinstance(result, EffectError):
                    cont = self.bind(cast(TOuter, result), lambda value: self._send(gen, done, value))
                    result = self.combine(result, cont)
            except EffectError:
                pass

            if result is None:
                result = self.zero()

            return result

        return wrapper
