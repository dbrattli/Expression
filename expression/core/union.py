from __future__ import annotations

import itertools
from abc import ABC
from typing import (
    Any,
    Dict,
    Generic,
    Iterable,
    Iterator,
    Optional,
    TypeVar,
    cast,
    get_origin,
)

from .pipe import PipeMixin
from .typing import GenericValidator, ModelField, SupportsMatch, SupportsValidation

_T = TypeVar("_T")


class Tag(SupportsMatch[_T]):
    """For creating tagged union cases.

    Args:
        tag: Optional tag number. If not set it will be generated
        automatically.

    """

    INITIAL_TAG = 1000
    _count = itertools.count(start=INITIAL_TAG)

    def __init__(self, tag: Optional[int] = None, *args: Any, **kwargs: Any) -> None:
        self.value = args[0] if args else None
        self.fields: Dict[str, Any] = kwargs
        self.tag = tag or next(Tag._count)

    def __match__(self, pattern: Any) -> Iterable[_T]:
        if pattern is self:
            return [cast(_T, None)]

        if isinstance(pattern, Tag):
            if pattern.tag == self.tag:
                return [cast(_T, None)]

        if isinstance(pattern, TaggedUnion):
            if pattern.tag.tag == self.tag:
                if self.value and self.value == pattern.value:
                    return [pattern.value]

                for key, value in self.fields.items():
                    if pattern.value and getattr(pattern.value, key) != value:
                        return []
                    if pattern.fields and pattern.fields.get(key) != value:
                        return []

                if hasattr(pattern, "value"):
                    return [pattern.value]
                return [cast(_T, pattern.fields.values())]

        return []

    def __eq__(self, other: Any) -> bool:
        if self is other:
            return True

        if not isinstance(other, Tag):
            return False

        return self.tag == other.tag

    def __str__(self) -> str:
        return f"tag: {self.tag}"

    def __repr__(self) -> str:
        return f"tag: {self.tag}"

    def __call__(self, *args: Any, **kwargs: Any) -> Tag[_T]:
        return self.__class__(self.tag, *args, **kwargs)


class TaggedUnion(SupportsValidation[Any], PipeMixin, ABC):
    """A discriminated (tagged) union.

    Takes a value, and an optional tag that may be used for matching."""

    def __init__(self, tag: Tag[Any], __value: Any = None, **kwargs: Any) -> None:
        self.value = __value
        self.tag = tag
        self.fields = kwargs

    def __match__(self, pattern: _T) -> Iterable[_T]:
        if self.value is pattern:
            return [self.value]

        try:
            origin: Any = get_origin(pattern)
            if isinstance(self.value, origin or pattern):
                return [self.value]
        except TypeError:
            pass

        return []

    def dict(self) -> Any:
        tags: Dict[str, Any] = {
            k: v for (k, v) in self.__class__.__dict__.items() if v is self.tag
        }
        if hasattr(self.value, "dict"):
            value = self.value.dict()
        else:
            value = self.value
        return dict(tag=list(tags.keys())[0], value=value)

    @classmethod
    def __get_validators__(cls) -> Iterator[GenericValidator[TaggedUnion]]:
        def _validate(union: Any, field: ModelField) -> TaggedUnion:
            if isinstance(union, TaggedUnion):
                return union

            tags: Dict[str, Any] = {
                k: v for (k, v) in cls.__dict__.items() if k == union["tag"]
            }
            if field.sub_fields:
                sub_field = field.sub_fields[0]
                value, error = sub_field.validate(union["value"], {}, loc=union["tag"])
                if error:
                    raise ValueError(str(error))
            else:
                value = union["value"]
            return cls(tags[union["tag"]], value)

        yield _validate

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, TaggedUnion):
            return False

        return self.tag == other.tag and self.value == other.value


class SingleCaseUnion(TaggedUnion, Generic[_T]):
    """Single case union.

    Helper class to make single case tagged unions without having to
    declare the tag which is needed to make a tagged union. The name of
    the tag for a single case union is `VALUE` and may be used for
    matching purposes.
    """

    VALUE = Tag[_T]()

    def __init__(self, value: _T) -> None:
        super().__init__(SingleCaseUnion.VALUE, value)


__all__ = ["SingleCaseUnion", "Tag", "TaggedUnion"]
