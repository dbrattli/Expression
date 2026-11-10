from __future__ import annotations

from typing import Literal

import pytest
from pydantic import BaseModel, TypeAdapter, ValidationError
from pydantic.json_schema import JsonSchemaValue

from expression import Nothing, Ok, Option, Result, Some


def _resolve(document: JsonSchemaValue, schema: JsonSchemaValue) -> JsonSchemaValue:
    if "allOf" in schema and len(schema["allOf"]) == 1:
        schema = schema["allOf"][0]
    while "$ref" in schema:
        reference: str = schema["$ref"]
        assert reference.startswith("#/$defs/")
        schema = document["$defs"][reference.removeprefix("#/$defs/")]
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
    for tag, payload_type in (("ok", "integer"), ("error", "string")):
        case = _case(schema, schema, tag)
        assert set(case["required"]) == {"tag", tag}
        assert set(case["properties"]) == {"tag", tag}
        assert case["properties"]["tag"]["const"] == tag
        assert case["properties"][tag]["anyOf"] == [{"type": payload_type}, {"type": "null"}]
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
    assert value.some.ok is Nothing


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
    assert parsed.child.some.child is Nothing
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
    assert parsed.optional is Nothing
    assert parsed.present == Some(1)
