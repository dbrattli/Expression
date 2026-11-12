"""Encode case payloads without erasing nested tagged-union distinctions."""

from collections.abc import Mapping
from dataclasses import fields, is_dataclass
from typing import Protocol, cast, runtime_checkable


@runtime_checkable
class _ModelDump(Protocol):
    def model_dump(self) -> object: ...


def encode(value: object) -> object:
    """Encode dataclasses, containers, and model payloads recursively.

    Leaves remain the responsibility of the caller's JSON encoder or codec.
    In particular, this does not stringify otherwise unsupported Python values.
    """
    if is_dataclass(value) and not isinstance(value, type):
        return {item.name: encode(getattr(value, item.name)) for item in fields(value)}
    if isinstance(value, Mapping):
        mapping = cast(Mapping[object, object], value)
        return {key: encode(item) for key, item in mapping.items()}
    if isinstance(value, (list, tuple)):
        return [encode(item) for item in cast(list[object] | tuple[object, ...], value)]
    if isinstance(value, _ModelDump):
        return encode(value.model_dump())
    return value
