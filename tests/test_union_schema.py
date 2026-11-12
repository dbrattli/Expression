from __future__ import annotations

from dataclasses import dataclass, field
from typing import Annotated, ClassVar, Generic, Literal, TypeVar, final

import pytest
from pydantic import AfterValidator, BaseModel, ConfigDict, Field, TypeAdapter, ValidationError
from pydantic.json_schema import JsonSchemaValue

from expression import Nothing, Ok, Option, Result, Some, TaggedUnion, case, tag
from expression.core._union_schema import UnionSchema


def _resolve(document: JsonSchemaValue, schema: JsonSchemaValue) -> JsonSchemaValue:
    while "$ref" in schema:
        reference: str = schema["$ref"]
        assert reference.startswith("#/$defs/")
        schema = document["$defs"][reference.removeprefix("#/$defs/")]
    if "allOf" in schema and len(schema["allOf"]) == 1:
        base = _resolve(document, schema["allOf"][0])
        if set(schema) <= {"allOf", "$defs"}:
            return base
        return {
            **base,
            **{key: value for key, value in schema.items() if key not in ("allOf", "properties", "required")},
            "properties": {**schema.get("properties", {}), **base.get("properties", {})},
            "required": list(dict.fromkeys([*base.get("required", []), *schema.get("required", [])])),
        }
    return schema


def _case(document: JsonSchemaValue, union: JsonSchemaValue, tag: str) -> JsonSchemaValue:
    union = _resolve(document, union)
    reference = union["discriminator"]["mapping"][tag]
    assert {"$ref": reference} in union["oneOf"]
    return _resolve(document, {"$ref": reference})


@pytest.mark.parametrize("mode", ["validation", "serialization"])
def test_option_json_schema_requires_tag_and_exact_case_fields(mode: Literal["validation", "serialization"]):
    schema = TypeAdapter(Option[int | None]).json_schema(mode=mode)
    some = _case(schema, schema, "some")
    nothing = _case(schema, schema, "none")

    assert set(some["required"]) == {"tag", "some"}
    assert set(some["properties"]) == {"tag", "some"}
    assert some["properties"]["tag"]["const"] == "some"
    assert some["properties"]["some"]["anyOf"] == [{"type": "integer"}, {"type": "null"}]
    assert some["additionalProperties"] is False
    assert nothing["required"] == ["tag"]
    assert set(nothing["properties"]) == {"tag"}
    assert nothing["properties"]["tag"]["const"] == "none"
    assert nothing["additionalProperties"] is False


@pytest.mark.parametrize("mode", ["validation", "serialization"])
def test_result_json_schema_requires_tag_and_exact_case_fields(mode: Literal["validation", "serialization"]):
    schema = TypeAdapter(Result[int | None, str | None]).json_schema(mode=mode)
    for case_tag, payload_type in (("ok", "integer"), ("error", "string")):
        case = _case(schema, schema, case_tag)
        assert set(case["required"]) == {"tag", case_tag}
        assert set(case["properties"]) == {"tag", case_tag}
        assert case["properties"]["tag"]["const"] == case_tag
        assert case["properties"][case_tag]["anyOf"] == [{"type": payload_type}, {"type": "null"}]
        assert case["additionalProperties"] is False


def test_nested_union_json_schema_keeps_each_case_closed():
    adapter = TypeAdapter(Option[Result[Option[int | None], str]])
    schema = adapter.json_schema()
    outer = _case(schema, schema, "some")
    result = outer["properties"]["some"]
    ok = _case(schema, result, "ok")
    inner = _case(schema, ok["properties"]["ok"], "some")
    nothing = _case(schema, ok["properties"]["ok"], "none")
    assert all(case["additionalProperties"] is False for case in (outer, ok, inner, nothing))
    assert set(inner["required"]) == {"tag", "some"}
    assert nothing["required"] == ["tag"]
    value = adapter.validate_python({"tag": "some", "some": {"tag": "ok", "ok": {"tag": "none"}}})
    assert isinstance(value, Some)
    assert isinstance(value.some, Ok)
    assert value.some.ok is Nothing()


class SchemaTree(BaseModel):
    child: Option[SchemaTree]


def test_recursive_union_json_schema_preserves_model_references():
    schema = SchemaTree.model_json_schema()
    tree = _resolve(schema, schema)
    some = _case(schema, tree["properties"]["child"], "some")
    assert _resolve(schema, some["properties"]["some"]) is tree
    assert set(some["required"]) == {"tag", "some"}
    assert some["additionalProperties"] is False

    parsed = SchemaTree.model_validate({"child": {"tag": "some", "some": {"child": {"tag": "none"}}}})
    assert isinstance(parsed.child, Some)
    assert parsed.child.some.child is Nothing()
    with pytest.raises(ValidationError):
        SchemaTree.model_validate({"child": {"tag": "some", "some": {"child": {"tag": "none", "some": 1}}}})


def test_union_json_schema_does_not_change_bare_dataclass_schema():
    class MixedModel(BaseModel):
        optional: Option[int]
        present: Some[int]

    schema = MixedModel.model_json_schema()
    some = _case(schema, schema["properties"]["optional"], "some")
    bare = _resolve(schema, schema["properties"]["present"])
    assert set(some["required"]) == {"tag", "some"}
    assert some["additionalProperties"] is False
    assert bare["required"] == ["some"]
    assert "additionalProperties" not in bare
    parsed = MixedModel.model_validate({"optional": {"tag": "none"}, "present": {"some": 1}})
    assert parsed.optional is Nothing()
    assert parsed.present == Some(1)


@final
@case
class SchemaCircle:
    radius: Annotated[float, Field(gt=0)]
    tag: Literal["circle"] = tag()


@final
@case
class SchemaRectangle:
    __pydantic_config__: ClassVar[ConfigDict] = ConfigDict(extra="forbid")

    width: float
    height: float
    label: str = "rectangle"
    tag: Literal["rectangle"] = tag()


_SchemaValue = TypeVar("_SchemaValue")


@final
@case
class SchemaBox(Generic[_SchemaValue]):
    value: _SchemaValue
    notes: list[str] = field(default_factory=list[str])
    tag: Literal["box"] = tag()


@final
@case
class ModernSchemaBox[T]:
    value: T
    tag: Literal["modern_box"] = tag()


def test_python312_type_parameters_preserve_payload_validation():
    adapter = TypeAdapter(TaggedUnion[ModernSchemaBox[Option[int]]])
    value = adapter.validate_python({"tag": "modern_box", "value": {"tag": "some", "some": 42}})
    assert value == ModernSchemaBox(Some(42))
    assert adapter.validate_json(adapter.dump_json(value)) == value
    with pytest.raises(ValidationError):
        adapter.validate_python({"tag": "modern_box", "value": {"tag": "some", "some": "invalid"}})


@final
@case
class SchemaUnit:
    initialized: ClassVar[list[str]] = []
    tag: Literal["unit"] = tag()

    def __post_init__(self) -> None:
        self.initialized.append("unit")


def test_custom_case_single_generic_union_and_default_factory():
    adapter = TypeAdapter(TaggedUnion[SchemaBox[int]])
    first = adapter.validate_python({"tag": "box", "value": 42})
    second = adapter.validate_python({"tag": "box", "value": 43})
    assert first == SchemaBox(42)
    assert first.notes is not second.notes
    with pytest.raises(ValidationError):
        adapter.validate_python({"tag": "box", "value": "invalid"})
    schema = adapter.json_schema()
    box = _case(schema, schema, "box")
    assert set(box["required"]) == {"tag", "value"}
    assert box["properties"]["value"]["type"] == "integer"


def test_generic_payload_types_are_not_shadowed_by_caller_type_variables():
    _T = TypeVar("_T")
    _E = TypeVar("_E")

    with pytest.raises(ValidationError):
        TypeAdapter(Ok[int]).validate_python({"ok": "invalid"})
    adapter = TypeAdapter(Result[int, str])
    with pytest.raises(ValidationError):
        adapter.validate_python({"tag": "ok", "ok": "invalid"})
    with pytest.raises(ValidationError):
        adapter.validate_python({"tag": "error", "error": 42})


def test_custom_multifield_case_accepts_extra_forbid_and_defaults():
    adapter = TypeAdapter(TaggedUnion[SchemaCircle | SchemaRectangle])
    value = adapter.validate_python({"tag": "rectangle", "width": 3, "height": 4})
    assert value == SchemaRectangle(3, 4)
    assert adapter.dump_python(value) == {"tag": "rectangle", "width": 3, "height": 4, "label": "rectangle"}
    for invalid in (
        {"width": 3, "height": 4},
        {"tag": "rectangle", "width": 3},
        {"tag": "rectangle", "width": 3, "height": 4, "radius": 1},
        {"tag": "circle", "radius": -1},
    ):
        with pytest.raises(ValidationError):
            adapter.validate_python(invalid)


def test_custom_unit_cases_are_ordinary_values_and_initialize_once():
    adapter = TypeAdapter(TaggedUnion[SchemaCircle | SchemaUnit])
    SchemaUnit.initialized.clear()
    first = adapter.validate_python({"tag": "unit"})
    second = adapter.validate_python({"tag": "unit"})
    assert first == second
    assert first is not second
    assert SchemaUnit.initialized == ["unit", "unit"]


def test_nested_tagged_union_aliases_flatten_and_keep_canonical_units():
    adapter = TypeAdapter(TaggedUnion[TaggedUnion[SchemaCircle | SchemaRectangle] | Option[int]])
    assert adapter.validate_python({"tag": "circle", "radius": 2}) == SchemaCircle(2)
    assert adapter.validate_python({"tag": "none"}) is Nothing()
    schema = adapter.json_schema()
    assert set(schema["discriminator"]["mapping"]) == {"circle", "rectangle", "some", "none"}


@final
@case
class SchemaLeaf:
    value: int
    tag: Literal["leaf"] = tag()


@final
@case
class SchemaBranch:
    children: list[TaggedUnion[SchemaLeaf | SchemaBranch]]
    tag: Literal["branch"] = tag()


def test_recursive_custom_cases_validate_and_preserve_schema_references():
    adapter = TypeAdapter(TaggedUnion[SchemaLeaf | SchemaBranch])
    wire = {"tag": "branch", "children": [{"tag": "branch", "children": [{"tag": "leaf", "value": 42}]}]}
    value = adapter.validate_python(wire)
    assert value == SchemaBranch([SchemaBranch([SchemaLeaf(42)])])
    assert adapter.dump_python(value) == wire
    schema = adapter.json_schema()
    branch = _case(schema, schema, "branch")
    nested = branch["properties"]["children"]["items"]
    assert _case(schema, nested, "branch") == branch


def test_canonical_units_do_not_leak_between_differently_configured_aliases():
    wire = [{"tag": "none"}, {"tag": "none"}]
    option_first = TypeAdapter(tuple[Option[int], TaggedUnion[Nothing]]).validate_python(wire)
    option_last = TypeAdapter(tuple[TaggedUnion[Nothing], Option[int]]).validate_python(wire)
    assert option_first[0] is Nothing()
    assert option_last[1] is Nothing()

    canonical = SchemaUnit()
    unit_wire = [{"tag": "unit"}, {"tag": "unit"}]
    first = TypeAdapter(
        tuple[Annotated[SchemaUnit, UnionSchema(canonical_values=(canonical,))], TaggedUnion[SchemaUnit]]
    ).validate_python(unit_wire)
    last = TypeAdapter(
        tuple[TaggedUnion[SchemaUnit], Annotated[SchemaUnit, UnionSchema(canonical_values=(canonical,))]]
    ).validate_python(unit_wire)
    assert first[0] is canonical
    assert first[1] is not canonical
    assert last[0] is not canonical
    assert last[1] is canonical


def _small_circle(value: SchemaCircle) -> SchemaCircle:
    if value.radius > 10:
        raise ValueError("Circle is too large")
    return value


def test_annotated_case_validation_metadata_is_preserved_and_isolated():
    adapter = TypeAdapter(
        tuple[
            TaggedUnion[Annotated[SchemaCircle, AfterValidator(_small_circle)] | SchemaUnit],
            TaggedUnion[SchemaCircle | SchemaUnit],
        ]
    )
    assert adapter.validate_python([{"tag": "circle", "radius": 2}, {"tag": "circle", "radius": 20}]) == (
        SchemaCircle(2),
        SchemaCircle(20),
    )
    with pytest.raises(ValidationError, match="too large"):
        adapter.validate_python([{"tag": "circle", "radius": 20}, {"tag": "circle", "radius": 2}])


def test_nested_union_level_validation_metadata_is_rejected_explicitly():
    with pytest.raises(TypeError, match="union-level validation metadata"):
        TypeAdapter(
            TaggedUnion[
                Annotated[TaggedUnion[SchemaCircle | SchemaUnit], AfterValidator(lambda value: value)] | SchemaBox[int]
            ]
        )


def test_union_rejects_duplicate_tags_and_noncase_members():
    @final
    @case
    class OtherCircle:
        diameter: float
        tag: Literal["circle"] = tag()

    @dataclass(frozen=True)
    class PlainDataclass:
        value: int

    with pytest.raises(TypeError, match="Duplicate tagged union tag 'circle'"):
        TypeAdapter(TaggedUnion[SchemaCircle | OtherCircle])
    with pytest.raises(TypeError, match="Duplicate tagged union tag 'box'"):
        TypeAdapter(TaggedUnion[SchemaBox[int] | SchemaBox[str]])
    with pytest.raises(TypeError, match="decorated with @case"):
        TypeAdapter(Annotated[PlainDataclass, UnionSchema()])
    with pytest.raises(TypeError, match="decorated with @case"):
        TypeAdapter(Annotated[int, UnionSchema()])


@final
@case
class SchemaAliased:
    value: Annotated[int, Field(alias="wire_value")]
    tag: Literal["aliased"] = tag()


@final
@case
class SchemaSerializationAlias:
    value: Annotated[int, Field(serialization_alias="wire_value")]
    tag: Literal["serialization_alias"] = tag()


@pytest.mark.parametrize("case_type", [SchemaAliased, SchemaSerializationAlias])
def test_case_field_aliases_are_rejected_explicitly(case_type: type[SchemaAliased] | type[SchemaSerializationAlias]):
    with pytest.raises(TypeError, match="without Pydantic aliases"):
        TypeAdapter(TaggedUnion[case_type])
