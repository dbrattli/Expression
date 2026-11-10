from __future__ import annotations

from inspect import Parameter, Signature, signature, unwrap

import pytest

from expression import Ok, Some, effect
from expression.effect import OptionScope, ResultScope


def test_scope_signature_preserves_future_local_annotations_without_evaluating_them():
    class LocalValue:
        def __init__(self, text: str):
            self.text = text

    class LocalFailure:
        pass

    def body(scope: ResultScope[LocalFailure], value: LocalValue, /, *, suffix: str = "!") -> str:
        return scope.bind(Ok(value.text + suffix))

    computation = effect.result(body)
    external = signature(computation)
    assert tuple(external.parameters) == ("value", "suffix")
    assert external.parameters["value"].kind is Parameter.POSITIONAL_ONLY
    assert external.parameters["value"].annotation == "LocalValue"
    assert external.parameters["suffix"].kind is Parameter.KEYWORD_ONLY
    assert external.parameters["suffix"].default == "!"
    assert external.return_annotation is Signature.empty
    assert computation.__annotations__ == {"value": "LocalValue", "suffix": "str"}
    assert unwrap(computation) is body
    assert body.__annotations__ == {
        "scope": "ResultScope[LocalFailure]",
        "value": "LocalValue",
        "suffix": "str",
        "return": "str",
    }
    assert computation(LocalValue("hello")) == Ok("hello!")


@pytest.mark.asyncio
async def test_async_scope_signature_preserves_future_local_annotations():
    class LocalValue:
        pass

    async def body(scope: OptionScope, value: LocalValue) -> LocalValue:
        return scope.bind(Some(value))

    computation = effect.async_option(body)
    assert tuple(signature(computation).parameters) == ("value",)
    assert signature(computation).return_annotation is Signature.empty
    assert computation.__annotations__ == {"value": "LocalValue"}
    assert unwrap(computation) is body
    assert body.__annotations__ == {"scope": "OptionScope", "value": "LocalValue", "return": "LocalValue"}
    value = LocalValue()
    assert await computation(value) == Some(value)
