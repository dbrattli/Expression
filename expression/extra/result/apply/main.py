from __future__ import annotations

from collections.abc import Callable
from functools import partial
from inspect import Parameter, isclass, signature
from operator import methodcaller
from typing import TYPE_CHECKING, Any, Generic, Protocol, TypeVar, Union, cast, overload

from typing_extensions import TypeVarTuple, Unpack

from expression.core.result import Error, Ok

if TYPE_CHECKING:
    from expression.core.result import Result

    _ArgsT = TypeVarTuple("_ArgsT")
    _ReturnT_co = TypeVar("_ReturnT_co", covariant=True)

    class _Callable(Protocol, Generic[Unpack[_ArgsT], _ReturnT_co]):
        def __call__(self, *args: Unpack[_ArgsT]) -> _ReturnT_co:
            ...


ArgT = TypeVar("ArgT")
OtherArgT = TypeVar("OtherArgT")
ValueT = TypeVar("ValueT")
ReturnT = TypeVar("ReturnT")
OtherReturnT = TypeVar("OtherReturnT")
ArgsT = TypeVarTuple("ArgsT")
OtherArgsT = TypeVarTuple("OtherArgsT")
AnotherArgsT = TypeVarTuple("AnotherArgsT")
ErrorT = TypeVar("ErrorT", bound=Exception)

__all__ = ["Seq", "Func", "Call", "func", "of_obj", "of_iterable", "call"]


class Apply(Generic[ValueT]):
    """Base class to apply

    Args:
        value: Value wrapped as Result
    """

    def __init__(self, value: Result[ValueT, Any]) -> None:
        self._value = value

    @property
    def value(self) -> Result[ValueT, Any]:
        """wrapped value as Result"""
        return self._value

    def __repr__(self) -> str:
        name = type(self).__name__
        return f"<{name}: {repr(self.value)}>"

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Apply) and (
            self.value == other.value  # type: ignore[reportUnknownMemberType]
        )


class Seq(Apply[tuple[Unpack[ArgsT]]], Generic[Unpack[ArgsT]]):
    """some Values wrapped as Result for use to apply

    Example:
        >>> from expression import Ok
        >>> from expression.extra.result.apply import call, func, of_iterable, of_obj
        >>>
        >>> ### declare
        >>> values = (1, "q", b"w")
        >>> seq_0 = of_iterable(*values)
        >>> seq_1 = of_obj(values[0]) * of_obj(values[1]) * of_obj(values[2])
        >>> seq_2 = (
        >>>     of_iterable(values[0])
        >>>     * of_iterable(values[1])
        >>>     * of_iterable(values[2])
        >>> )
        >>> assert seq_0 == seq_1 == seq_2
        >>> assert seq_0 * of_obj(1) != of_obj(1) * seq_0
        >>> assert seq_0 * of_iterable(1, 2) != of_iterable(1, 2) * seq_0
        >>>
        >>> ### declare as result
        >>> seq_3 = (
        >>>     of_obj(Ok(values[0]))
        >>>     * of_obj(Ok(values[1]))
        >>>     * of_obj(Ok(values[2]))
        >>> )
        >>> assert seq_0 == seq_3
        >>>
        >>>
        >>> ### with function
        >>> @func
        >>> def test_func(a: int, b: str, c: bytes) -> tuple[int, str, bytes]:
        >>>     return (a, b, c)
        >>> # or
        >>> # test_func = func(test_func)
        >>>
        >>>
        >>> left, right = of_obj(values[0]), of_iterable(*values[1:])
        >>> lr_seq = left * right
        >>> res_0 = test_func * left * right * call
        >>> res_1 = left * test_func * right * call
        >>> res_2 = left * right * test_func * call
        >>> res_3 = lr_seq * test_func * call
        >>> res_4 = test_func * lr_seq * call
        >>> res_5 = test_func % lr_seq
        >>> res_6 = lr_seq % test_func
        >>> assert res_0 == res_1 == res_2 == res_3 == res_4 == res_5 == res_6
        >>>
        >>>
        >>> ### only __mod__
        >>> def other_test_func(a: int, b: str, c: bytes) -> tuple[int, str, bytes]:
        >>>     return (a, b, c)
        >>>
        >>>
        >>> another_test_func = func(other_test_func)
        >>> assert other_test_func % lr_seq == another_test_func % lr_seq
    """

    @overload
    def __mul__(
        self,
        func_or_arg_or_args: Seq[Unpack[OtherArgsT]],
    ) -> Seq[Unpack[ArgsT], Unpack[OtherArgsT]]:
        ...

    @overload
    def __mul__(
        self,
        func_or_arg_or_args: Union[
            _Callable[Unpack[ArgsT], Unpack[OtherArgsT], ReturnT],
            Func[Unpack[ArgsT], Unpack[OtherArgsT], ReturnT],
        ],
    ) -> Func[Unpack[OtherArgsT], ReturnT]:
        ...

    @overload
    def __mul__(
        self,
        func_or_arg_or_args: Union[
            _Callable[Unpack[ArgsT], ReturnT],
            Func[Unpack[ArgsT], ReturnT],
        ],
    ) -> Func[ReturnT]:
        ...

    def __mul__(
        self,
        func_or_arg_or_args: Union[
            Seq[Unpack[OtherArgsT]],
            _Callable[Unpack[ArgsT], Unpack[OtherArgsT], ReturnT],
            Func[Unpack[ArgsT], Unpack[OtherArgsT], ReturnT],
            _Callable[Unpack[ArgsT], ReturnT],
            Func[Unpack[ArgsT], ReturnT],
        ],
    ) -> Union[
        Seq[Unpack[ArgsT], Unpack[OtherArgsT]],
        Func[Unpack[OtherArgsT], ReturnT],
        Func[ReturnT],
    ]:
        if isinstance(func_or_arg_or_args, Func):
            return func_or_arg_or_args * self
        if isinstance(func_or_arg_or_args, Seq):
            return Seq(
                self.value.map2(func_or_arg_or_args.value, lambda xs, ys: (*xs, *ys)),
            )
        if callable(func_or_arg_or_args):
            return self * func(func_or_arg_or_args)
        raise NotImplementedError

    @overload
    def __rmul__(
        self,
        func_or_arg_or_args: Seq[Unpack[OtherArgsT]],
    ) -> Seq[Unpack[OtherArgsT], Unpack[ArgsT]]:
        ...

    @overload
    def __rmul__(
        self,
        func_or_arg_or_args: Union[
            _Callable[Unpack[ArgsT], Unpack[OtherArgsT], ReturnT],
            Func[Unpack[ArgsT], Unpack[OtherArgsT], ReturnT],
        ],
    ) -> Func[Unpack[OtherArgsT], ReturnT]:
        ...

    @overload
    def __rmul__(
        self,
        func_or_arg_or_args: Union[
            _Callable[Unpack[ArgsT], ReturnT],
            Func[Unpack[ArgsT], ReturnT],
        ],
    ) -> Func[ReturnT]:
        ...

    def __rmul__(
        self,
        func_or_arg_or_args: Union[
            Seq[Unpack[OtherArgsT]],
            _Callable[Unpack[ArgsT], Unpack[OtherArgsT], ReturnT],
            Func[Unpack[ArgsT], Unpack[OtherArgsT], ReturnT],
            _Callable[Unpack[ArgsT], ReturnT],
            Func[Unpack[ArgsT], ReturnT],
        ],
    ) -> Union[
        Seq[Unpack[OtherArgsT], Unpack[ArgsT]],
        Func[Unpack[OtherArgsT], ReturnT],
        Func[ReturnT],
    ]:
        if isinstance(func_or_arg_or_args, Func):
            return func_or_arg_or_args * self
        if isinstance(func_or_arg_or_args, Seq):
            return Seq(
                self.value.map2(func_or_arg_or_args.value, lambda xs, ys: (*ys, *xs)),
            )
        if callable(func_or_arg_or_args):
            return func(func_or_arg_or_args) * self
        raise NotImplementedError

    def __mod__(
        self,
        f: Union[Callable[[Unpack[ArgsT]], ReturnT], Func[Unpack[ArgsT], ReturnT]],
    ) -> Result[ReturnT, Any]:
        if isinstance(f, Func):
            return f % self
        if callable(f):
            return func(f) % self
        raise NotImplementedError

    __rmod__ = __mod__


class Func(
    Apply[Callable[[Unpack[ArgsT]], ReturnT]],
    Generic[Unpack[ArgsT], ReturnT],
):
    """a function(without keyword parameters) wrapped as Result for use to apply

    Example:
        >>> from expression import Ok
        >>> from expression.extra.result.apply import call, func, of_iterable, of_obj
        >>>
        >>>
        >>> ### declare
        >>> def test_func_0(a: int, b: str, c: bytes) -> tuple[int, str, bytes]:
        >>>     return (a, b, c)
        >>>
        >>>
        >>> @func
        >>> def test_func_1(a: int, b: str, c: bytes) -> tuple[int, str, bytes]:
        >>>     return (a, b, c)
        >>>
        >>>
        >>> test_func_2 = func(test_func_0)
        >>>
        >>> ### __call__
        >>> values = (1, "q", b"w")
        >>> seq = of_iterable(*values)
        >>> assert (
        >>>     Ok(test_func_0(*values))
        >>>     == test_func_1(*values)
        >>>     == test_func_2(*values)
        >>>     == test_func_1 * seq * call
        >>>     == seq * test_func_1 * call
        >>>     == test_func_1 % seq
        >>>     == seq % test_func_1
        >>>     == test_func_2 * seq * call
        >>>     == seq * test_func_2 * call
        >>>     == test_func_2 % seq
        >>>     == seq % test_func_2
        >>> )
        >>>
        >>>
        >>> ### with seq
        >>>
        >>> values = (1, "q", b"w")
        >>> left, right = of_obj(values[0]), of_iterable(*values[1:])
        >>> lr_seq = left * right
        >>> res_0 = test_func_1 * left * right * call
        >>> res_1 = left * test_func_1 * right * call
        >>> res_2 = left * right * test_func_1 * call
        >>> res_3 = lr_seq * test_func_1 * call
        >>> res_4 = test_func_1 * lr_seq * call
        >>> res_5 = test_func_1 % lr_seq
        >>> res_6 = lr_seq % test_func_1
        >>> assert res_0 == res_1 == res_2 == res_3 == res_4 == res_5 == res_6
        >>>
        >>>
        >>> ### only __mod__
        >>> assert (
        >>>     test_func_1 % values
        >>>     == test_func_1 % Ok(values)
        >>>     == test_func_1 % lr_seq
        >>> )
    """

    def __init__(self, value: Result[Callable[[Unpack[ArgsT]], ReturnT], Any]) -> None:
        if isinstance(value, Error) or not (params := _keyword_params(value.value)):
            super().__init__(value)
            return
        error_msg = "func has keyword params: \n" + "\n".join(map(str, params.values()))
        raise TypeError(error_msg)

    @overload
    def __mul__(
        self: Func[OtherReturnT],
        caller_or_arg_or_args: Union[type[Call], Call],
    ) -> Result[OtherReturnT, Any]:
        ...

    @overload
    def __mul__(
        self: Func[Unpack[OtherArgsT], Unpack[AnotherArgsT], OtherReturnT],
        caller_or_arg_or_args: Seq[Unpack[OtherArgsT]],
    ) -> Func[Unpack[AnotherArgsT], OtherReturnT]:
        ...

    @overload
    def __mul__(
        self: Func[Unpack[ArgsT], ReturnT],
        caller_or_arg_or_args: Seq[Unpack[ArgsT]],
    ) -> Func[ReturnT]:
        ...

    def __mul__(
        self: Union[
            Func[OtherReturnT],
            Func[Unpack[OtherArgsT], Unpack[AnotherArgsT], OtherReturnT],
            Func[Unpack[ArgsT], ReturnT],
        ],
        caller_or_arg_or_args: Union[
            type[Call],
            Call,
            Seq[Unpack[OtherArgsT]],
            Seq[Unpack[ArgsT]],
        ],
    ) -> Union[
        Result[OtherReturnT, Any],
        Func[Unpack[AnotherArgsT], OtherReturnT],
        Func[ReturnT],
    ]:
        if isinstance(caller_or_arg_or_args, Call):
            _self = cast("Func[OtherReturnT]", self)
            return caller_or_arg_or_args * _self
        if isinstance(caller_or_arg_or_args, Seq):
            _self = cast(
                "Func[Unpack[OtherArgsT], Unpack[AnotherArgsT], OtherReturnT]",
                self,
            )
            _caller_or_arg_or_args = cast(
                "Seq[Unpack[OtherArgsT]]",
                caller_or_arg_or_args,
            )
            return Func(
                _self.value.map2(_caller_or_arg_or_args.value, _partial_1),
            )
        if isclass(caller_or_arg_or_args) and issubclass(
            caller_or_arg_or_args,
            Call,
        ):
            _self = cast("Func[OtherReturnT]", self)
            return caller_or_arg_or_args() * _self
        raise NotImplementedError

    __rmul__ = __mul__

    def __mod__(
        self,
        arg_or_args: Union[
            Seq[Unpack[ArgsT]],
            Result[tuple[Unpack[ArgsT]], Any],
            tuple[Unpack[ArgsT]],
        ],
    ) -> Result[ReturnT, Any]:
        if isinstance(arg_or_args, Seq):
            return self * arg_or_args * call
        if isinstance(arg_or_args, Ok | Error):
            return self * Seq(arg_or_args) * call
        if isinstance(arg_or_args, tuple):  # type: ignore[reportUnnecessaryIsInstance]
            return self * Seq(Ok(arg_or_args)) * call
        raise NotImplementedError

    __rmod__ = __mod__

    def __call__(self, *args: Unpack[ArgsT]) -> Result[ReturnT, Any]:
        return self * of_iterable(*args) * call


class Call:
    """call magic method '__call__' of wrapped function"""

    def __mul__(self, func: Func[ReturnT]) -> Result[ReturnT, Any]:
        return func.value.map(_safe).bind(_call)


@overload
def func(f: Callable[[Unpack[ArgsT]], ReturnT]) -> Func[Unpack[ArgsT], ReturnT]:
    ...


@overload
def func(
    f: Result[Callable[[Unpack[ArgsT]], ReturnT], Any],
) -> Func[Unpack[ArgsT], ReturnT]:
    ...


def func(
    f: Union[
        Callable[[Unpack[ArgsT]], ReturnT],
        Result[Callable[[Unpack[ArgsT]], ReturnT], Any],
    ],
) -> Func[Unpack[ArgsT], ReturnT]:
    """convert function(or wrapped as Result) to Func

    Args:
        f: callable(without keyword parameters)

    Returns:
        wrapped function as Func
    """
    if isinstance(f, Ok | Error):
        return Func(f)
    return Func(Ok(f))


@overload
def of_obj(value: Result[ValueT, Any]) -> Seq[ValueT]:
    ...


@overload
def of_obj(value: ArgT) -> Seq[ArgT]:
    ...


def of_obj(value: Union[ArgT, Result[ValueT, Any]]) -> Union[Seq[ArgT], Seq[ValueT]]:
    """convert a value(or wrapped as Result) to Var

    Args:
        value: some native value or Result[value, Any]

    Returns:
        wrapped value as Var
    """
    if isinstance(value, Ok | Error):
        return Seq(cast("Result[ValueT, Any]", value).map(_tup_0))
    return Seq(Ok((value,)))


def of_iterable(*values: Unpack[ArgsT]) -> Seq[Unpack[ArgsT]]:
    """convert some values to Seq

    Returns:
        wrapped values as Seq
    """
    return Seq(Ok(values))


def _base_safe(
    func: Callable[[], ReturnT],
    error: type[ErrorT],
) -> Callable[[], Result[ReturnT, ErrorT]]:
    def inner() -> Result[ReturnT, ErrorT]:
        try:
            result = func()
        except error as exc:
            return Error(exc)
        return Ok(result)

    return inner


def _partial_1(
    func: _Callable[Unpack[OtherArgsT], Unpack[AnotherArgsT], ReturnT],
    args: tuple[Unpack[OtherArgsT]],
) -> Callable[[Unpack[AnotherArgsT]], ReturnT]:
    return partial(func, *args)


def _tup_0(x: ArgT) -> tuple[ArgT]:
    return (x,)


def _keyword_params(func: Callable[..., Any]) -> dict[str, Parameter]:
    params = signature(func).parameters

    has_slash = False
    positional = {
        Parameter.POSITIONAL_ONLY,
        Parameter.POSITIONAL_OR_KEYWORD,
        Parameter.VAR_POSITIONAL,
    }
    keyword_params: dict[str, Parameter] = {}
    for name, param in params.items():
        if param.kind == param.POSITIONAL_ONLY:
            has_slash = True
        if has_slash:
            if param.kind != param.POSITIONAL_ONLY:
                keyword_params[name] = param
            continue
        if param.kind not in positional:
            keyword_params[name] = param

    return keyword_params


_safe = partial(_base_safe, error=Exception)
_call = methodcaller("__call__")
call = Call()
