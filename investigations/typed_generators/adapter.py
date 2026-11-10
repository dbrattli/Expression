"""Experimental synchronous generator adapters; not a public Expression API."""

from collections.abc import Callable, Generator
from functools import wraps
from typing import Never, ParamSpec, TypeVar, cast, overload

from typing_extensions import TypeAliasType

from expression import NOTHING, Error, Nothing, Ok, Option, Result, Some


_T = TypeVar("_T")
_E = TypeVar("_E")
_P = ParamSpec("_P")

# Explicit parameter order: the yielded error channel mentions E before T.
ResultComputation = TypeAliasType("ResultComputation", Generator[Result[object, _E], None, _T], type_params=(_T, _E))
OptionComputation = TypeAliasType("OptionComputation", Generator[Option[object], None, _T], type_params=(_T,))


@overload
def bind(value: Ok[_T]) -> Generator[Ok[object], None, _T]: ...


@overload
def bind(value: Error[_E]) -> Generator[Error[_E], None, Never]: ...


@overload
def bind(value: Result[_T, _E]) -> ResultComputation[_T, _E]: ...


@overload
def bind(value: Some[_T]) -> Generator[Some[object], None, _T]: ...


@overload
def bind(value: Nothing) -> Generator[Nothing, None, Never]: ...


@overload
def bind(value: Option[_T]) -> OptionComputation[_T]: ...


def bind(value: Result[_T, _E] | Option[_T]) -> Generator[Result[object, _E] | Option[object], None, _T]:
    yield value
    match value:
        case Ok(payload) | Some(payload):
            return payload
        case _:
            raise RuntimeError("A failed bind must not be resumed")


def result(body: Callable[_P, ResultComputation[_T, _E]]) -> Callable[_P, Result[_T, _E]]:
    @wraps(body)
    def run(*args: _P.args, **kwargs: _P.kwargs) -> Result[_T, _E]:
        computation = body(*args, **kwargs)
        try:
            while True:
                try:
                    effect = next(computation)
                except StopIteration as done:
                    return Ok(cast(_T, done.value))
                match effect:
                    case Ok():
                        pass
                    case Error():
                        return effect
                    case _:
                        raise TypeError("Expected a yielded Ok or Error")
        finally:
            computation.close()

    return run


def option(body: Callable[_P, OptionComputation[_T]]) -> Callable[_P, Option[_T]]:
    @wraps(body)
    def run(*args: _P.args, **kwargs: _P.kwargs) -> Option[_T]:
        computation = body(*args, **kwargs)
        try:
            while True:
                try:
                    effect = next(computation)
                except StopIteration as done:
                    return Some(cast(_T, done.value))
                match effect:
                    case Some():
                        pass
                    case Nothing():
                        return NOTHING
                    case _:
                        raise TypeError("Expected a yielded Some or Nothing")
        finally:
            computation.close()

    return run
