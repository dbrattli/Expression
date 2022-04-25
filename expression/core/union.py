from __future__ import annotations

import itertools
from abc import ABC
from typing import (
    Any,
    Dict,
    Generic,
    Iterable,
    Iterator,
    List,
    Optional,
    TypeVar,
    cast,
    get_origin,
)

from .typing import SupportsMatch, Validated, Validator

_T = TypeVar("_T")


def _validate(union: Any) -> TaggedUnion:
    if isinstance(union, TaggedUnion):
        return union

    raise NotImplementedError


class Tag(SupportsMatch[_T]):
    """For creating tagged union cases.

    Args:
        tag: Optional tag number. If not set it will be generated
        automatically.

    """

    _count = itertools.count(start=1000)

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

    def __call__(self, *args: Any, **kwargs: Any) -> Tag[_T]:
        return self.__class__(self.tag, *args, **kwargs)


class TaggedUnion(Validated[Any], ABC):
    """A discriminated (tagged) union.

    Takes a value, and an optional tag that may be used for matching."""

    __validators__: List[Validator[Any]] = [_validate]

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

    def to_json(self) -> Any:
        raise NotImplementedError

    @classmethod
    def __get_validators__(cls) -> Iterator[Validator[Any]]:
        yield from cls.__validators__


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
