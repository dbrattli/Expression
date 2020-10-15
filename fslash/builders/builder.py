from typing import Generic, Generator, Optional, TypeVar, Callable, List, Iterable, Coroutine, cast, Union
from fslash.core.misc import ComputationalExpressionError

TInner = TypeVar("TInner")
TOuter = TypeVar("TOuter")


class Builder(Generic[TOuter, TInner]):
    def bind(self, xs, fn):
        raise NotImplementedError

    def return_(self, x):
        raise NotImplementedError

    def return_from(self, xs):
        raise NotImplementedError

    def combine(self, xs, ys):
        raise NotImplementedError

    def zero(self):
        raise NotImplementedError

    def _send(self, gen, done: List[bool], value: Optional[TInner] = None) -> TOuter:
        try:
            yielded = gen.send(value)
            return self.return_(yielded)
        except ComputationalExpressionError as error:
            done.append(True)
            return self.return_from(error)
        except StopIteration as ex:
            done.append(True)

            if ex.value is not None:
                return self.return_(ex.value)
            elif value is not None:
                return self.return_(value)
            return self.zero()
        except Exception:
            done.append(True)
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
            gen = iter(cast(Iterable[TInner], fn(*args, **kw)))

            done: List[bool] = []
            result: TOuter = self._send(gen, done)

            while not done and not isinstance(result, ComputationalExpressionError):
                result = self.combine(result, self.bind(result, lambda value: self._send(gen, done, value)))

            return result

        return wrapper
