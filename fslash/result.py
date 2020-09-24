from abc import abstractmethod
from typing import TypeVar, Generic, Callable, Coroutine, Generator, Iterator, Iterable, Optional, Union, List, cast

TSource = TypeVar("TSource")
TResult = TypeVar("TResult")
TError = TypeVar("TError")


class ResultModule(Generic[TSource, TError]):
    @staticmethod
    def map(mapper: Callable[[TSource], TResult]) -> "Callable[[Result[TSource, TError]], Result[TResult, TError]]":
        def _map(result: Result[TSource, TError]) -> "Result[TResult, TError]":
            return result.map(mapper)

        return _map

    @staticmethod
    def bind(
        mapper: Callable[[TSource], "Result[TResult, TError]"]
    ) -> "Callable[[Result[TSource, TError]], Result[TResult, TError]]":
        def _bind(result: Result[TSource, TError]) -> Result[TResult, TError]:
            return result.bind(mapper)

        return _bind


class Result(Generic[TSource, TError], Iterable[Union[TSource, TError]]):
    @abstractmethod
    def __iter__(self) -> Iterator[TSource]:
        raise NotImplementedError

    @abstractmethod
    def map(self, mapper: Callable[[TSource], TResult]) -> "Result[TResult, TError]":
        raise NotImplementedError

    @abstractmethod
    def bind(self, mapper: Callable[[TSource], "Result[TResult, TError]"]) -> "Result[TResult, TError]":
        raise NotImplementedError

    def __repr__(self):
        return str(self)


class Ok(Result[TSource, TError]):
    def __init__(self, value: TSource) -> None:
        self._value = value

    @property
    def value(self):
        return self._value

    def map(self, mapper: Callable[[TSource], TResult]) -> Result[TResult, TError]:
        return Ok(mapper(self._value))

    def bind(self, mapper: Callable[[TSource], Result[TResult, TError]]) -> Result[TResult, TError]:
        return mapper(self._value)

    def map_error(self, mapper: Callable[[TError], TResult]) -> Result[TSource, TResult]:
        return Ok(self._value)

    def __iter__(self) -> Iterator[TSource]:
        """Return iterator for Ok case."""
        return (yield self._value)

    def __str__(self):
        return f"Ok {self._value}"


class Error(Result[TSource, TError]):
    def __init__(self, error: TError) -> None:
        self._error = error

    @property
    def error(self) -> TError:
        return self._error

    def map(self, mapper: Callable[[TSource], TResult]) -> Result[TResult, TError]:
        return Error(self._error)

    def bind(self, mapper: Callable[[TSource], Result[TResult, TError]]) -> Result[TResult, TError]:
        return Error(self._error)

    def map_error(self, mapper: Callable[[TError], TResult]) -> Result[TSource, TResult]:
        return Error(mapper(self._error))

    def __iter__(self) -> Iterator[TSource]:
        """Return iterator for Error case."""
        print("Error:iter")
        raise ResultException(self._error)
        yield

    def __str__(self):
        return f"Error {self._error}"


class ResultException(Exception):
    def __init__(self, error):
        self.error = error


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

    # This is a mess, but we basically just want to convert plain functions with a return statement into coroutines.
    gen = iter(cast(Iterable[TSource], fn()))

    def wrapper(*args, **kw) -> Result[TSource, TError]:
        done: List[bool] = []
        result: Result[TSource, TError] = send(gen, done)

        while not isinstance(result, Error) and not done:
            result = result.bind(lambda value: send(gen, done, value))
            print("Result: ", result)

        return result
    return wrapper


__all__ = ["ResultModule", "Result", "Ok", "Error", "result"]
