from __future__ import annotations

import itertools
from abc import ABC
from typing import (
    Any,
    Dict,
    Generic,
    Iterator,
    Optional,
    Type,
    TypeVar,
    overload,
)

from .pipe import PipeMixin
from .typing import GenericValidator, ModelField, SupportsValidation

_T = TypeVar("_T")


class Tag(Generic[_T]):
    """For creating tagged union cases.

    Args:
        tag: Optional tag number. If not set it will be generated
        automatically.

    """

    INITIAL_TAG = 1000
    _count = itertools.count(start=INITIAL_TAG)

    def __init__(
        self,
        tag: Optional[int] = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self.value = args[0] if args else None
        self.fields: Dict[str, Any] = kwargs
        self.tag = tag or next(Tag._count)

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


@overload
def tag() -> Tag[None]:
    ...


@overload
def tag(type: Type[_T]) -> Tag[_T]:
    ...


def tag(type: Optional[Type[Any]] = None) -> Tag[Any]:
    """Convenience from creating tags.

    Less and simpler syntax since the type is given as an argument."""
    return Tag()


class TaggedUnion(SupportsValidation[Any], PipeMixin, ABC):
    """A discriminated (tagged) union.

    Takes a value, and an optional tag that may be used for matching."""

    __match_args__ = ("tag", "value")

    def __init__(self, tag: Tag[Any], value: Any = None, **kwargs: Any) -> None:
        self.value = value
        self.tag = tag
        self.fields = kwargs

        if not hasattr(self.__class__, "_tags"):
            tags = {
                tag.tag: name
                for (name, tag) in self.__class__.__dict__.items()
                if isinstance(tag, Tag)
            }
            setattr(self.__class__, "_tags", tags)

        self.name = getattr(self.__class__, "_tags")[tag.tag]

    def dict(self) -> Any:
        tags: Dict[str, Any] = {
            k: v for (k, v) in self.__class__.__dict__.items() if v is self.tag
        }
        if hasattr(self.value, "dict"):
            value = self.value.dict()
        else:
            value = self.value
        return dict(tag=list(tags.keys())[0], value=value)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}: {self.name} {self.value}"

    def __repr__(self) -> str:
        return str(self)

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
        setattr(self.__class__, "_tags", {SingleCaseUnion.VALUE.tag: "VALUE"})
        super().__init__(SingleCaseUnion.VALUE, value)


__all__ = ["SingleCaseUnion", "Tag", "TaggedUnion", "tag"]
