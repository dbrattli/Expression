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
    def create_model(name: str | None, type_: Any, *type_arg: Any) -> type[BaseModel]:
        return create_model(name or "_", value=(type_.__class_getitem__(type_arg), Field(...)))

    def test_nested_type(self, type_: Any):
        target = self.create_model(None, type_, Annotated[Annotated[int, 1], 2], Any)
        origin = self.create_model(None, type_, int, Any)

        target_schema = target.model_json_schema()
        origin_schema = origin.model_json_schema()
        assert target_schema == origin_schema

    def test_build_custom_type(self, type_: Any):
        _ = self.create_model(None, type_, CustomString, Any)

    def test_build_nested_custom_type(self, type_: Any):
        _ = self.create_model(None, type_, Annotated[Annotated[CustomString, 1], 2], Any)
