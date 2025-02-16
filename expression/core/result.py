"""Result module.

The Result[TSource,TError] type lets you write error-tolerant code that
can be composed. The Result type is typically used in monadic
error-handling, which is often referred to as Railway-oriented
Programming.

There is also a simplified alias of this type called `Try` that pins
the Result type to Exception.
"""

from __future__ import annotations

import builtins
from collections.abc import Callable, Generator, Iterable
from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    Literal,
    TypeGuard,
    TypeVar,
    cast,
    get_args,
    get_origin,
)


if TYPE_CHECKING:
    from pydantic import GetCoreSchemaHandler
    from pydantic_core import CoreSchema

    from expression.core.option import Option

from .curry import curry_flip
from .error import EffectError
from .pipe import PipeMixin
from .tagged_union import case, tag, tagged_union


_TSource = TypeVar("_TSource")
_TSourceOut = TypeVar("_TSourceOut", covariant=True)
_TOther = TypeVar("_TOther")
_TResult = TypeVar("_TResult")
_TError = TypeVar("_TError")
_TErrorOut = TypeVar("_TErrorOut", covariant=True)


@tagged_union(frozen=True, order=True)
class Result(
    Iterable[_TSourceOut],
    PipeMixin,
    Generic[_TSourceOut, _TErrorOut],
):
    """The result class."""

    tag: Literal["ok", "error"] = tag()

    ok: _TSourceOut = case()
    error: _TErrorOut = case()

    @staticmethod
    def Ok(value: _TResult) -> Result[_TResult, _TErrorOut]:
        """Create a new Ok result."""
        return Result(tag="ok", ok=value)

    @staticmethod
    def Error(error: _TError) -> Result[_TSourceOut, _TError]:
        """Create a new Error result."""
        return Result(tag="error", error=error)

    def default_value(self, value: _TSource) -> _TSourceOut | _TSource:
        """Get with default value.

        Gets the value of the result if the result is Ok, otherwise
        returns the specified default value.
        """
        match self:
            case Result(tag="ok", ok=ok):
                return ok
            case _:
                return value

    def default_with(self, getter: Callable[[_TErrorOut], _TSource]) -> _TSource | _TSourceOut:
        """Get with default value lazily.

        Gets the value of the result if the result is Ok, otherwise
        returns the value produced by the getter
        """
        match self:
            case Result(tag="ok", ok=value):
                return value
            case Result(error=error):
                return getter(error)

    def map(self, mapper: Callable[[_TSourceOut], _TResult]) -> Result[_TResult, _TErrorOut]:
        """Map result.

        Return a result of the value after applying the mapping
        function, or Error if the input is Error.
        """
        match self:
            case Result(tag="ok", ok=value):
                return Result[_TResult, _TErrorOut].Ok(mapper(value))
            case Result(error=error):
                return Result[_TResult, _TErrorOut].Error(error)

    def map2(
        self,
        other: Result[_TOther, _TErrorOut],
        mapper: Callable[[_TSourceOut, _TOther], _TResult],
    ) -> Result[_TResult, _TErrorOut]:
        """Map result.

        Return a result of the value after applying the mapping
        function, or Error if the input is Error.
        """
        match self:
            case Result(tag="ok", ok=value):
                return other.map(lambda value_: mapper(value, value_))
            case Result(error=error):
                return Result(error=error)

    def map_error(self, mapper: Callable[[_TErrorOut], _TResult]) -> Result[_TSourceOut, _TResult]:
        """Map error.

        Return a result of the error value after applying the mapping
        function, or Ok if the input is Ok.
        """
        match self:
            case Result(tag="ok", ok=value):
                return Result[_TSourceOut, _TResult].Ok(value)
            case Result(error=error):
                return Result[_TSourceOut, _TResult].Error(mapper(error))

    def bind(self, mapper: Callable[[_TSourceOut], Result[_TResult, _TErrorOut]]) -> Result[_TResult, _TErrorOut]:
        """Bind result.

        Return a result of the value after applying the mapping
        function, or Error if the input is Error.
        """
        match self:
            case Result(tag="ok", ok=value):
                return mapper(value)
            case Result(error=error):
                return Result[_TResult, _TErrorOut].Error(error)

    def is_error(self) -> bool:
        """Returns `True` if the result is an `Error` value."""
        return self.tag == "error"

    def is_ok(self) -> bool:
        """Return `True` if the result is an `Ok` value."""
        return self.tag == "ok"

    def filter(
        self, predicate: Callable[[_TSourceOut], bool], default: _TError
    ) -> Result[_TSourceOut, _TError | _TErrorOut]:
        """Filter result.

        Returns the input if the predicate evaluates to true, otherwise
        returns the `default`
        """
        match self:
            case Result(tag="ok", ok=value) if predicate(value):
                return self
            case Result(tag="error"):
                return self
            case _:
                return Error(default)

    def filter_with(
        self,
        predicate: Callable[[_TSourceOut], bool],
        default: Callable[[_TSourceOut], _TErrorOut],
    ) -> Result[_TSourceOut, _TErrorOut]:
        """Filter result.

        Returns the input if the predicate evaluates to true, otherwise
        returns the `default` using the value as input
        """
        match self:
            case Result(tag="ok", ok=value) if predicate(value):
                return self
            case Result(tag="ok", ok=value):
                return Error(default(value))
            case Result():
                return self

    def dict(self) -> builtins.dict[str, _TSourceOut | _TErrorOut | Literal["ok", "error"]]:
        """Return a json serializable representation of the result."""
        match self:
            case Result(tag="ok", ok=value):
                attr = getattr(value, "model_dump", None) or getattr(value, "dict", None)
                if attr and callable(attr):
                    value = cast(_TSourceOut, attr())
                return {"tag": "ok", "ok": value}
            case Result(error=error):
                attr = getattr(error, "model_dump", None) or getattr(error, "dict", None)
                if attr and callable(attr):
                    error = cast(_TErrorOut, attr())
                return {"tag": "error", "error": error}

    def swap(self) -> Result[_TErrorOut, _TSourceOut]:
        """Swaps the value in the result so an Ok becomes an Error and an Error becomes an Ok."""
        match self:
            case Result(tag="ok", ok=value):
                return Result(error=value)
            case Result(error=error):
                return Result(ok=error)

    def or_else(self, other: Result[_TSourceOut, _TErrorOut]) -> Result[_TSourceOut, _TErrorOut]:
        """Return the result if it is Ok, otherwise return the other result."""
        return self if self.is_ok() else other

    def or_else_with(
        self, other: Callable[[_TErrorOut], Result[_TSourceOut, _TErrorOut]]
    ) -> Result[_TSourceOut, _TErrorOut]:
        """Return the result if it is Ok, otherwise return the result of the other function."""
        return self if self.is_ok() else other(self.error)

    def merge(self: Result[_TSource, _TSource]) -> _TSource:
        """Merge the ok and error values into a single value.

        This method is only available on Results where _TSource and _TError are the same type.
        """
        return self.default_with(lambda x: x)

    def to_option(self) -> Option[_TSourceOut]:
        """Convert result to an option."""
        match self:
            case Result(tag="ok", ok=value):
                from expression.core.option import Some

                return Some(value)
            case _:
                from expression.core.option import Nothing

                return Nothing

    @classmethod
    def of_option(cls, value: Option[_TSource], error: _TError) -> Result[_TSource, _TError]:
        """Convert option to a result."""
        return of_option(value, error)

    @classmethod
    def of_option_with(cls, value: Option[_TSource], error: Callable[[], _TError]) -> Result[_TSource, _TError]:
        """Convert option to a result."""
        return of_option_with(value, error)

    def __iter__(self) -> Generator[_TSourceOut, _TSourceOut, _TSourceOut]:
        match self:
            case Result(tag="ok", ok=value):
                return (yield value)
            case _:
                raise EffectError(self)

    def __str__(self) -> str:
        match self:
            case Result(tag="ok", ok=value):
                return f"Ok {value}"
            case Result(error=error):
                return f"Error {error}"

    def __repr__(self) -> str:
        return str(self)

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: GetCoreSchemaHandler) -> CoreSchema:
        from pydantic import ValidatorFunctionWrapHandler
        from pydantic_core import core_schema

        origin = get_origin(source_type)
        if origin is None:  # used as `x: Result` without params
            origin = source_type
            type_vars = (Any, Any)
        else:
            type_vars = get_args(source_type)

        ok_schema = handler.generate_schema(type_vars[0])
        error_schema = handler.generate_schema(type_vars[1])

        def validate_ok(v: Any, handler: ValidatorFunctionWrapHandler) -> Result[_TSourceOut, _TErrorOut]:
            if "ok" not in v:
                raise ValueError("Missing ok field")
            value = handler(v["ok"])
            return cls(ok=value)

        def validate_error(v: Any, handler: ValidatorFunctionWrapHandler) -> Result[_TSourceOut, _TErrorOut]:
            if "error" not in v:
                raise ValueError("Missing error field")

            value = handler(v["error"])
            return cls(error=value)

        python_schema = core_schema.union_schema(
            [
                core_schema.is_instance_schema(cls),
                core_schema.no_info_wrap_validator_function(validate_error, error_schema),
                core_schema.no_info_wrap_validator_function(validate_ok, ok_schema),
            ]
        )
        json_schema = core_schema.chain_schema(
            [
                core_schema.union_schema(
                    [
                        core_schema.typed_dict_schema(
                            {
                                "tag": core_schema.typed_dict_field(core_schema.str_schema()),
                                "ok": core_schema.typed_dict_field(ok_schema),
                            }
                        ),
                        core_schema.typed_dict_schema(
                            {
                                "tag": core_schema.typed_dict_field(core_schema.str_schema()),
                                "error": core_schema.typed_dict_field(error_schema),
                            }
                        ),
                    ]
                ),
                # after validating the json data convert it to python
                core_schema.no_info_before_validator_function(
                    lambda data: cls(data),
                    python_schema,
                ),
            ]
        )

        return core_schema.json_or_python_schema(
            json_schema=json_schema,
            python_schema=python_schema,
            serialization=core_schema.plain_serializer_function_ser_schema(lambda instance: instance.dict()),
        )


def Error(error: _TError) -> Result[Any, _TError]:
    return Result[Any, _TError].Error(error)


def Ok(value: _TSource) -> Result[_TSource, Any]:
    return Result[_TSource, Any].Ok(value)


class ResultException(EffectError):
    """Makes the Error case a valid exception for effect handling.

    Do not use directly.
    """

    def __init__(self, message: str):
        self.message = message


def default_value(value: _TSource) -> Callable[[Result[_TSource, Any]], _TSource]:
    """Get the value or default value.

    Gets the value of the result if the result is Ok, otherwise
    returns the specified default value.
    """

    def _default_value(result: Result[_TSource, Any]) -> _TSource:
        return result.default_value(value)

    return _default_value


def default_with(getter: Callable[[_TError], _TSource]) -> Callable[[Result[_TSource, _TError]], _TSource]:
    """Get with default value lazily.

    Gets the value of the option if the option is Some, otherwise
    returns the value produced by the getter
    """

    def _default_with(result: Result[_TSource, _TError]) -> _TSource:
        return result.default_with(getter)

    return _default_with


@curry_flip(1)
def map(result: Result[_TSource, _TError], mapper: Callable[[_TSource], _TResult]) -> Result[_TResult, _TError]:
    return result.map(mapper)


@curry_flip(2)
def map2(
    x: Result[_TSource, _TError],
    y: Result[_TOther, _TError],
    mapper: Callable[[_TSource, _TOther], _TResult],
) -> Result[_TResult, _TError]:
    return x.map2(y, mapper)


@curry_flip(1)
def map_error(result: Result[_TSource, _TError], mapper: Callable[[_TError], _TResult]) -> Result[_TSource, _TResult]:
    return result.map_error(mapper)


@curry_flip(1)
def bind(
    result: Result[_TSource, _TError],
    mapper: Callable[[_TSource], Result[_TResult, Any]],
) -> Result[_TResult, _TError]:
    return result.bind(mapper)


def dict(source: Result[_TSource, _TError]) -> builtins.dict[str, _TSource | _TError | Literal["ok", "error"]]:
    return source.dict()


def is_ok(result: Result[_TSource, _TError]) -> TypeGuard[Result[_TSource, _TError]]:
    """Returns `True` if the result is an `Ok` value."""
    return result.is_ok()


def is_error(result: Result[_TSource, _TError]) -> TypeGuard[Result[_TSource, _TError]]:
    """Returns `True` if the result is an `Error` value."""
    return result.is_error()


@curry_flip(1)
def filter(
    result: Result[_TSource, _TError],
    predicate: Callable[[_TSource], bool],
    default: _TError,
) -> Result[_TSource, _TError]:
    return result.filter(predicate, default)


@curry_flip(1)
def filter_with(
    result: Result[_TSource, _TError],
    predicate: Callable[[_TSource], bool],
    default: Callable[[_TSource], _TError],
) -> Result[_TSource, _TError]:
    return result.filter_with(predicate, default)


def swap(result: Result[_TSource, _TError]) -> Result[_TError, _TSource]:
    """Swaps the value in the result so an Ok becomes an Error and an Error becomes an Ok."""
    return result.swap()


@curry_flip(1)
def or_else(result: Result[_TSource, _TError], other: Result[_TSource, _TError]) -> Result[_TSource, _TError]:
    return result.or_else(other)


@curry_flip(1)
def or_else_with(
    result: Result[_TSource, _TError],
    other: Callable[[_TError], Result[_TSource, _TError]],
) -> Result[_TSource, _TError]:
    return result.or_else_with(other)


def merge(result: Result[_TSource, _TSource]) -> _TSource:
    return result.merge()


def to_option(result: Result[_TSource, Any]) -> Option[_TSource]:
    from expression.core.option import Nothing, Some

    match result:
        case Result(tag="ok", ok=value):
            return Some(value)
        case _:
            return Nothing


def of_option(value: Option[_TSource], error: _TError) -> Result[_TSource, _TError]:
    return value.to_result(error)


def of_option_with(value: Option[_TSource], error: Callable[[], _TError]) -> Result[_TSource, _TError]:
    return value.to_result_with(error)


__all__ = [
    "Error",
    "Ok",
    "Result",
    "bind",
    "default_value",
    "default_with",
    "dict",
    "filter",
    "filter_with",
    "is_error",
    "is_ok",
    "map",
    "map2",
    "map_error",
    "merge",
    "of_option",
    "of_option_with",
    "or_else",
    "or_else_with",
    "swap",
    "to_option",
]
