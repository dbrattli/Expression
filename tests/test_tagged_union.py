"""Public case declarations have the same contracts as ordinary frozen dataclasses."""

from __future__ import annotations

from collections.abc import Callable
from copy import copy, deepcopy
from dataclasses import FrozenInstanceError, InitVar, asdict, dataclass, field, fields, replace
from operator import lt
from pickle import dumps, loads
from typing import Any, ClassVar, Generic, Literal, TypeAlias, TypeVar, assert_never, assert_type, final

import pytest

from expression import TaggedUnion, case, tag


_T = TypeVar("_T", covariant=True)


@final
@case
class Circle:
    radius: float
    tag: Literal["circle"] = tag()

    def area(self) -> float:
        return 3.14159 * self.radius**2


@final
@case
class Rectangle:
    width: float
    height: float
    tag: Literal["rectangle"] = tag()

    def area(self) -> float:
        return self.width * self.height


Shape: TypeAlias = TaggedUnion[Circle | Rectangle]


@final
@case
class Just(Generic[_T]):
    value: _T
    tag: Literal["just"] = tag()


@final
@case
class Missing:
    tag: Literal["missing"] = tag()


Maybe: TypeAlias = TaggedUnion[Just[_T] | Missing]


# The payload type does not exist when the decorator runs. Only the tag's
# annotation can be resolved eagerly; payload annotations belong to consumers.
@final
@case
class Folder:
    name: str
    children: tuple[Tree, ...]
    tag: Literal["folder"] = tag()


@final
@case
class Leaf:
    name: str
    tag: Literal["leaf"] = tag()


Tree: TypeAlias = TaggedUnion[Folder | Leaf]


@final
@case(kw_only=True)
class Request:
    path: str
    retries: int = 3
    headers: dict[str, str] = field(default_factory=dict[str, str])
    tag: Literal["request"] = tag()


@final
@case
class Labelled:
    number: int
    label: str = field(default="", kw_only=True)
    tag: Literal["labelled"] = tag()


@final
@case(repr=False)
class SecurePassword:
    password: str
    tag: Literal["password"] = tag()

    def __repr__(self) -> str:
        return "SecurePassword('********')"

    def __str__(self) -> str:
        return "********"


def describe(shape: Shape) -> str:
    match shape:
        case Circle(radius):
            assert_type(radius, float)
            return f"circle of radius {radius}"
        case Rectangle(width, height):
            assert_type(width, float)
            assert_type(height, float)
            return f"rectangle {width} by {height}"
        case _:
            assert_never(shape)


def test_multifield_cases_construct_and_match():
    assert_type(Circle(2.0), Circle)
    assert_type(Rectangle(3.0, 4.0), Rectangle)
    assert describe(Circle(2.0)) == "circle of radius 2.0"
    assert describe(Rectangle(width=3.0, height=4.0)) == "rectangle 3.0 by 4.0"
    assert Rectangle(3.0, 4.0).area() == 12.0
    assert Circle.__match_args__ == ("radius",)
    assert Rectangle.__match_args__ == ("width", "height")
    assert Missing.__match_args__ == ()


def test_case_tag_is_fixed_and_not_a_constructor_argument():
    value = Rectangle(3.0, 4.0)
    assert value.tag == "rectangle"
    assert not next(item for item in fields(value) if item.name == "tag").init
    with pytest.raises(TypeError):
        Rectangle(**{"width": 3.0, "height": 4.0, "tag": "circle"})  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        Circle(**{"tag": "circle"})  # type: ignore[arg-type]


def test_generic_cases_preserve_payload_types_and_nesting():
    assert_type(Just(42), Just[int])
    assert_type(Just[int](42), Just[int])
    value: Maybe[Shape] = Just(Rectangle(3.0, 4.0))
    match value:
        case Just(Rectangle(width, height)):
            assert width * height == 12.0
        case _:
            pytest.fail("The nested cases did not match")
    assert Just(None) != Missing()
    assert Just(Missing()) != Missing()
    assert Just(Just(None)) != Just(None)


def test_tags_narrow_to_the_correct_case():
    def radius(shape: Shape) -> float | None:
        if shape.tag == "circle":
            assert_type(shape, Circle)
            return shape.radius
        assert_type(shape, Rectangle)
        return None

    assert radius(Circle(2.0)) == 2.0
    assert radius(Rectangle(3.0, 4.0)) is None


def test_dataclass_equality_and_hashing():
    assert Circle(2.0) == Circle(2.0)
    assert Circle(2.0) != Circle(3.0)
    assert Circle(2.0) != Rectangle(2.0, 2.0)
    assert hash(Circle(2.0)) == hash(Circle(2.0))
    assert len({Circle(2.0), Circle(2.0), Rectangle(2.0, 2.0)}) == 2
    with pytest.raises(TypeError):
        hash(Just([1, 2]))
    compare: Callable[[Any, Any], bool] = lt
    with pytest.raises(TypeError):
        compare(Circle(1.0), Circle(2.0))
    with pytest.raises(TypeError):
        compare(Circle(1.0), Rectangle(2.0, 3.0))


def test_unit_cases_are_ordinary_values_without_automatic_singletons():
    first = Missing()
    second = Missing()
    assert first == second
    assert first is not second
    assert asdict(first) == {"tag": "missing"}
    assert replace(first) == first


def test_copy_deepcopy_replace_and_pickle():
    value = Just([Rectangle(3.0, 4.0)])
    shallow = copy(value)
    deep = deepcopy(value)
    restored = loads(dumps(value))
    assert shallow == deep == restored == value
    assert shallow.value is value.value
    assert deep.value is not value.value
    assert restored.value is not value.value
    assert replace(Rectangle(3.0, 4.0), width=5.0) == Rectangle(5.0, 4.0)
    assert loads(dumps(Missing())) == Missing()
    assert asdict(value) == {
        "value": [{"width": 3.0, "height": 4.0, "tag": "rectangle"}],
        "tag": "just",
    }
    with pytest.raises((ValueError, TypeError)):
        replace(value, tag="missing")


def test_cases_are_frozen_including_new_attributes():
    value = Circle(2.0)
    for name, replacement in (("radius", 3.0), ("tag", "rectangle"), ("extra", 1)):
        with pytest.raises(FrozenInstanceError):
            setattr(value, name, replacement)
    with pytest.raises(FrozenInstanceError):
        delattr(value, "radius")


def test_runtime_subclassing_is_rejected():
    for cls in (Circle, Rectangle, Just, Missing):
        with pytest.raises(TypeError):
            type("ExtraCase", (cls,), {})


def test_defaults_keyword_only_fields_and_custom_representation():
    first = Request(path="/items")
    second = Request(path="/items")
    assert first.retries == 3
    assert first.headers == {}
    assert first.headers is not second.headers
    assert Request.__match_args__ == ()
    assert Labelled.__match_args__ == ("number",)
    assert Labelled(1, label="one").label == "one"
    assert str(SecurePassword("secret")) == "********"
    assert repr(SecurePassword("secret")) == "SecurePassword('********')"
    assert "secret" not in repr(SecurePassword("secret"))


def test_recursive_payload_annotations_remain_deferred():
    value: Tree = Folder("root", (Leaf("file"), Folder("empty", ())))
    assert asdict(value) == {
        "name": "root",
        "children": (
            {"name": "file", "tag": "leaf"},
            {"name": "empty", "children": (), "tag": "folder"},
        ),
        "tag": "folder",
    }
    assert loads(dumps(value)) == value


def test_plain_mixins_and_post_init_validation_are_supported():
    class Named:
        def description(self) -> str:
            return type(self).__name__

    @final
    @case
    class Positive(Named):
        value: int
        tag: Literal["positive"] = tag()

        def __post_init__(self) -> None:
            if self.value <= 0:
                raise ValueError("Expected a positive value")

    assert Positive(1).description() == "Positive"
    with pytest.raises(ValueError, match="positive"):
        Positive(0)


def _declaration(annotations: dict[str, object], attributes: dict[str, object]) -> type[object]:
    return type("Invalid", (), {"__module__": __name__, "__annotations__": annotations, **attributes})


@pytest.mark.parametrize(
    ("annotations", "attributes"),
    [
        ({"value": int}, {}),
        ({}, {"tag": tag()}),
        ({"tag": str}, {"tag": tag()}),
        ({"tag": Literal["x", "y"]}, {"tag": tag()}),
        ({"tag": Literal[1]}, {"tag": tag()}),
        ({"tag": ClassVar[Literal["x"]]}, {"tag": tag()}),
        ({"tag": "Literal[missing]"}, {"tag": tag()}),
        ({"tag": Literal["x"]}, {"tag": "x"}),
        ({"tag": Literal["x"]}, {"tag": field(default="x", init=False)}),
        ({"tag": Literal["x"], "value": int}, {"tag": tag(), "value": field(default=1, init=False)}),
        ({"tag": Literal["x"], "value": InitVar[int]}, {"tag": tag()}),
        ({"tag": Literal["x"], "other": str}, {"tag": tag(), "other": tag()}),
    ],
)
def test_invalid_case_declarations_are_rejected(annotations: dict[str, object], attributes: dict[str, object]):
    with pytest.raises(TypeError):
        case(_declaration(annotations, attributes))


def test_already_decorated_dataclasses_are_rejected():
    @dataclass
    class Existing:
        value: int
        tag: Literal["existing"] = tag()

    with pytest.raises(TypeError):
        case(Existing)
    with pytest.raises(TypeError):
        case(Circle)


def test_dataclass_inheritance_is_rejected():
    @dataclass
    class Existing:
        value: int

    class Inherited(Existing):
        tag: Literal["inherited"] = tag()

    with pytest.raises(TypeError):
        case(Inherited)


def test_custom_init_is_rejected():
    class Custom:
        value: int
        tag: Literal["custom"] = tag()

        def __init__(self, value: int) -> None:
            self.value = value

    with pytest.raises(TypeError):
        case(Custom)


def test_local_literal_import_resolves_with_bare_case_decorator():
    from typing import Literal as L

    @final
    @case
    class Local:
        value: int
        tag: L["local"] = tag()

    assert Local(42).tag == "local"


def test_local_literal_import_resolves_with_case_decorator_factory():
    from typing import Literal as L

    @final
    @case()
    class Local:
        value: int
        tag: L["local"] = tag()

    assert Local(42).tag == "local"


def test_reused_case_decorator_resolves_locals_where_each_class_is_declared():
    decorate = case()

    def first() -> object:
        from typing import Literal as L

        @final
        @decorate
        class First:
            tag: L["first"] = tag()

        return First()

    def second() -> object:
        from typing import Literal as L

        @final
        @decorate
        class Second:
            tag: L["second"] = tag()

        return Second()

    assert getattr(first(), "tag") == "first"
    assert getattr(second(), "tag") == "second"


def test_inferred_tag_precedes_payload_and_keeps_dataclass_contract():
    @final
    @case
    class Identifier:
        tag: Literal["identifier"] = tag(repr=True)
        value: int

    identifier = Identifier(42)
    assert_type(identifier.tag, Literal["identifier"])
    assert identifier.tag == "identifier"
    assert Identifier.tag == "identifier"
    assert fields(Identifier)[0].default == "identifier"
    assert Identifier.__match_args__ == ("value",)
    assert asdict(identifier) == {"tag": "identifier", "value": 42}
    assert repr(identifier).endswith("Identifier(tag='identifier', value=42)")


def test_inferred_tag_without_postponed_annotations():
    namespace: dict[str, Any] = {"__name__": __name__}
    source = """
from typing import Literal
from expression import case, tag

@case
class Identifier:
    value: int
    tag: Literal["identifier"] = tag()
"""
    exec(compile(source, "<case-declaration>", "exec", dont_inherit=True), namespace)
    identifier = namespace["Identifier"](42)
    assert identifier.tag == "identifier"
    assert asdict(identifier) == {"value": 42, "tag": "identifier"}


def test_tag_rejects_explicit_value_argument():
    dynamic_tag: Any = tag
    with pytest.raises(TypeError):
        dynamic_tag("explicit")
