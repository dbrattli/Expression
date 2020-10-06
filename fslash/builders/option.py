from typing import Generator, Optional, TypeVar, Callable, List, Iterable, Coroutine, cast, Union

from fslash.core.option import Option, Nothing, Some
TSource = TypeVar("TSource")
TResult = TypeVar("TResult")


def send(gen, done: List[bool], value: Optional[TSource] = None) -> Option[TSource]:
    try:
        yielded = gen.send(value)
        return Some(yielded) if yielded else Nothing
    except GeneratorExit:
        done.append(True)
        return Nothing
    except StopIteration as ex:
        done.append(True)
        if ex.value is not None:
            return Some(ex.value)
        elif value is not None:
            return Some(value)
        return Nothing
    except Exception:
        done.append(True)
        return Nothing


def option(
    fn: Callable[  # Function
        ...,       # ... that takes anything
        Union[     # ... and returns
            # Coroutine that yields or returns an option
            Coroutine[TSource, Optional[TSource], Optional[Option[TSource]]],
            # Generator that yields or returns an option
            Generator[TSource, Optional[TSource], Optional[Option[TSource]]],
            # or simply just an Option
            Option[TSource]
        ]
    ]
) -> Callable[..., Option[TSource]]:
    """Option builder.

    Enables the use of options as computational expressions using
    coroutines. Thus inside the coroutine the keywords `yield` and
    `yield from` reasembles `yield` and `yield!` from F#.

    Args:
        fn: A function that contains a computational expression and
        returns either a coroutine, generator or an option.

    Returns:
        An `Option` object.
    """

    # This is a mess, but we basically just want to convert plain functions with a return statement into coroutines.
    gen = iter(cast(Iterable[TSource], fn()))

    def wrapper(*args, **kw) -> Option[TSource]:
        done: List[bool] = []
        result: Option[TSource] = send(gen, done)

        while result != Nothing and not done:
            result = result.bind(lambda value: send(gen, done, value))

        return result
    return wrapper


__all__ = ["option"]