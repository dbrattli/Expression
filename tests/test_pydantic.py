from typing import Annotated, Any

import pytest
from pydantic import BaseModel, Field, create_model
from pydantic.annotated_handlers import GetCoreSchemaHandler
from pydantic_core import core_schema

from expression import Option, Result


class CustomString(str):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: GetCoreSchemaHandler) -> Any:
        return core_schema.no_info_after_validator_function(cls, handler(str))


@pytest.mark.parametrize("type_", [Option, Result])
class TestNestedOrCustomType:
    @staticmethod
    def create_model(name: str | None, type_: Any, type_arg: Any) -> type[BaseModel]:
        _type_arg = type_arg if type_ is Option else (type_arg, Any)
        return create_model(name or "_", value=(type_.__class_getitem__(_type_arg), Field(...)))  # type: ignore

    def test_option_create_model(self, type_: Any):
        if type_ is Result:
            pytest.skip("This test is for Option")

        class expect(BaseModel):
            value: type_[int]

        target = self.create_model(None, type_, int)
        target_schema = target.model_json_schema()
        expect_schema = expect.model_json_schema()
        for schema in (target_schema, expect_schema):
            schema.pop("title")
        assert target_schema == expect_schema

    def test_result_create_model(self, type_: Any):
        if type_ is Option:
            pytest.skip("This test is for Result")

        class expect(BaseModel):
            value: type_[int, Any]

        target = self.create_model(None, type_, int)
        target_schema = target.model_json_schema()
        expect_schema = expect.model_json_schema()
        for schema in (target_schema, expect_schema):
            schema.pop("title")
        assert target_schema == expect_schema

    def test_nested_type(self, type_: Any):
        target = self.create_model(None, type_, Annotated[Annotated[int, 1], 2])
        origin = self.create_model(None, type_, int)

        target_schema = target.model_json_schema()
        origin_schema = origin.model_json_schema()
        assert target_schema == origin_schema

    def test_build_custom_type(self, type_: Any):
        _ = self.create_model(None, type_, CustomString)

    def test_build_nested_custom_type(self, type_: Any):
        _ = self.create_model(None, type_, Annotated[Annotated[CustomString, 1], 2])
