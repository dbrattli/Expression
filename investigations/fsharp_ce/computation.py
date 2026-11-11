"""Experimental CE values separate from ordinary Option/Result iteration."""

from collections.abc import Callable, Generator
from dataclasses import dataclass
from functools import wraps
from typing import Generic, Never, ParamSpec, TypeVar, cast, overload

from typing_extensions import TypeAliasType

from expression import NOTHING, Error, Nothing, Ok, Option, Result, Some


_T = TypeVar("_T")
_E = TypeVar("_E")
_T_co = TypeVar("_T_co", covariant=True)
_E_co = TypeVar("_E_co", covariant=True)
_P = ParamSpec("_P")


@dataclass(frozen=True)
class ResultStep(Generic[_E_co]):
    value: Result[object, _E_co]


@dataclass(frozen=True)
class OptionStep:
    value: Option[object]


ResultBody = TypeAliasType("ResultBody", Generator[ResultStep[_E], None, _T], type_params=(_T, _E))
OptionBody = TypeAliasType("OptionBody", Generator[OptionStep, None, _T], type_params=(_T,))


class ResultComputation(Generic[_T_co, _E_co]):
    """Reusable delayed computation; iteration binds, run realizes its result."""

    def __init__(self, run: Callable[[], Result[_T_co, _E_co]]) -> None:
        self._run = run

    def run(self) -> Result[_T_co, _E_co]:
        return self._run()

    def __iter__(self) -> Generator[ResultStep[_E_co], None, _T_co]:
        value = self.run()
        yield ResultStep(value)
        if isinstance(value, Ok):
            return value.ok
        raise RuntimeError("A failed computation must not be resumed")


class OptionComputation(Generic[_T_co]):
    def __init__(self, run: Callable[[], Option[_T_co]]) -> None:
        self._run = run

    def run(self) -> Option[_T_co]:
        return self._run()

    def __iter__(self) -> Generator[OptionStep, None, _T_co]:
        value = self.run()
        yield OptionStep(value)
        if isinstance(value, Some):
            return value.some
        raise RuntimeError("A failed computation must not be resumed")


@overload
def computation(value: Ok[_T]) -> ResultComputation[_T, Never]: ...


@overload
def computation(value: Error[_E]) -> ResultComputation[Never, _E]: ...


@overload
def computation(value: Result[_T, _E]) -> ResultComputation[_T, _E]: ...


@overload
def computation(value: Some[_T]) -> OptionComputation[_T]: ...


@overload
def computation(value: Nothing) -> OptionComputation[Never]: ...


@overload
def computation(value: Option[_T]) -> OptionComputation[_T]: ...


def computation(value: Result[_T, _E] | Option[_T]) -> ResultComputation[_T, _E] | OptionComputation[_T]:
    match value:
        case Ok() | Error():
            return ResultComputation(lambda: value)
        case _:
            return OptionComputation(lambda: value)


def result(body: Callable[_P, ResultBody[_T, _E]]) -> Callable[_P, ResultComputation[_T, _E]]:
    @wraps(body)
    def delayed(*args: _P.args, **kwargs: _P.kwargs) -> ResultComputation[_T, _E]:
        def run() -> Result[_T, _E]:
            generator = body(*args, **kwargs)
            try:
                while True:
                    try:
                        step = next(generator)
                    except StopIteration as done:
                        return Ok(cast(_T, done.value))
                    match step:
                        case ResultStep(Error() as failure):
                            return failure
                        case ResultStep(Ok()):
                            pass
                        case _:
                            raise TypeError("Expected a Result computation")
            finally:
                generator.close()

        return ResultComputation(run)

    return delayed


def option(body: Callable[_P, OptionBody[_T]]) -> Callable[_P, OptionComputation[_T]]:
    @wraps(body)
    def delayed(*args: _P.args, **kwargs: _P.kwargs) -> OptionComputation[_T]:
        def run() -> Option[_T]:
            generator = body(*args, **kwargs)
            try:
                while True:
                    try:
                        step = next(generator)
                    except StopIteration as done:
                        return Some(cast(_T, done.value))
                    match step:
                        case OptionStep(Nothing()):
                            return NOTHING
                        case OptionStep(Some()):
                            pass
                        case _:
                            raise TypeError("Expected an Option computation")
            finally:
                generator.close()

        return OptionComputation(run)

    return delayed


YieldResultBody = TypeAliasType(
    "YieldResultBody", Generator[_T | ResultStep[_E], None, _T | None], type_params=(_T, _E)
)


def yield_result(body: Callable[_P, YieldResultBody[_T, _E]]) -> Callable[_P, ResultComputation[_T, _E]]:
    """Probe the legacy yield-as-Return spelling with last-value Combine.

    This intentionally exposes its limits: None/fallthrough is ambiguous,
    conditional omission of all Return operations requires a runtime check,
    and the private step envelope is reserved rather than a legal raw payload.
    """

    @wraps(body)
    def delayed(*args: _P.args, **kwargs: _P.kwargs) -> ResultComputation[_T, _E]:
        return ResultComputation(lambda: _run_yield_result(body(*args, **kwargs)))

    return delayed


def _finish_yield_result(returned: _T | None, last: Result[_T, _E] | None) -> Result[_T, _E]:
    if returned is not None:
        return Ok(returned)
    if last is None:
        raise RuntimeError("The computation did not produce a result")
    return last


def _run_yield_result(generator: YieldResultBody[_T, _E]) -> Result[_T, _E]:
    last: Result[_T, _E] | None = None
    try:
        while True:
            try:
                step = next(generator)
            except StopIteration as done:
                return _finish_yield_result(cast(_T | None, done.value), last)
            if isinstance(step, ResultStep):
                # The raw-yield variant reserves ResultStep for protocol events.
                # T=object defeats that boundary; the counterexample test records
                # why this variant is not a sound public API.
                checked = cast(ResultStep[_E], step)
                if isinstance(checked.value, Error):
                    return checked.value
            else:
                last = Ok(step)
    finally:
        generator.close()
