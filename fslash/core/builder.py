from typing import Generic, Generator, Optional, TypeVar, Callable, Coroutine, Union, List
from fslash.core.misc import ComputationalExpressionExit

TInner = TypeVar("TInner")
TOuter = TypeVar("TOuter")


class Builder(Generic[TOuter, TInner]):
    def bind(self, xs, fn):
        raise NotImplementedError("Builder does not implement a bind method")

    def return_(self, x):
        raise NotImplementedError("Builder does not implement a return method")

    def return_from(self, xs):
        raise NotImplementedError("Builder does not implement a return from method")

    def combine(self, xs, ys):
        raise NotImplementedError("Builder does not implement a combine method")

    def zero(self):
        raise NotImplementedError("Builder does not implement a zero method")

    def _send(self, gen, done, value: Optional[TInner] = None) -> TOuter:
        try:
            yielded = gen.send(value)
            return self.return_(yielded)
        except ComputationalExpressionExit as error:
            done.append(True)
            return self.return_from(error)
        except StopIteration as ex:
            done.append(True)
            if ex.value is not None:
                return self.return_(ex.value)

            raise ComputationalExpressionExit()
        except Exception:
            raise

    def __call__(
        self,  # Ignored self parameter
        fn: Callable[  # Function
            ...,  # ... that takes anything
            Union[  # ... and returns
                # Coroutine that yields or returns TOuter
                Coroutine[TInner, Optional[TInner], Optional[TOuter]],
                # Generator that yields or returns TOuter
                Generator[TInner, Optional[TInner], Optional[TOuter]],
                # or simply just an Option
                TOuter,
                None
            ],
        ],
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

        def wrapper(*args, **kw) -> TOuter:
            gen = fn(*args, **kw)
            done: List[bool] = []

            result: Optional[TOuter] = None
            try:
                result = self._send(gen, done)
                while not done and not isinstance(result, ComputationalExpressionExit):
                    cont = self.bind(result, lambda value: self._send(gen, done, value))
                    result = self.combine(result, cont)
            except ComputationalExpressionExit:
                pass

            if result is None:
                result = self.zero()

            return result
        return wrapper
