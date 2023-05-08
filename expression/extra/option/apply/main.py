from __future__ import annotations

from collections.abc import Callable
from functools import partial
from inspect import Parameter, isclass, signature
from typing import TYPE_CHECKING, Any, Generic, Protocol, TypeVar, Union, cast, overload

from typing_extensions import TypeVarTuple, Unpack

from expression.core.option import Nothing, Nothing_, Some

if TYPE_CHECKING:
    from expression.core.option import Option

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

__all__ = ["Seq", "Func", "Call", "func", "of_obj", "of_iterable", "call"]


class Apply(Generic[ValueT]):
    """Base class to apply

    Args:
        value: Value wrapped as Option
    """

    def __init__(self, value: Option[ValueT]) -> None:
        self._value = value

    @property
    def value(self) -> Option[ValueT]:
        """wrapped value as Option"""
        return self._value

    def __repr__(self) -> str:
        name = type(self).__name__
        return f"<{name}: {repr(self.value)}>"

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Apply) and (
            self.value == other.value  # type: ignore[reportUnknownMemberType]
        )


class Seq(Apply[tuple[Unpack[ArgsT]]], Generic[Unpack[ArgsT]]):
    """some Values wrapped as Option for use to apply

    Example:
        >>> from expression import Some, Option
        >>> from expression.extra.option.apply import Seq, Func, call, func
        >>>
        >>>
        >>> def test_func(a: int, b: int, c: str) -> tuple[int, str]:
        >>>     return (a + b, c)
        >>>
        >>>
        >>> values: tuple[int, int, str] = (1, 1, "q")
        >>> some_value: Option[tuple[int, int, str]] = Some(values)
        >>> wrapped_seq: Seq[int, int, str] = Seq(some_value)
        >>> wrapped_func: Func[int, int, str, tuple[int, str]] = func(test_func)
        >>>
        >>> new_func: Func[tuple[int, str]] = wrapped_func * wrapped_seq
        >>> assert new_func * call == Some(test_func(*values))
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
                self.value.map2(lambda xs, ys: (*xs, *ys), func_or_arg_or_args.value),
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
                self.value.map2(_combine, func_or_arg_or_args.value)
                .map(_switch)
                .map(lambda tup: (*tup[0], *tup[1])),
            )
        if callable(func_or_arg_or_args):
            return func(func_or_arg_or_args) * self
        raise NotImplementedError


class Func(
    Apply[Callable[[Unpack[ArgsT]], ReturnT]],
    Generic[Unpack[ArgsT], ReturnT],
):
    """a function(without keyword parameters) wrapped as Option for use to apply

    Example:
        >>> from expression import Some, Option
        >>> from expression.extra.option.apply import Seq, Func, call, func
        >>>
        >>>
        >>> def test_func(a: int, b: int, c: str) -> tuple[int, str]:
        >>>     return (a + b, c)
        >>>
        >>>
        >>> values: tuple[int, int, str] = (1, 1, "q")
        >>> some_value: Option[tuple[int, int, str]] = Some(values)
        >>> wrapped_seq: Seq[int, int, str] = Seq(some_value)
        >>> wrapped_func: Func[int, int, str, tuple[int, str]] = Func(Some(test_func))
        >>>
        >>> new_func: Func[tuple[int, str]] = wrapped_func * wrapped_seq
        >>> assert new_func * call == Some(test_func(*values))
    """

    def __init__(self, value: Option[Callable[[Unpack[ArgsT]], ReturnT]]) -> None:
        if isinstance(value, Nothing_) or not (params := _keyword_params(value.value)):
            super().__init__(value)
            return
        error_msg = "func has keyword params: \n" + "\n".join(map(str, params.values()))
        raise TypeError(error_msg)

    @overload
    def __mul__(
        self: Func[OtherReturnT],
        caller_or_arg_or_args: Union[type[Call], Call],
    ) -> Option[OtherReturnT]:
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
        Option[OtherReturnT],
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
                _self.value.map2(_partial_1, _caller_or_arg_or_args.value),
            )
        if isclass(caller_or_arg_or_args) and issubclass(
            caller_or_arg_or_args,
            Call,
        ):
            _self = cast("Func[OtherReturnT]", self)
            return caller_or_arg_or_args() * _self
        raise NotImplementedError

    __rmul__ = __mul__

    def __mod__(self, arg_or_args: Seq[Unpack[ArgsT]]) -> Option[ReturnT]:
        return self * arg_or_args * call

    __rmod__ = __mod__

    def __call__(self, *args: Unpack[ArgsT]) -> Option[ReturnT]:
        return self * of_iterable(*args) * call


class Call:
    """call magic method '__call__' of wrapped function

    WARNING:
        function wrapped as Option is not safe.
        The error is still exposed.
    """

    def __mul__(self, func: Func[ReturnT]) -> Option[ReturnT]:
        if isinstance(func.value, Nothing_):
            return Nothing
        return Some(func.value.value())


@overload
def func(f: Callable[[Unpack[ArgsT]], ReturnT]) -> Func[Unpack[ArgsT], ReturnT]:
    ...


@overload
def func(f: Option[Callable[[Unpack[ArgsT]], ReturnT]]) -> Func[Unpack[ArgsT], ReturnT]:
    ...


def func(
    f: Union[
        Callable[[Unpack[ArgsT]], ReturnT],
        Option[Callable[[Unpack[ArgsT]], ReturnT]],
    ],
) -> Func[Unpack[ArgsT], ReturnT]:
    """convert function(or wrapped as Option) to Func

    Args:
        f: callable(without keyword parameters)

    Returns:
        wrapped function as Func
    """
    if isinstance(f, Some | Nothing_):
        return Func(f)
    return Func(Some(f))


@overload
def of_obj(value: Option[ValueT]) -> Seq[ValueT]:
    ...


@overload
def of_obj(value: ArgT) -> Seq[ArgT]:
    ...


def of_obj(value: Union[ArgT, Option[ValueT]]) -> Union[Seq[ArgT], Seq[ValueT]]:
    """convert a value(or wrapped as Option) to Var

    Args:
        value: some native value or Option[value]

    Returns:
        wrapped value as Var
    """
    if isinstance(value, Some | Nothing_):
        return Seq(cast("Option[ValueT]", value).map(_tup_0))
    return Seq(Some((value,)))


def of_iterable(*values: Unpack[ArgsT]) -> Seq[Unpack[ArgsT]]:
    """convert some values to Seq

    Returns:
        wrapped values as Seq
    """
    return Seq(Some(values))


def _partial_1(
    func: _Callable[Unpack[OtherArgsT], Unpack[AnotherArgsT], ReturnT],
    args: tuple[Unpack[OtherArgsT]],
) -> Callable[[Unpack[AnotherArgsT]], ReturnT]:
    return partial(func, *args)


def _switch(value: tuple[ArgT, OtherArgT]) -> tuple[OtherArgT, ArgT]:
    return (value[1], value[0])


def _combine(x: ArgT, y: OtherArgT) -> tuple[ArgT, OtherArgT]:
    return x, y


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


call = Call()
