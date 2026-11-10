"""Pydantic metadata for closed unions of declared case dataclasses.

Case constructors fix their tags. The wire representation additionally requires
that tag and rejects extra fields, including with nested and generic payloads.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator, Mapping
from dataclasses import MISSING, fields, is_dataclass
from functools import partial
from types import UnionType
from typing import TYPE_CHECKING, Annotated, Any, Union, cast, get_args, get_origin


if TYPE_CHECKING:
    from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler
    from pydantic.json_schema import JsonSchemaValue
    from pydantic_core import CoreSchema
    from pydantic_core.core_schema import DataclassArgsSchema


class UnionSchema:
    """Require declared tags and fields when decoding a case union."""

    def __init__(self, *, canonical_values: tuple[object, ...] = ()) -> None:
        self.canonical_values = canonical_values

    def __get_pydantic_core_schema__(self, source_type: Any, handler: GetCoreSchemaHandler) -> CoreSchema:
        from pydantic_core import core_schema

        choices: dict[str, CoreSchema] = {}
        for member, canonical_values in _members(source_type, self.canonical_values):
            origin = _case_origin(member)
            tag = origin.__dict__.get("__tagged_union_case__")
            if not isinstance(tag, str) or not is_dataclass(origin):
                raise TypeError("TaggedUnion members must be classes decorated with @case")
            case_fields = fields(origin)
            tag_field = next((item for item in case_fields if item.name == "tag"), None)
            if (
                tag_field is None
                or tag_field.init
                or tag_field.default != tag
                or tag_field.default_factory is not MISSING
            ):
                raise TypeError(f"Invalid fixed tag field on {origin.__name__}")
            if tag in choices:
                raise TypeError(f"Duplicate tagged union tag {tag!r}")
            allowed = frozenset(item.name for item in case_fields)
            schema = handler.generate_schema(member)
            _check_field_aliases(schema, handler)
            original_ref = schema.get("ref") or schema.get("schema_ref")
            schema = core_schema.no_info_before_validator_function(_check_case(tag, allowed), schema)
            canonical = _canonical_value(origin, tag, allowed, canonical_values)
            if canonical is not None:
                schema = core_schema.no_info_after_validator_function(_canonicalize(canonical), schema)
            if isinstance(original_ref, str):
                name, separator, parameters = original_ref.partition(":")
                schema["ref"] = f"{name}Tagged{separator}{parameters}"
            else:
                # Annotated case metadata can wrap the dataclass schema. Keep
                # such a choice distinct from an unannotated use of the case.
                schema["ref"] = f"{origin.__module__}.{origin.__qualname__}Tagged:{id(member)}"
            if canonical is not None:
                schema["ref"] = f"{origin.__module__}.{origin.__qualname__}TaggedCanonical:{id(canonical)}"
            schema["metadata"] = {"pydantic_js_functions": [partial(_case_json_schema, allowed=allowed)]}
            choices[tag] = schema
        return core_schema.tagged_union_schema(choices, discriminator="tag")


def _members(source_type: Any, canonical_values: tuple[object, ...]) -> Iterator[tuple[Any, tuple[object, ...]]]:
    origin = get_origin(source_type)
    if origin in (Union, UnionType):
        for member in get_args(source_type):
            yield from _members(member, canonical_values)
    elif origin is Annotated:
        base, *metadata = get_args(source_type)
        nested = tuple(item for item in metadata if isinstance(item, UnionSchema))
        if nested:
            other_metadata = tuple(item for item in metadata if not isinstance(item, UnionSchema))
            canonical_values += tuple(value for item in nested for value in item.canonical_values)
            if other_metadata:
                if get_origin(base) in (Union, UnionType):
                    raise TypeError("Nested TaggedUnion aliases cannot also carry union-level validation metadata")
                base = Annotated[base, *other_metadata]
            yield from _members(base, canonical_values)
        else:
            if get_origin(base) in (Union, UnionType):
                raise TypeError("Annotated union members must use TaggedUnion metadata")
            yield source_type, canonical_values
    else:
        yield source_type, canonical_values


def _case_origin(member: Any) -> type[object]:
    while get_origin(member) is Annotated:
        member = get_args(member)[0]
    origin = get_origin(member) or member
    if not isinstance(origin, type):
        raise TypeError("TaggedUnion members must be classes decorated with @case")
    return cast(type[object], origin)


def _check_field_aliases(schema: CoreSchema, handler: GetCoreSchemaHandler) -> None:
    if schema["type"] == "definition-ref":
        try:
            schema = handler.resolve_ref_schema(schema)
        except LookupError:
            # Recursive cases are still being built. Their complete schema is
            # checked when the surrounding case finishes generating.
            return
    if schema["type"] == "dataclass":
        arguments = schema["schema"]
        if arguments["type"] == "dataclass-args":
            for field in cast("DataclassArgsSchema", arguments)["fields"]:
                if field.get("validation_alias") not in (None, field["name"]) or field.get(
                    "serialization_alias"
                ) not in (
                    None,
                    field["name"],
                ):
                    raise TypeError("TaggedUnion case fields must use their Python names, without Pydantic aliases")
    elif schema["type"] in ("function-before", "function-after", "function-wrap", "default"):
        _check_field_aliases(cast(Mapping[str, Any], schema)["schema"], handler)


def _case_json_schema(
    core_schema: CoreSchema, handler: GetJsonSchemaHandler, *, allowed: frozenset[str]
) -> JsonSchemaValue:
    schema: JsonSchemaValue = handler(core_schema)
    while "$ref" in schema:
        try:
            schema = handler.resolve_ref_schema(schema)
        except LookupError:
            # A recursive case's definition may still be under construction.
            # Keep its reference and close the object in a sibling schema;
            # the empty properties permit exactly the declared field names.
            properties: dict[str, JsonSchemaValue] = {name: {} for name in sorted(allowed)}
            schema = {"allOf": [schema], "properties": properties}
            break
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
            # The dataclass constructor does not accept its fixed tag. Strip it
            # after checking so Pydantic's extra='forbid' also works correctly.
            return {key: item for key, item in data.items() if key != "tag"}
        return value

    return check


def _canonical_value(
    origin: type[object], tag: str, allowed: frozenset[str], values: tuple[object, ...]
) -> object | None:
    matching = tuple(value for value in values if type(value) is origin)
    if not matching:
        return None
    canonical = matching[0]
    if any(value is not canonical for value in matching):
        raise TypeError("A case cannot have conflicting canonical values")
    if allowed != frozenset({"tag"}):
        raise TypeError("Only unit cases can have a canonical value")
    if getattr(canonical, "tag", None) != tag:
        raise TypeError("A canonical case must have its declared tag")
    return canonical


def _canonicalize(canonical: object) -> Callable[[object], object]:
    def canonicalize(value: object) -> object:
        return canonical

    return canonicalize
