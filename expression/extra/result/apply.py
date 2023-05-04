from __future__ import annotations

from collections.abc import Callable
from functools import partial
from inspect import isclass
from operator import methodcaller
from typing import TYPE_CHECKING, Any, Generic, TypeVar, Union, cast, overload

from typing_extensions import TypeVarTuple, Unpack

from expression.core.result import Error, Ok

if TYPE_CHECKING:
    from expression.core.result import Result

ArgT = TypeVar("ArgT")
OtherArgT = TypeVar("OtherArgT")
ValueT = TypeVar("ValueT")
ReturnT = TypeVar("ReturnT")
OtherReturnT = TypeVar("OtherReturnT")
ArgsT = TypeVarTuple("ArgsT")
OtherArgsT = TypeVarTuple("OtherArgsT")
AnotherArgsT = TypeVarTuple("AnotherArgsT")

__all__ = ["Var", "Seq", "Func", "Call", "func", "of_obj", "of_iterable", "call"]


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


class Var(Apply[ValueT], Generic[ValueT]):
    """a Value wrapped as Result for use to apply

    Example:
        >>> from typing import Any
        >>> from expression import Ok, Result
        >>> from expression.extra.result.apply import Var, Func, call
        >>>
        >>>
        >>> def func(a: int) -> int:
        >>>     return a
        >>>
        >>>
        >>> value: int = 1
        >>> some_value: Result[int, Any] = Ok(1)
        >>> wrapped: Var[int] = Var(some_value)
        >>>
        >>> new_func: Func[int] = func * wrapped
        >>> assert new_func * call == Ok(value)
    """

    @overload
    def __mul__(
        self: Var[ArgT],
        func_or_arg_or_args: Union[
            Callable[[ArgT, Unpack[ArgsT]], ReturnT], Func[ArgT, Unpack[ArgsT], ReturnT]
        ],
    ) -> Func[Unpack[ArgsT], ReturnT]:
        ...

    @overload
    def __mul__(
        self: Var[ArgT],
        func_or_arg_or_args: Seq[Unpack[ArgsT]],
    ) -> Seq[ArgT, Unpack[ArgsT]]:
        ...

    @overload
    def __mul__(
        self: Var[ArgT],
        func_or_arg_or_args: Var[OtherArgT],
    ) -> Seq[ArgT, OtherArgT]:
        ...

    @overload
    def __mul__(
        self: Var[ArgT],
        func_or_arg_or_args: Union[
            Func[ArgT, Unpack[ArgsT], ReturnT],
            Seq[Unpack[ArgsT]],
            Var[OtherArgT],
            Callable[[ArgT, Unpack[ArgsT]], ReturnT],
        ],
    ) -> Union[
        Func[Unpack[ArgsT], ReturnT], Seq[ArgT, Unpack[ArgsT]], Seq[ArgT, OtherArgT]
    ]:
        ...

    # FIXME: error in pyright. but it works.
    def __mul__(  # type: ignore
        self: Var[ArgT],
        func_or_arg_or_args: Union[
            Func[ArgT, Unpack[ArgsT], ReturnT],
            Seq[Unpack[ArgsT]],
            Var[OtherArgT],
            Callable[[ArgT, Unpack[ArgsT]], ReturnT],
        ],
    ) -> Union[
        Func[Unpack[ArgsT], ReturnT], Seq[ArgT, Unpack[ArgsT]], Seq[ArgT, OtherArgT]
    ]:
        if isinstance(func_or_arg_or_args, Func):
            return func_or_arg_or_args * self
        if isinstance(func_or_arg_or_args, Var):
            return Seq(
                self.value.map2(func_or_arg_or_args.value, _iter_tuple_0),
            )
        if isinstance(func_or_arg_or_args, Seq):
            return Seq(
                self.value.map2(func_or_arg_or_args.value, _iter_unpack_tuple_0),
            )
        if callable(func_or_arg_or_args):
            return self * func(func_or_arg_or_args)
        raise NotImplementedError

    @overload
    def __rmul__(
        self: Var[ArgT],
        func_or_arg_or_args: Union[
            Callable[[ArgT, Unpack[ArgsT]], ReturnT], Func[ArgT, Unpack[ArgsT], ReturnT]
        ],
    ) -> Func[Unpack[ArgsT], ReturnT]:
        ...

    @overload
    def __rmul__(
        self: Var[ArgT],
        func_or_arg_or_args: Seq[Unpack[ArgsT]],
    ) -> Seq[Unpack[ArgsT], ArgT]:
        ...

    @overload
    def __rmul__(
        self: Var[ArgT],
        func_or_arg_or_args: Var[OtherArgT],
    ) -> Seq[OtherArgT, ArgT]:
        ...

    @overload
    def __rmul__(
        self: Var[ArgT],
        func_or_arg_or_args: Union[
            Func[ArgT, Unpack[ArgsT], ReturnT],
            Seq[Unpack[ArgsT]],
            Var[OtherArgT],
            Callable[[ArgT, Unpack[ArgsT]], ReturnT],
        ],
    ) -> Union[
        Func[Unpack[ArgsT], ReturnT], Seq[Unpack[ArgsT], ArgT], Seq[OtherArgT, ArgT]
    ]:
        ...

    # FIXME: error in pyright. but it works.
    def __rmul__(  # type: ignore
        self: Var[ArgT],
        func_or_arg_or_args: Union[
            Func[ArgT, Unpack[ArgsT], ReturnT],
            Seq[Unpack[ArgsT]],
            Var[OtherArgT],
            Callable[[ArgT, Unpack[ArgsT]], ReturnT],
        ],
    ) -> Union[
        Func[Unpack[ArgsT], ReturnT], Seq[Unpack[ArgsT], ArgT], Seq[OtherArgT, ArgT]
    ]:
        if isinstance(func_or_arg_or_args, Func):
            return func_or_arg_or_args * self
        if isinstance(func_or_arg_or_args, Var):
            return Seq(
                self.value.map2(func_or_arg_or_args.value, _iter_tuple_1),
            )
        if isinstance(func_or_arg_or_args, Seq):
            return Seq(
                self.value.map2(func_or_arg_or_args.value, _iter_unpack_tuple_1),
            )
        if callable(func_or_arg_or_args):
            return func(func_or_arg_or_args) * self
        raise NotImplementedError


class Seq(Apply[tuple[Unpack[ArgsT]]], Generic[Unpack[ArgsT]]):
    """some Values wrapped as Result for use to apply

    Example:
        >>> from typing import Any
        >>> from expression import Ok, Result
        >>> from expression.extra.result.apply import Seq, Func, call
        >>>
        >>>
        >>> def func(a: int, b: int, c: str) -> tuple[int, str]:
        >>>     return (a + b, c)
        >>>
        >>>
        >>> values: tuple[int, int, str] = (1, 1, "q")
        >>> some_value: Result[tuple[int, int, str], Any] = Ok(values)
        >>> wrapped: Seq[int, int, str] = Seq(some_value)
        >>>
        >>> new_func: Func[tuple[int, str]] = func * wrapped
        >>> assert new_func * call == Ok(func(*values))
    """

    @overload
    def __mul__(
        self: Seq[Unpack[OtherArgsT]],
        func_or_arg_or_args: Union[
            Callable[
                # [Unpack, Unpack]
                # The pyright indicates an error,
                # but the type inference is carried out normally.
                [Unpack[OtherArgsT], Unpack[AnotherArgsT]],  # type: ignore
                ReturnT,
            ],
            Func[
                Unpack[OtherArgsT],
                Unpack[AnotherArgsT],
                ReturnT,
            ],
        ],
    ) -> Func[Unpack[AnotherArgsT], ReturnT]:
        ...

    @overload
    def __mul__(
        self: Seq[Unpack[OtherArgsT]],
        func_or_arg_or_args: Var[ArgT],
    ) -> Seq[Unpack[OtherArgsT], ArgT]:
        ...

    @overload
    def __mul__(
        self: Seq[Unpack[OtherArgsT]],
        func_or_arg_or_args: Seq[Unpack[AnotherArgsT]],
    ) -> Seq[Unpack[OtherArgsT], Unpack[AnotherArgsT]]:
        ...

    @overload
    def __mul__(
        self: Seq[Unpack[OtherArgsT]],
        func_or_arg_or_args: Union[
            Func[
                Unpack[OtherArgsT],
                Unpack[AnotherArgsT],
                ReturnT,
            ],
            Var[ArgT],
            Seq[Unpack[AnotherArgsT]],
            Callable[
                # [Unpack, Unpack]
                # The pyright indicates an error,
                # but the type inference is carried out normally.
                [Unpack[OtherArgsT], Unpack[AnotherArgsT]],  # type: ignore
                ReturnT,
            ],
        ],
    ) -> Union[
        Func[Unpack[AnotherArgsT], ReturnT],
        Seq[Unpack[OtherArgsT], ArgT],
        Seq[Unpack[OtherArgsT], Unpack[AnotherArgsT]],
    ]:
        ...

    def __mul__(
        self: Seq[Unpack[OtherArgsT]],
        func_or_arg_or_args: Union[
            Func[
                Unpack[OtherArgsT],
                Unpack[AnotherArgsT],
                ReturnT,
            ],
            Var[ArgT],
            Seq[Unpack[AnotherArgsT]],
            Callable[
                # [Unpack, Unpack]
                # The pyright indicates an error,
                # but the type inference is carried out normally.
                [Unpack[OtherArgsT], Unpack[AnotherArgsT]],  # type: ignore
                ReturnT,
            ],
        ],
    ) -> Union[
        Func[Unpack[AnotherArgsT], ReturnT],
        Seq[Unpack[OtherArgsT], ArgT],
        Seq[Unpack[OtherArgsT], Unpack[AnotherArgsT]],
    ]:
        if isinstance(func_or_arg_or_args, Func):
            return func_or_arg_or_args * self
        if isinstance(func_or_arg_or_args, Var):
            return func_or_arg_or_args.__rmul__(self)
        if isinstance(func_or_arg_or_args, Seq):
            return Seq(
                self.value.map2(func_or_arg_or_args.value, _iter_unpack_tuples_0),
            )
        if callable(func_or_arg_or_args):
            # [Unpack, Unpack]
            # The pyright indicates an error,
            # but the type inference is carried out normally.
            return self * func(func_or_arg_or_args)  # type: ignore
        raise NotImplementedError

    @overload
    def __rmul__(
        self: Seq[Unpack[OtherArgsT]],
        func_or_arg_or_args: Union[
            Callable[
                # [Unpack, Unpack]
                # The pyright indicates an error,
                # but the type inference is carried out normally.
                [Unpack[OtherArgsT], Unpack[AnotherArgsT]],  # type: ignore
                ReturnT,
            ],
            Func[Unpack[OtherArgsT], Unpack[AnotherArgsT], ReturnT],
        ],
    ) -> Func[Unpack[AnotherArgsT], ReturnT]:
        ...

    @overload
    def __rmul__(
        self: Seq[Unpack[OtherArgsT]],
        func_or_arg_or_args: Var[ArgT],
    ) -> Seq[ArgT, Unpack[OtherArgsT]]:
        ...

    @overload
    def __rmul__(
        self: Seq[Unpack[OtherArgsT]],
        func_or_arg_or_args: Seq[Unpack[AnotherArgsT]],
    ) -> Seq[Unpack[AnotherArgsT], Unpack[OtherArgsT]]:
        ...

    @overload
    def __rmul__(
        self: Seq[Unpack[OtherArgsT]],
        func_or_arg_or_args: Union[
            Func[Unpack[OtherArgsT], Unpack[AnotherArgsT], ReturnT],
            Var[ArgT],
            Seq[Unpack[AnotherArgsT]],
            Callable[
                # [Unpack, Unpack]
                # The pyright indicates an error,
                # but the type inference is carried out normally.
                [Unpack[OtherArgsT], Unpack[AnotherArgsT]],  # type: ignore
                ReturnT,
            ],
        ],
    ) -> Union[
        Func[Unpack[AnotherArgsT], ReturnT],
        Seq[ArgT, Unpack[OtherArgsT]],
        Seq[Unpack[AnotherArgsT], Unpack[OtherArgsT]],
    ]:
        ...

    def __rmul__(
        self: Seq[Unpack[OtherArgsT]],
        func_or_arg_or_args: Union[
            Func[Unpack[OtherArgsT], Unpack[AnotherArgsT], ReturnT],
            Var[ArgT],
            Seq[Unpack[AnotherArgsT]],
            Callable[
                # [Unpack, Unpack]
                # The pyright indicates an error,
                # but the type inference is carried out normally.
                [Unpack[OtherArgsT], Unpack[AnotherArgsT]],  # type: ignore
                ReturnT,
            ],
        ],
    ) -> Union[
        Func[Unpack[AnotherArgsT], ReturnT],
        Seq[ArgT, Unpack[OtherArgsT]],
        Seq[Unpack[AnotherArgsT], Unpack[OtherArgsT]],
    ]:
        if isinstance(func_or_arg_or_args, Func):
            return func_or_arg_or_args * self
        if isinstance(func_or_arg_or_args, Var):
            return func_or_arg_or_args.__mul__(self)
        if isinstance(func_or_arg_or_args, Seq):
            return Seq(
                self.value.map2(func_or_arg_or_args.value, _iter_unpack_tuples_1),
            )
        if callable(func_or_arg_or_args):
            # [Unpack, Unpack]
            # The pyright indicates an error,
            # but the type inference is carried out normally.
            return func(func_or_arg_or_args) * self  # type: ignore
        raise NotImplementedError


class Func(
    Apply[Callable[[Unpack[ArgsT]], ReturnT]],
    Generic[Unpack[ArgsT], ReturnT],
):
    """a function(without keyword parameters) wrapped as Result for use to apply

    Example:
        >>> from typing import Any
        >>> from expression import Ok, Result
        >>> from expression.extra.result.apply import Seq, Func, call
        >>>
        >>>
        >>> def func(a: int, b: int, c: str) -> tuple[int, str]:
        >>>     return (a + b, c)
        >>>
        >>>
        >>> wrapped_func = Func(Ok(func))
        >>> values: tuple[int, int, str] = (1, 1, "q")
        >>> some_value: Result[tuple[int, int, str], Any] = Ok(values)
        >>> wrapped: Seq[int, int, str] = Seq(some_value)
        >>>
        >>> new_func: Func[tuple[int, str]] = wrapped_func * wrapped
        >>> assert new_func * call == Ok(func(*values))
    """

    @overload
    def __mul__(
        self: Func[OtherReturnT],
        caller_or_arg_or_args: Union[type[Call], Call],
    ) -> Result[OtherReturnT, Any]:
        ...

    @overload
    def __mul__(
        self: Func[ArgT, Unpack[OtherArgsT], OtherReturnT],
        caller_or_arg_or_args: Var[ArgT],
    ) -> Func[Unpack[OtherArgsT], OtherReturnT]:
        ...

    @overload
    def __mul__(
        self: Func[Unpack[OtherArgsT], Unpack[AnotherArgsT], OtherReturnT],
        caller_or_arg_or_args: Seq[Unpack[OtherArgsT]],
    ) -> Func[Unpack[AnotherArgsT], OtherReturnT]:
        ...

    @overload
    def __mul__(
        self: Union[
            Func[OtherReturnT],
            Func[ArgT, Unpack[OtherArgsT], OtherReturnT],
            Func[Unpack[OtherArgsT], Unpack[AnotherArgsT], OtherReturnT],
        ],
        caller_or_arg_or_args: Union[
            type[Call], Call, Var[ArgT], Seq[Unpack[OtherArgsT]]
        ],
    ) -> Union[
        Result[OtherReturnT, Any],
        Func[Unpack[OtherArgsT], OtherReturnT],
        Func[Unpack[AnotherArgsT], OtherReturnT],
    ]:
        ...

    # FIXME: error in pyright. but it works.
    def __mul__(  # type: ignore
        self: Union[
            Func[OtherReturnT],
            Func[ArgT, Unpack[OtherArgsT], OtherReturnT],
            Func[Unpack[OtherArgsT], Unpack[AnotherArgsT], OtherReturnT],
        ],
        caller_or_arg_or_args: Union[
            type[Call], Call, Var[ArgT], Seq[Unpack[OtherArgsT]]
        ],
    ) -> Union[
        Result[OtherReturnT, Any],
        Func[Unpack[OtherArgsT], OtherReturnT],
        Func[Unpack[AnotherArgsT], OtherReturnT],
    ]:
        if isinstance(caller_or_arg_or_args, Call):
            _self = cast("Func[OtherReturnT]", self)
            return caller_or_arg_or_args * _self
        if isinstance(caller_or_arg_or_args, Var):
            _self = cast(
                "Func[ArgT, Unpack[OtherArgsT], OtherReturnT]",
                self,
            )
            return Func(
                _self.value.map2(caller_or_arg_or_args.value, _partial_0),
            )
        if isinstance(caller_or_arg_or_args, Seq):
            _self = cast(
                "Func[Unpack[OtherArgsT], Unpack[AnotherArgsT], OtherReturnT]",
                self,
            )
            return Func(
                _self.value.map2(
                    caller_or_arg_or_args.value,
                    # An error occurred in the pylance using more than one Unpack.
                    # but the type inference is carried out normally.
                    _partial_1,  # type: ignore
                ),
            )
        if isclass(caller_or_arg_or_args) and issubclass(
            caller_or_arg_or_args,
            Call,
        ):
            _self = cast("Func[OtherReturnT]", self)
            return caller_or_arg_or_args() * _self
        raise NotImplementedError

    __rmul__ = __mul__


class Call:
    """call magic method '__call__' of wrapped function"""

    def __mul__(self, func: Func[ReturnT]) -> Result[ReturnT, Any]:
        return func.value.map(_safe).bind(_call)


@overload
def func(f: Callable[[Unpack[ArgsT]], ReturnT]) -> Func[Unpack[ArgsT], ReturnT]:
    ...


@overload
def func(
    f: Result[Callable[[Unpack[ArgsT]], ReturnT], Any]
) -> Func[Unpack[ArgsT], ReturnT]:
    ...


def func(
    f: Union[
        Callable[[Unpack[ArgsT]], ReturnT],
        Result[Callable[[Unpack[ArgsT]], ReturnT], Any],
    ]
) -> Func[Unpack[ArgsT], ReturnT]:
    if isinstance(f, Ok | Error):
        return Func(f)
    return Func(Ok(f))


@overload
def of_obj(value: Result[ValueT, Any]) -> Var[ValueT]:
    ...


@overload
def of_obj(value: ArgT) -> Var[ArgT]:
    ...


def of_obj(value: Union[ArgT, Result[ValueT, Any]]) -> Union[Var[ArgT], Var[ValueT]]:
    if isinstance(value, Ok | Error):
        return Var(cast("Result[ValueT, Any]", value))
    return Var(Ok(value))


def of_iterable(*values: Unpack[ArgsT]) -> Seq[Unpack[ArgsT]]:
    return Seq(Ok(values))


def _safe(func: Callable[[], ReturnT]) -> Callable[[], Result[ReturnT, Exception]]:
    def inner() -> Result[ReturnT, Exception]:
        try:
            result = func()
        except Exception as exc:
            return Error(exc)
        return Ok(result)

    return inner


@overload
def _iter_tuple_0(value: ArgT, other_value: OtherArgT) -> tuple[ArgT, OtherArgT]:
    ...


@overload
def _iter_tuple_0(
    value: ArgT, other_value: OtherArgT, *values: Unpack[ArgsT]
) -> tuple[ArgT, OtherArgT, Unpack[ArgsT]]:
    ...


def _iter_tuple_0(
    value: ArgT, other_value: OtherArgT, *values: Unpack[ArgsT]
) -> Union[tuple[ArgT, OtherArgT], tuple[ArgT, OtherArgT, Unpack[ArgsT]]]:
    return (value, other_value, *values)


def _iter_unpack_tuple_0(
    value: ArgT,
    other: tuple[Unpack[ArgsT]],
) -> tuple[ArgT, Unpack[ArgsT]]:
    return (value, *other)


def _iter_unpack_tuples_0(
    value: tuple[Unpack[ArgsT]],
    other: tuple[Unpack[OtherArgsT]],
    # [Unpack, Unpack]
    # The pyright indicates an error, but the type inference is carried out normally.
) -> tuple[Unpack[ArgsT], Unpack[OtherArgsT]]:  # type: ignore
    return (*value, *other)


@overload
def _iter_tuple_1(value: ArgT, other_value: OtherArgT) -> tuple[OtherArgT, ArgT]:
    ...


@overload
def _iter_tuple_1(
    value: ArgT, other_value: OtherArgT, *values: Unpack[ArgsT]
) -> tuple[OtherArgT, Unpack[ArgsT], ArgT]:
    ...


def _iter_tuple_1(
    value: ArgT, other_value: OtherArgT, *values: Unpack[ArgsT]
) -> tuple[OtherArgT, ArgT] | tuple[OtherArgT, Unpack[ArgsT], ArgT]:
    return (other_value, *values, value)


def _iter_unpack_tuple_1(
    value: ArgT,
    other: tuple[Unpack[ArgsT]],
) -> tuple[Unpack[ArgsT], ArgT]:
    return (*other, value)


def _iter_unpack_tuples_1(
    value: tuple[Unpack[ArgsT]],
    other: tuple[Unpack[OtherArgsT]],
    # [Unpack, Unpack]
    # The pyright indicates an error, but the type inference is carried out normally.
) -> tuple[Unpack[OtherArgsT], Unpack[ArgsT]]:  # type: ignore
    return (*other, *value)


def _partial_0(
    func: Callable[[ArgT, Unpack[ArgsT]], ReturnT],
    arg: ArgT,
) -> Callable[[Unpack[ArgsT]], ReturnT]:
    return partial(func, arg)


def _partial_1(
    # [Unpack, Unpack]
    # The pyright indicates an error, but the type inference is carried out normally.
    func: Callable[[Unpack[OtherArgsT], Unpack[AnotherArgsT]], ReturnT],  # type: ignore
    args: tuple[Unpack[OtherArgsT]],
) -> Callable[[Unpack[AnotherArgsT]], ReturnT]:
    return partial(func, *args)


_call = methodcaller("__call__")
call = Call()
