"""Option module.

Contains a collection of static methods (functions) for operating on
options. All functions takes the source as the last curried argument,
i.e all functions returns a function that takes the source sequence as
the only argument.
"""

from __future__ import annotations

import builtins
from collections.abc import Callable, Generator, Iterable
from typing import TYPE_CHECKING, Any, Literal, TypeGuard, TypeVar, cast, get_args, get_origin

from typing_extensions import TypeVarTuple, Unpack

from .curry import curry_flip
from .error import EffectError
from .pipe import PipeMixin
from .tagged_union import case, tag, tagged_union


if TYPE_CHECKING:
    # The following imports are only used for type checking and will be lazy imported.
    from pydantic import GetCoreSchemaHandler
    from pydantic_core import CoreSchema

    from expression.collections.seq import Seq
    from expression.core.result import Result


_TSourceOut = TypeVar("_TSourceOut", covariant=True)
_TSource = TypeVar("_TSource")
_TResult = TypeVar("_TResult")
_TError = TypeVar("_TError")

_T1 = TypeVar("_T1")
_T2 = TypeVar("_T2")
_P = TypeVarTuple("_P")


@tagged_union(frozen=True, order=True)
class Option(
    Iterable[_TSourceOut],
    PipeMixin,
):
    """Option class."""

    tag: Literal["some", "none"] = tag()

    none: None = case()
    some: _TSourceOut = case()

    @staticmethod
    def Some(value: _TResult) -> Option[_TResult]:
        """Create a Some option."""
        return Option(some=value)

    @staticmethod
    def Nothing() -> Option[_TSourceOut]:
        """Create a None option."""
        return Option(none=None)

    def default_value(self, value: _TSource) -> _TSourceOut | _TSource:
        """Get with default value.

        Gets the value of the option if the option is Some, otherwise
        returns the specified default value.
        """
        match self:
            case Option(tag="some", some=some):
                return some
            case _:
                return value

    def default_with(self, getter: Callable[[], _TSource]) -> _TSourceOut | _TSource:
        """Get with default value lazily.

        Gets the value of the option if the option is Some, otherwise
        returns the value produced by the getter
        """
        match self:
            case Option(tag="some", some=some):
                return some
            case _:
                return getter()

    def map(self, mapper: Callable[[_TSourceOut], _TResult]) -> Option[_TResult]:
        """Map option.

        Applies the mapper to the value if the option is Some, otherwise
        returns `Nothing`.
        """
        match self:
            case Option(tag="some", some=some):
                return Some(mapper(some))
            case _:
                return Nothing

    def map2(self, mapper: Callable[[_TSourceOut, _T2], _TResult], other: Option[_T2]) -> Option[_TResult]:
        """Map2 option.

        Applies the mapper to the values if both options are Some,
        otherwise returns `Nothing`.
        """
        match self, other:
            case Option(tag="some", some=some), Option(tag="some", some=other_value):
                return Some(mapper(some, other_value))
            case _:
                return Nothing

    def starmap(self: Option[tuple[Unpack[_P]]], mapper: Callable[[Unpack[_P]], _TResult]) -> Option[_TResult]:
        """Starmap option.

        Applies the mapper to the values if the option is Some,
        otherwise returns `Nothing`. The tuple is unpacked before
        applying the mapper.
        """
        match self:
            case Option(tag="some", some=some):
                return Some(mapper(*some))
            case _:
                return Nothing

    def bind(self, mapper: Callable[[_TSourceOut], Option[_TResult]]) -> Option[_TResult]:
        """Bind option.

        Applies and returns the result of the mapper if the value is
        `Some`. If the value is `Nothing` then `Nothing` is returned.

        Args:
            mapper: A function that takes the value of type TSource from
                an option and transforms it into an option containing a
                value of type TResult.

        Returns:
            An option of the output type of the mapper.
        """
        match self:
            case Option(tag="some", some=some):
                return mapper(some)
            case _:
                return Nothing

    def or_else(self, if_none: Option[_TSourceOut]) -> Option[_TSourceOut]:
        """Returns option if it is Some, otherwise returns `if_one`."""
        match self:
            case Option(tag="some"):
                return self
            case _:
                return if_none

    def or_else_with(self, if_none: Callable[[], Option[_TSourceOut]]) -> Option[_TSourceOut]:
        """Or-else-with.

        Returns option if it is Some,
        otherwise evaluates the given function and returns the result.
        """
        match self:
            case Option(tag="some"):
                return self
            case _:
                return if_none()

    def filter(self, predicate: Callable[[_TSourceOut], bool]) -> Option[_TSourceOut]:
        """Filter option.

        Returns the input if the predicate evaluates to true, otherwise
        returns `Nothing`.
        """
        match self:
            case Option(tag="some", some=some) if predicate(some):
                return self
            case _:
                return Nothing

    def to_list(self) -> list[_TSourceOut]:
        """Convert option to list."""
        match self:
            case Option(tag="some", some=some):
                return [some]
            case _:
                return []

    def to_seq(self) -> Seq[_TSourceOut]:
        """Convert option to sequence."""
        # deferred import to avoid circular dependencies
        from expression.collections.seq import Seq

        match self:
            case Option(tag="some", some=some):
                return Seq[_TSourceOut].of(some)
            case _:
                return Seq()

    def is_some(self) -> bool:
        """Returns true if the option is not Nothing."""
        match self:
            case Option(tag="some"):
                return True
            case _:
                return False

    def is_none(self) -> bool:
        """Returns true if the option is Nothing."""
        match self:
            case Option(tag="some"):
                return False
            case _:
                return True

    @staticmethod
    def of_obj(value: _TSource) -> Option[_TSource]:
        """Convert object to an option."""
        return of_optional(value)

    @staticmethod
    def of_optional(value: _TSource | None) -> Option[_TSource]:
        """Convert optional value to an option."""
        return of_optional(value)

    @staticmethod
    def of_result(result: Result[_TSource, Any]) -> Option[_TSource]:
        """Convert result to an option."""
        return of_result(result)

    def to_optional(self) -> _TSourceOut | None:
        """Convert option to an optional."""
        match self:
            case Option(tag="some", some=some):
                return some
            case _:
                return None

    def to_result(self, error: _TError) -> Result[_TSourceOut, _TError]:
        """Convert option to a result."""
        from expression.core.result import Result

        match self:
            case Option(tag="some", some=some):
                return Result(ok=some)
            case _:
                return Result(error=error)

    def to_result_with(self, error: Callable[[], _TError]) -> Result[_TSourceOut, _TError]:
        """Convert option to a result."""
        from expression.core.result import Result

        match self:
            case Option(tag="some", some=some):
                return Result(ok=some)
            case _:
                return Result(error=error())

    def dict(self) -> _TSourceOut | None:
        """Returns a json string representation of the option."""
        match self:
            case Option(tag="some", some=value):
                attr = getattr(value, "model_dump", None) or getattr(value, "dict", None)
                if attr and callable(attr):
                    value = cast(_TSourceOut, attr())

                return value
            case _:
                return None

    @property
    def value(self) -> _TSourceOut:
        """Returns the value wrapped by the option.

        A `ValueError` is raised if the option is `Nothing`.
        """
        match self:
            case Option(tag="some", some=some):
                return some
            case _:
                raise ValueError("There is no value.")

    def __eq__(self, o: Any) -> bool:
        return isinstance(o, Option) and self.tag == o.tag and getattr(self, self.tag) == getattr(o, self.tag)  # type: ignore

    def __iter__(self) -> Generator[_TSourceOut, _TSourceOut, _TSourceOut]:
        match self:
            case Option(tag="some", some=value):
                return (yield value)
            case _:
                raise EffectError(Nothing)

    def __str__(self) -> str:
        match self:
            case Option(tag="some", some=some):
                return f"Some {some}"
            case _:
                return "Nothing"

    def __repr__(self) -> str:
        return self.__str__()

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: GetCoreSchemaHandler) -> CoreSchema:
        from pydantic import ValidatorFunctionWrapHandler
        from pydantic_core import core_schema

        origin = get_origin(source_type)
        if origin is None:  # used as `x: Owner` without params
            origin = source_type
            item_tp = Any
        else:
            item_tp = get_args(source_type)[0]

        value_schema = handler.generate_schema(item_tp)
        none_schema = handler.generate_schema(None)

        def validate_some(v: Any, handler: ValidatorFunctionWrapHandler) -> Option[Any]:
            value = handler(v)
            return Some(value)

        def validate_none(v: Any, handler: ValidatorFunctionWrapHandler) -> Option[Any]:
            _ = handler(v)
            return Nothing

        python_schema = core_schema.union_schema(
            [
                core_schema.is_instance_schema(Option),
                core_schema.chain_schema(
                    [
                        core_schema.none_schema(),
                        core_schema.no_info_wrap_validator_function(validate_none, none_schema),
                    ]
                ),
                core_schema.chain_schema(
                    [
                        # item_tp's schema should ensure the value is an instance of _T
                        # is_instance_schema doesn't work for Annotated[_T, ...]
                        # Use the value_schema to validate `values`
                        core_schema.no_info_wrap_validator_function(validate_some, value_schema),
                    ]
                ),
            ]
        )

        return core_schema.json_or_python_schema(
            json_schema=core_schema.chain_schema(
                [
                    core_schema.any_schema(),
                    # after validating the json data convert it to python
                    core_schema.no_info_before_validator_function(
                        lambda data: cls(some=data) if data is not None else cls(none=data),
                        python_schema,
                    ),
                ]
            ),
            python_schema=python_schema,
            serialization=core_schema.plain_serializer_function_ser_schema(lambda instance: instance.dict()),
        )


# # The singleton None class. We use the name 'Nothing' here instead of `None` to
# # avoid conflicts with the builtin `None` value in Python.
# TODO: also allow None here?
Nothing: Option[Any] = Option[Any].Nothing()
"""Singleton `Nothing` object.

Since Nothing is a singleton it can be tested e.g using `is`:
    >>> if xs is Nothing:
    ...     return True
"""


def Some(value: _T1) -> Option[_T1]:
    """Create a Some option."""
    return Option[_T1].Some(value)


@curry_flip(1)
def bind(option: Option[_TSource], mapper: Callable[[_TSource], Option[_TResult]]) -> Option[_TResult]:
    """Bind option.

    Applies and returns the result of the mapper if the value is
    `Some`. If the value is `Nothing` then `Nothing` is returned.

    Args:
        option: Source option to bind.
        mapper: A function that takes the value of type _TSource from
            an option and transforms it into an option containing a
            value of type TResult.

    Returns:
        A partially applied function that takes an option and returns an
        option of the output type of the mapper.
    """
    return option.bind(mapper)


@curry_flip(1)
def default_value(option: Option[_TSource], value: _T1) -> _TSource | _T1:
    """Get value or default value.

    Gets the value of the option if the option is Some, otherwise
    returns the specified default value.
    """
    return option.default_value(value)


def default_with(getter: Callable[[], _TSource]) -> Callable[[Option[_TSource]], _TSource]:
    """Get with default value lazily.

    Gets the value of the option if the option is Some, otherwise
    returns the value produced by the getter
    """

    def _default_with(option: Option[_TSource]) -> _TSource:
        return option.default_with(getter)

    return _default_with


def is_none(option: Option[_TSource]) -> TypeGuard[Option[_TSource]]:
    return option.is_none()


def is_some(option: Option[_TSource]) -> TypeGuard[Option[_TSource]]:
    return option.is_some()


@curry_flip(1)
def map(option: Option[_TSource], mapper: Callable[[_TSource], _TResult]) -> Option[_TResult]:
    return option.map(mapper)


@curry_flip(2)
def map2(opt1: Option[_T1], opt2: Option[_T2], mapper: Callable[[_T1, _T2], _TResult]) -> Option[_TResult]:
    return opt1.map2(mapper, opt2)


@curry_flip(1)
def starmap(option: Option[tuple[Unpack[_P]]], mapper: Callable[[*_P], _TResult]) -> Option[_TResult]:
    return option.starmap(mapper)


def or_else(
    option: Option[_TSource],
    if_none: Option[_TSource],
) -> Option[_TSource]:
    """Returns option if it is Some, otherwise returns `if_none`."""
    return option.or_else(if_none)


def to_list(option: Option[_TSource]) -> list[_TSource]:
    return option.to_list()


def to_seq(option: Option[_TSource]) -> Seq[_TSource]:
    return option.to_seq()


def to_optional(value: Option[_TSource]) -> _TSource | None:
    """Convert an option value to an optional.

    Args:
        value: The input option value.

    Return:
        The result optional.
    """
    return value.to_optional()


def of_optional(value: _TSource | None) -> Option[_TSource]:
    """Convert an optional value to an option.

    Args:
        value: The input optional value.

    Return:
        The result option.
    """
    if value is None:
        return Nothing

    return Some(value)


def of_obj(value: Any) -> Option[Any]:
    """Convert object to an option.

    Convert a value that could be `None` into an `Option` value.

    Args:
        value: The input object.

    Return:
        The result option.
    """
    return of_optional(value)


def of_result(result: Result[_TSource, Any]) -> Option[_TSource]:
    from expression.core.result import Result

    match result:
        case Result(tag="ok", ok=value):
            return Some(value)
        case _:
            return Nothing


def to_result(value: Option[_TSource], error: _TError) -> Result[_TSource, _TError]:
    return value.to_result(error)


def to_result_with(value: Option[_TSource], error: Callable[[], _TError]) -> Result[_TSource, _TError]:
    return value.to_result_with(error)


def model_dump(value: Option[_TSource]) -> _TSource | builtins.dict[Any, Any] | None:
    return value.dict()


def default_arg(value: Option[_TSource], default_value: _T1) -> _TSource | _T1:
    """Specify default argument.

    Used to specify a default value for an optional argument in the
    implementation of a function. Same as `default_value`, but
    "uncurried" and with the arguments swapped.
    """
    return value.default_value(default_value)


__all__ = [
    "Nothing",
    "Option",
    "Some",
    "bind",
    "default_arg",
    "default_value",
    "default_with",
    "is_none",
    "is_some",
    "map",
    "map2",
    "model_dump",
    "of_obj",
    "of_optional",
    "of_result",
    "or_else",
    "to_list",
    "to_optional",
    "to_result",
    "to_seq",
]
