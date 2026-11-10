"""Pydantic metadata for the public closed case unions.

Pydantic skips custom hooks on specialized standard dataclasses and ignores
``init=False`` fields on input. Validate case selection before invoking its
normal payload schema, including for generic and recursively nested unions.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import fields
from typing import TYPE_CHECKING, Any, cast, get_args, get_origin


if TYPE_CHECKING:
    from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler
    from pydantic.json_schema import JsonSchemaValue
    from pydantic_core import CoreSchema


class UnionSchema:
    """Require the declared tag and fields when decoding a public union."""

    def __get_pydantic_core_schema__(self, source_type: Any, handler: GetCoreSchemaHandler) -> CoreSchema:
        from pydantic_core import core_schema

        choices: dict[str, CoreSchema] = {}
        for member in get_args(source_type):
            origin = get_origin(member) or member
            case_fields = fields(origin)
            tag = next(item.default for item in case_fields if item.name == "tag")
            if not isinstance(tag, str):
                raise TypeError("Union case tags must be strings")
            allowed = frozenset(item.name for item in case_fields)
            schema = handler.generate_schema(member)
            original_ref = schema.get("ref") or schema.get("schema_ref")
            schema = core_schema.no_info_before_validator_function(_check_case(tag, allowed), schema)
            if allowed == frozenset({"tag"}):
                # Dataclass validation bypasses __new__; restore canonical units.
                schema = core_schema.no_info_after_validator_function(_canonicalize(origin), schema)
            if isinstance(original_ref, str):
                # Bare cases may occur alongside unions. Give the stricter wire
                # schema its own definition instead of changing the bare case.
                name, separator, parameters = original_ref.partition(":")
                schema["ref"] = f"{name}Tagged{separator}{parameters}"
            schema["metadata"] = {"pydantic_js_functions": [_case_json_schema]}
            choices[tag] = schema
        return core_schema.tagged_union_schema(choices, discriminator="tag")


def _case_json_schema(core_schema: CoreSchema, handler: GetJsonSchemaHandler) -> JsonSchemaValue:
    schema = handler(core_schema)
    while "$ref" in schema:
        schema = handler.resolve_ref_schema(schema)
    schema = schema.copy()
    schema["required"] = list(dict.fromkeys([*schema.get("required", []), "tag"]))
    schema["additionalProperties"] = False
    return schema


def _check_case(tag: str, allowed: frozenset[str]) -> Callable[[object], object]:
    def check(value: object) -> object:
        if isinstance(value, Mapping):
            data = cast(Mapping[object, object], value)
            if data.get("tag") != tag:
                raise ValueError(f"Expected tag {tag!r}")
            if any(key not in allowed for key in data):
                raise ValueError(f"Unexpected fields for {tag!r}")
            return data
        return value

    return check


def _canonicalize(case_type: Callable[[], object]) -> Callable[[object], object]:
    def canonicalize(value: object) -> object:
        return case_type()

    return canonicalize
