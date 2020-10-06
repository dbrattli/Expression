from typing import TypeVar, Callable, Iterable, Generator, Union, Coroutine, Optional, cast
from fslash.collections.seq import Seq

TSource = TypeVar("TSource")
TResult = TypeVar("TResult")
TState = TypeVar("TState")


def seq(
    fn: Callable[  # Function
        ...,
        Union[
            Coroutine[TSource, Optional[TSource], Optional[Iterable[TSource]]],
            # Generator that yields or returns an option
            Generator[TSource, Optional[TSource], Optional[Iterable[TSource]]],
            # or simply just an Iterable
            Iterable[TSource]
        ]
    ]
) -> Callable[..., Seq[TSource]]:
    """Sequence builder.

    Enables the use of sequences as computational expressions using
    generators and coroutines Note that this is exactly the same as just
    using generators. But we define it for completeness.
    """

    def wrapper(*args, **kw) -> Seq[TSource]:
        return Seq(cast(Callable, fn)(*args, **kw))
    return wrapper


__all__ = ["seq"]
