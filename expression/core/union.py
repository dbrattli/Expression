from __future__ import annotations

import itertools
from abc import ABC
from typing import Any, Dict, Iterable, Optional, TypeVar, cast, get_origin

from .typing import SupportsMatch

_T = TypeVar("_T")


class Tag(SupportsMatch[_T]):
    count = itertools.count(start=1000)

    def __init__(self, tag: Optional[int] = None, **kwargs: Any) -> None:
        self.fields: Dict[str, Any] = kwargs
        self.tag = tag or next(Tag.count)

    def __match__(self, pattern: Any) -> Iterable[_T]:
        if pattern is self:
            return [cast(_T, None)]

        if isinstance(pattern, Tag):
            if pattern.tag == self.tag:
                return [cast(_T, None)]

        if isinstance(pattern, TaggedUnion):
            if pattern.tag.tag == self.tag:
                # print("Fields:", self.fields)
                for key, value in self.fields.items():
                    if pattern.value and getattr(pattern.value, key) != value:
                        return []
                    if pattern.fields and pattern.fields.get(key) != value:
                        return []

                if pattern.value:
                    return [pattern.value]
                return [cast(_T, pattern.fields.values())]

        return []

    def __eq__(self, other: Any) -> bool:
        if self is other:
            return True

        if not isinstance(other, Tag):
            return False

        return self.tag == other.tag

    def __call__(self, **kwargs: Any) -> Tag[_T]:
        return self.__class__(self.tag, **kwargs)


class TaggedUnion(ABC):
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
                print("got here", self.value, origin, pattern)
                return [self.value]
        except TypeError:
            pass

        return []
