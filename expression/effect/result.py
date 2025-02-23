from collections.abc import Callable, Generator
from typing import Any, TypeVar

from typing_extensions import ParamSpec

from expression.core import Builder, Ok, Result, pipe, result


_TSource = TypeVar("_TSource")
_TResult = TypeVar("_TResult")
_TError = TypeVar("_TError")
_P = ParamSpec("_P")


class ResultBuilder(Builder[_TSource, Result[Any, _TError]]):
    def bind(
        self,
        xs: Result[_TSource, _TError],
        fn: Callable[[Any], Result[_TResult, _TError]],
    ) -> Result[_TResult, _TError]:
        """Bind a function to a result value.

        In F# computation expressions, this corresponds to ``let!`` and enables
        sequencing of computations.

        Args:
            xs: The result value to bind
            fn: The function to apply to the value if Ok

        Returns:
            The result of applying fn to the value if Ok, otherwise Error
        """
        return pipe(xs, result.bind(fn))

    def return_(self, x: _TSource) -> Result[_TSource, _TError]:  # Use Any for return_ type
        """Wrap a value in a result.

        In F# computation expressions, this corresponds to ``return`` and lifts
        a value into the result context.

        Args:
            x: The value to wrap

        Returns:
            Ok containing the value
        """
        return Ok(x)

    def return_from(self, xs: Result[_TSource, _TError]) -> Result[_TSource, _TError]:
        """Return a result value directly.

        In F# computation expressions, this corresponds to ``return!`` and allows
        returning an already wrapped value.

        Args:
            xs: The result value to return

        Returns:
            The result value unchanged
        """
        return xs

    def combine(self, xs: Result[_TSource, _TError], ys: Result[_TSource, _TError]) -> Result[_TSource, _TError]:
        """Combine two result computations.

        In F# computation expressions, this enables sequencing multiple
        expressions where we only care about the final result.

        Args:
            xs: First result computation
            ys: Second result computation

        Returns:
            The second computation if first is Ok, otherwise Error
        """
        return xs.bind(lambda _: ys)

    def zero(self) -> Result[Any, _TError]:  # Use Any for zero return type
        """Return the zero value for results.

        In F# computation expressions, this is used when no value is returned,
        corresponding to Ok(()) in F#.

        Returns:
            Ok(None)
        """
        return Ok(None)

    def __call__(
        self,  # Ignored self parameter
        fn: Callable[
            _P,
            Generator[_TSource | None, _TSource, _TSource | None] | Generator[_TSource | None, None, _TSource | None],
        ],
    ) -> Callable[_P, Result[_TSource, _TError]]:
        return super().__call__(fn)


class TryBuilder(ResultBuilder[_TSource, Exception]): ...


__all__ = ["ResultBuilder", "TryBuilder"]
