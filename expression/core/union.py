from abc import ABC
from typing import Any, Generic, Iterable, Optional, TypeVar, Union, get_origin

from typing_extensions import TypeVarTuple, Unpack

from .typing import SupportsMatch

_T = TypeVar("_T")
_TArgs = TypeVarTuple("_TArgs")


class DiscriminatedUnion(
    Generic[_T, Unpack[_TArgs]], SupportsMatch[Union[_T, Unpack[_TArgs]]], ABC
):
    """A discriminated (tagged) union.

    Takes a value, and an optional tag that may be used for matching."""

    def __init__(
        self, value: Union[_T, Unpack[_TArgs]], tag: Optional[int] = None
    ) -> None:
        self.value = value
        self.tag = tag

    def __match__(self, pattern: Any) -> Iterable[Union[_T, Unpack[_TArgs]]]:
        if self.value is pattern or self.value == pattern:
            return [self.value]

        try:
            origin: Any = get_origin(pattern)
            if isinstance(self.value, origin or pattern):
                return [self.value]
        except TypeError:
            pass

        return []
