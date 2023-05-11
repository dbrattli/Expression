from __future__ import annotations

from inspect import signature
from typing import Callable, Generic, ParamSpec, TypeVar, Union, final, overload

from expression import Error, Ok, Result

ParamT = ParamSpec("ParamT")
ValueT = TypeVar("ValueT")
ErrorT = TypeVar("ErrorT", bound=Exception)
OtherErrorT = TypeVar("OtherErrorT", bound=Exception)
AnotherErrorT = TypeVar("AnotherErrorT", bound=Exception)


@final
class _Catch(Generic[ErrorT]):
    def __init__(self, error: Union[type[ErrorT], tuple[type[ErrorT], ...]]) -> None:
        if isinstance(error, tuple):
            self.error = error
        else:
            self.error = (error,)

    def __repr__(self) -> str:
        return f"<Catch: ..., [{self.error_string}]>"

    @property
    def error_string(self) -> str:
        return ",".join(x.__name__ for x in self.error)

    def combine(self, catch: _Catch[OtherErrorT]) -> _Catch[Union[ErrorT, OtherErrorT]]:
        return _Catch((*self.error, *catch.error))

    @overload
    def __call__(  # type: ignore
        self, func: Callable[ParamT, Result[ValueT, OtherErrorT]]
    ) -> Callable[ParamT, Result[ValueT, Union[ErrorT, OtherErrorT]]]:
        ...

    @overload
    def __call__(
        self, func: Callable[ParamT, ValueT]
    ) -> Callable[ParamT, Result[ValueT, ErrorT]]:
        ...

    def __call__(
        self,
        func: Union[
            Callable[ParamT, ValueT],
            Callable[ParamT, Result[ValueT, OtherErrorT]],
        ],
    ) -> Union[
        Callable[ParamT, Result[ValueT, ErrorT]],
        Callable[ParamT, Result[ValueT, Union[ErrorT, OtherErrorT]]],
    ]:
        if isinstance(func, _Catched):
            return func.combine(self)  # type: ignore
        return _Catched(func, catch=self)  # type: ignore


@final
class _Catched(Generic[ParamT, ValueT, ErrorT]):
    def __init__(self, func: Callable[ParamT, ValueT], catch: _Catch[ErrorT]) -> None:
        self.func = func
        self.catch = catch

    def combine(
        self, catch: _Catch[OtherErrorT]
    ) -> _Catched[ParamT, ValueT, Union[ErrorT, OtherErrorT]]:
        new_catch = self.catch.combine(catch)
        return _Catched(self.func, catch=new_catch)

    def __call__(
        self, *args: ParamT.args, **kwargs: ParamT.kwargs
    ) -> Result[ValueT, ErrorT]:
        try:
            out = self.func(*args, **kwargs)
        except self.catch.error as exc:
            return Error(exc)  # type: ignore

        if isinstance(out, (Ok, Error)):
            return out  # type: ignore
        return Ok(out)

    def __repr__(self) -> str:
        return f"<Catched: {signature(self.func)!s}, [{self.catch.error_string}]>"


@overload
def catch(
    func: None = ...,
    *,
    exception: type[ErrorT],
) -> _Catch[ErrorT]:
    ...


@overload
def catch(  # type: ignore
    func: Callable[ParamT, Result[ValueT, OtherErrorT]],
    *,
    exception: type[ErrorT],
) -> Callable[ParamT, Result[ValueT, Union[ErrorT, OtherErrorT]]]:
    ...


@overload
def catch(
    func: Callable[ParamT, ValueT],
    *,
    exception: type[ErrorT],
) -> Callable[ParamT, Result[ValueT, ErrorT]]:
    ...


def catch(
    func: Union[
        None,
        Callable[ParamT, ValueT],
        Callable[ParamT, Result[ValueT, OtherErrorT]],
    ] = None,
    *,
    exception: type[ErrorT],
) -> Union[
    _Catch[ErrorT],
    Callable[ParamT, Result[ValueT, ErrorT]],
    Callable[ParamT, Result[ValueT, Union[ErrorT, OtherErrorT]]],
]:
    func_catch = _Catch(exception)
    if func is None:
        return func_catch
    return func_catch(func)  # type: ignore


__all__ = ["catch"]
