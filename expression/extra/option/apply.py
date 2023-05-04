from __future__ import annotations

from collections.abc import Callable
from functools import partial
from inspect import isclass
from typing import TYPE_CHECKING, Generic, TypeVar, Union, cast, overload

from typing_extensions import TypeVarTuple, Unpack

from expression.core.option import Nothing, Some

if TYPE_CHECKING:
    from expression.core.option import Option

ArgT = TypeVar("ArgT")
OtherArgT = TypeVar("OtherArgT")
ValueT = TypeVar("ValueT")
ReturnT = TypeVar("ReturnT")
OtherReturnT = TypeVar("OtherReturnT")
ArgsT = TypeVarTuple("ArgsT")
OtherArgsT = TypeVarTuple("OtherArgsT")
AnotherArgsT = TypeVarTuple("AnotherArgsT")

__all__ = [
    "Var",
    "Seq",
    "Func",
    "Call",
    "func",
    "optional_func",
    "of_obj",
    "of_optional",
    "of_iterable",
    "call",
]


class Apply(Generic[ValueT]):
    def __init__(self, value: Option[ValueT]) -> None:
        self._value = value

    @property
    def value(self) -> Option[ValueT]:
        return self._value

    def __repr__(self) -> str:
        name = type(self).__name__
        return f"<{name}: {repr(self.value)}>"


class Var(Apply[ValueT], Generic[ValueT]):
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
                self.value.map2(
                    _iter_tuple_0,
                    func_or_arg_or_args.value,  # type: ignore
                ),
            )
        if isinstance(func_or_arg_or_args, Seq):
            return Seq(
                self.value.map2(_iter_unpack_tuple_0, func_or_arg_or_args.value),
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

    def __rmul__(  # type: ignore
        self: Var[ArgT],
        func_or_arg_or_args: Union[
            Func[ArgT, Unpack[ArgsT], ReturnT],
            Seq[Unpack[ArgsT]],
            Var[OtherArgT],
            Callable[[ArgT, Unpack[ArgsT]], ReturnT],
        ],
    ) -> Union[
        Func[Unpack[ArgsT], ReturnT],
        Seq[Unpack[ArgsT], ArgT],
        Seq[OtherArgT, ArgT],
        Func[Unpack[ArgsT], ReturnT],
    ]:
        if isinstance(func_or_arg_or_args, Func):
            return func_or_arg_or_args * self
        if isinstance(func_or_arg_or_args, Var):
            return Seq(
                self.value.map2(
                    _iter_tuple_1,
                    func_or_arg_or_args.value,  # type: ignore
                ),
            )
        if isinstance(func_or_arg_or_args, Seq):
            return Seq(
                self.value.map2(_iter_unpack_tuple_1, func_or_arg_or_args.value),
            )
        if callable(func_or_arg_or_args):
            return func(func_or_arg_or_args) * self
        raise NotImplementedError


class Seq(Apply[tuple[Unpack[ArgsT]]], Generic[Unpack[ArgsT]]):
    @overload
    def __mul__(
        self: Seq[Unpack[OtherArgsT]],
        func_or_arg_or_args: Union[
            Callable[
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
            return func_or_arg_or_args * self  # type: ignore
        if isinstance(func_or_arg_or_args, Var):
            return func_or_arg_or_args.__rmul__(self)
        if isinstance(func_or_arg_or_args, Seq):
            return Seq(
                self.value.map2(_iter_unpack_tuples_0, func_or_arg_or_args.value),
            )
        if callable(func_or_arg_or_args):
            return self * func(func_or_arg_or_args)
        raise NotImplementedError

    @overload
    def __rmul__(
        self: Seq[Unpack[OtherArgsT]],
        func_or_arg_or_args: Union[
            Callable[
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
            Func[
                Unpack[OtherArgsT],
                Unpack[AnotherArgsT],
                ReturnT,
            ],
            Var[ArgT],
            Seq[Unpack[AnotherArgsT]],
            Callable[
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
            Func[
                Unpack[OtherArgsT],
                Unpack[AnotherArgsT],
                ReturnT,
            ],
            Var[ArgT],
            Seq[Unpack[AnotherArgsT]],
            Callable[
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
                self.value.map2(_iter_unpack_tuples_1, func_or_arg_or_args.value),
            )
        if callable(func_or_arg_or_args):
            return func(func_or_arg_or_args) * self
        raise NotImplementedError


class Func(
    Apply[Callable[[Unpack[ArgsT]], ReturnT]],
    Generic[Unpack[ArgsT], ReturnT],
):
    @overload
    def __mul__(
        self: Func[OtherReturnT],
        caller_or_arg_or_args: Union[type[Call], Call],
    ) -> Option[OtherReturnT]:
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
        Option[OtherReturnT],
        Func[Unpack[OtherArgsT], OtherReturnT],
        Func[Unpack[AnotherArgsT], OtherReturnT],
    ]:
        ...

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
        Option[OtherReturnT],
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
                _self.value.map2(_partial_0, caller_or_arg_or_args.value),
            )
        if isinstance(caller_or_arg_or_args, Seq):
            _self = cast(
                "Func[Unpack[OtherArgsT], Unpack[AnotherArgsT], OtherReturnT]",
                self,
            )
            return Func(
                _self.value.map2(
                    _partial_1,  # type: ignore
                    caller_or_arg_or_args.value,
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
    def __mul__(self, func: Func[ReturnT]) -> Option[ReturnT]:
        if func.value is Nothing:
            return Nothing
        return Some(func.value.value())


def func(f: Callable[[Unpack[ArgsT]], ReturnT]) -> Func[Unpack[ArgsT], ReturnT]:
    return Func(Some(f))


def optional_func(
    f: Option[Callable[[Unpack[ArgsT]], ReturnT]]
) -> Func[Unpack[ArgsT], ReturnT]:
    return Func(f)


def of_obj(value: ValueT) -> Var[ValueT]:
    return Var(Some(value))


def of_optional(value: Option[ValueT]) -> Var[ValueT]:
    return Var(value)


def of_iterable(*values: Unpack[ArgsT]) -> Seq[Unpack[ArgsT]]:
    return Seq(Some(values))


def _iter_tuple_0(value: ArgT, *values: Unpack[ArgsT]) -> tuple[ArgT, Unpack[ArgsT]]:
    return (value, *values)


def _iter_unpack_tuple_0(
    value: ArgT,
    other: tuple[Unpack[ArgsT]],
) -> tuple[ArgT, Unpack[ArgsT]]:
    return (value, *other)


def _iter_unpack_tuples_0(
    value: tuple[Unpack[ArgsT]],
    other: tuple[Unpack[OtherArgsT]],
) -> tuple[Unpack[ArgsT], Unpack[OtherArgsT]]:  # type: ignore
    return (*value, *other)


def _iter_tuple_1(value: ArgT, *values: Unpack[ArgsT]) -> tuple[Unpack[ArgsT], ArgT]:
    return (*values, value)


def _iter_unpack_tuple_1(
    value: ArgT,
    other: tuple[Unpack[ArgsT]],
) -> tuple[Unpack[ArgsT], ArgT]:
    return (*other, value)


def _iter_unpack_tuples_1(
    value: tuple[Unpack[ArgsT]],
    other: tuple[Unpack[OtherArgsT]],
) -> tuple[Unpack[OtherArgsT], Unpack[ArgsT]]:  # type: ignore
    return (*other, *value)


def _partial_0(
    func: Callable[[ArgT, Unpack[ArgsT]], ReturnT],
    arg: ArgT,
) -> Callable[[Unpack[ArgsT]], ReturnT]:
    return partial(func, arg)


def _partial_1(
    func: Callable[[Unpack[OtherArgsT], Unpack[AnotherArgsT]], ReturnT],  # type: ignore
    args: tuple[Unpack[OtherArgsT]],
) -> Callable[[Unpack[AnotherArgsT]], ReturnT]:
    return partial(func, *args)


call = Call()
