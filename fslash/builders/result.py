from typing import TypeVar, Callable, Coroutine, Generator, Iterable, Optional, Union, List, cast

from fslash.core.result import Result, Ok, Error, ResultException

TSource = TypeVar("TSource")
TResult = TypeVar("TResult")
TError = TypeVar("TError")


def send(gen, done: List[bool], value: Optional[TSource] = None) -> Result[TSource, TError]:
    try:
        print("Sending: ", value)
        yielded = gen.send(value)
        print("Yielded: ", yielded)
        return Ok(yielded)
    except GeneratorExit:
        print("Generator exit")
        done.append(True)
        return Error(cast(TError, None))
    except StopIteration as ex:
        print("StopIteration of: ", ex.value)
        done.append(True)
        if ex.value is not None:
            return Ok(ex.value)

        return Ok(cast(TSource, value))
    except ResultException as ex:
        print("Got result exception: ", [ex])
        done.append(True)
        return Error(ex.error)


def result(
    fn: Callable[
        ...,
        Union[
            Coroutine[TSource, Optional[TSource], Optional[Result[TSource, TError]]],
            Generator[TSource, Optional[TSource], Optional[Result[TSource, TError]]],
            Result[TSource, TError],
        ],
    ]
) -> Callable[..., Result[TSource, TError]]:
    """Result builder.

    Enables the use of options as computational expressions using
    coroutines. Thus inside the coroutine the keywords `yield` and
    `yield from` reasembles `yield` and `yield!` from F#.

    Args:
        fn: A function that contains a computational expression and
        returns either a coroutine, generator or a result.

    Returns:
        A Result object.
    """

    def wrapper(*args, **kw) -> Result[TSource, TError]:
        done: List[bool] = []
        gen = iter(cast(Iterable[TSource], fn(*args, **kw)))
        result: Result[TSource, TError] = send(gen, done)

        while not isinstance(result, Error) and not done:
            result = result.bind(lambda value: send(gen, done, value))
            # print("Result: ", result)

        return result
    return wrapper


__all__ = ["result"]
