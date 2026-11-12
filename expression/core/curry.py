import functools
from collections.abc import Callable
from typing import Any, Concatenate, Literal, overload


_Arity = Literal[0, 1, 2, 3, 4]


def _curry(args: tuple[Any, ...], arity: int, fun: Callable[..., Any]) -> Callable[..., Any]:
    def wrapper(*args_: Any, **kw: Any) -> Any:
        if arity == 1:
            return fun(*args, *args_, **kw)
        return _curry(args + args_, arity - 1, fun)

    return wrapper


@overload
def curry[**P, B](num_args: Literal[0]) -> Callable[[Callable[P, B]], Callable[P, B]]: ...


@overload
def curry[B, A, **P](
    num_args: Literal[1],
) -> Callable[[Callable[Concatenate[A, P], B]], Callable[[A], Callable[P, B]]]: ...


@overload
def curry[C, A, B, **P](
    num_args: Literal[2],
) -> Callable[
    [Callable[Concatenate[A, B, P], C]],
    Callable[
        [A],
        Callable[
            [B],
            Callable[P, C],
        ],
    ],
]: ...


@overload
def curry[D, A, B, C, **P](
    num_args: Literal[3],
) -> Callable[
    [Callable[Concatenate[A, B, C, P], D]],
    Callable[
        [A],
        Callable[
            [B],
            Callable[
                [C],
                Callable[P, D],
            ],
        ],
    ],
]: ...


@overload
def curry[E, A, B, C, D, **P](
    num_args: Literal[4],
) -> Callable[
    [Callable[Concatenate[A, B, C, D, P], E]],
    Callable[
        [A],
        Callable[
            [B],
            Callable[
                [C],
                Callable[[D], Callable[P, E]],
            ],
        ],
    ],
]: ...


def curry(num_args: _Arity) -> Callable[..., Any]:
    """A curry decorator.

    Makes a function curried.

    Args:
        num_args: The number of args to curry from the start of the
        function

    Example:
        >>> @curry(1)
        ... def add(a: int, b: int) -> int:
        ...    return a + b
        >>>
        >>> assert add(3)(4) == 7
    """

    def wrapper(fun: Callable[..., Any]) -> Callable[..., Any]:
        return functools.wraps(fun)(_curry((), num_args + 1, fun))

    return wrapper


@overload
def curry_flip[**P, A](
    num_args: Literal[0],
) -> Callable[[Callable[P, A]], Callable[P, A]]: ...


@overload
def curry_flip[**P, B, A](
    num_args: Literal[1],
) -> Callable[[Callable[Concatenate[A, P], B]], Callable[P, Callable[[A], B]]]: ...


@overload
def curry_flip[**P, C, A, B](
    num_args: Literal[2],
) -> Callable[
    [Callable[Concatenate[A, B, P], C]],
    Callable[
        P,
        Callable[
            [A],
            Callable[[B], C],
        ],
    ],
]: ...


@overload
def curry_flip[**P, D, A, B, C](
    num_args: Literal[3],
) -> Callable[
    [Callable[Concatenate[A, B, C, P], D]],
    Callable[
        P,
        Callable[
            [A],
            Callable[
                [B],
                Callable[[C], D],
            ],
        ],
    ],
]: ...


@overload
def curry_flip[**P, E, A, B, C, D](
    num_args: Literal[4],
) -> Callable[
    [Callable[Concatenate[A, B, C, D, P], E]],
    Callable[
        P,
        Callable[
            [A],
            Callable[
                [B],
                Callable[[C], Callable[[D], E]],
            ],
        ],
    ],
]: ...


def curry_flip(
    num_args: _Arity,
) -> Callable[..., Any]:
    """A flipped curry decorator.

    Makes a function curried, but flips the curried arguments to become
    the last arguments. This is very nice when having e.g optional
    arguments after a source argument that will be piped.

    Args:
        num_args: The number of args to curry from the start of the
        function

    Example:
        >>> @curry_flip(1)
        ... def map(source: List[int], mapper: Callable[[int], int]):
        ...    return [mapper(x) for x in source]
        >>>
        >>> ys = pipe(xs, map(lambda x: x * 10))
    """

    def _wrap_fun(fun: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(fun)
        def _wrap_args(*args: Any, **kwargs: Any) -> Callable[..., Any]:
            def _wrap_curried(*curry_args: Any) -> Any:
                return fun(*curry_args, *args, **kwargs)

            return _curry((), num_args, _wrap_curried)

        return _wrap_args if num_args else fun

    return _wrap_fun


def pipeable[B, A, **P](
    function: Callable[Concatenate[A, P], B],
    /,
    *args: P.args,
    **kwargs: P.kwargs,
) -> Callable[[A], B]:
    """Partially apply a function's arguments after its pipeline value.

    Args:
        function: Function whose first argument is supplied by a pipeline.
        *args: Positional arguments after the pipeline value.
        **kwargs: Keyword arguments after the pipeline value.

    Returns:
        A single-argument function suitable for ``pipe``.
    """
    return curry_flip(1)(function)(*args, **kwargs)


__all__ = ["curry", "curry_flip", "pipeable"]
