"""Explicit, closed tagged unions understood by Python type checkers.

Declare each alternative with ``@final`` and ``@case``, give it a fixed literal
``tag``, then combine the alternatives in a ``TaggedUnion[A | B]`` type alias.
The alias supplies optional Pydantic decoding without hiding its case types.
"""

from __future__ import annotations

import sys
from collections.abc import Callable
from dataclasses import Field, dataclass, field, fields, is_dataclass
from inspect import currentframe, signature
from typing import (
    Annotated,
    Literal,
    Protocol,
    TypeAlias,
    TypeVar,
    dataclass_transform,
    final,
    get_args,
    get_origin,
    get_type_hints,
    overload,
)

from ._union_schema import UnionSchema


_T = TypeVar("_T")
_Tag = TypeVar("_Tag", bound=str)


class _TaggedCase(Protocol):
    @property
    def tag(self) -> str: ...


_Case = TypeVar("_Case", bound=_TaggedCase)
TaggedUnion: TypeAlias = Annotated[_Case, UnionSchema()]


def tag(value: _Tag, *, init: Literal[False] = False, repr: bool = False) -> _Tag:
    """Declare a fixed discriminator excluded from a case's constructor.

    Annotate the field as ``tag: Literal['name'] = tag('name')``. The literal
    remains visible to checkers, while construction cannot override its value.
    """
    if type(value) is not str:
        raise TypeError("A case tag must be a string")
    if init is not False:
        raise TypeError("A case tag cannot be a constructor parameter")
    return field(default=value, init=False, repr=repr, metadata={"expression.tag": True})


@overload
def case(_cls: type[_T], /, *, repr: bool = True, kw_only: bool = False) -> type[_T]: ...


@overload
def case(*, repr: bool = True, kw_only: bool = False) -> Callable[[type[_T]], type[_T]]: ...


@dataclass_transform(frozen_default=True, field_specifiers=(tag, field))
def case(
    _cls: type[_T] | None = None, /, *, repr: bool = True, kw_only: bool = False
) -> type[_T] | Callable[[type[_T]], type[_T]]:
    """Create a frozen case dataclass with runtime subclass rejection.

    Apply ``@final`` as well for static subclass rejection. Cases have ordinary
    dataclass equality, hashing, copying and matching. Payload fields participate
    in construction; only the fixed literal ``tag`` is excluded. Unit cases are
    ordinary values rather than automatically interned singletons.
    """

    def transform(cls: type[_T]) -> type[_T]:
        return apply(cls, _declaration_namespace())

    def apply(cls: type[_T], namespace: dict[str, object]) -> type[_T]:
        if is_dataclass(cls):
            raise TypeError("@case requires a new class without a dataclass or case base")
        if "__init__" in vars(cls):
            raise TypeError("@case generates __init__; use __post_init__ for payload checks")
        transformed = dataclass(cls, frozen=True, repr=repr, kw_only=kw_only)
        _validate_case(transformed, namespace)
        config = dict(getattr(transformed, "__pydantic_config__", {}))
        config["revalidate_instances"] = "always"
        setattr(transformed, "__pydantic_config__", config)
        setattr(transformed, "__init_subclass__", classmethod(_reject_subclass))
        return final(transformed)

    return transform if _cls is None else apply(_cls, _declaration_namespace())


def _declaration_namespace() -> dict[str, object]:
    # Resolve postponed tag annotations at the decorator call site, including
    # function-local imports and aliases. Copy locals without retaining frames.
    frame = currentframe()
    try:
        if frame is None or frame.f_back is None or frame.f_back.f_back is None:
            return {}
        return frame.f_back.f_back.f_locals.copy()
    finally:
        del frame


def _reject_subclass(cls: type[object], /, **kwargs: object) -> None:
    raise TypeError(f"Tagged union cases are final; cannot define {cls.__name__}")


def _validate_case(cls: type[object], namespace: dict[str, object]) -> None:
    if not is_dataclass(cls):
        raise TypeError("A case must be a dataclass")
    declared = fields(cls)
    discriminator = _case_discriminator(cls, declared, namespace)
    for item in declared:
        if item.name != "tag" and (not item.init or item.metadata.get("expression.tag")):
            raise TypeError(f"Payload field {item.name!r} must be a constructor field; only tag uses tag()")
    names = {item.name for item in declared}
    constructor_parameters = tuple(signature(cls.__init__).parameters)[1:]
    if any(name not in names for name in constructor_parameters):
        raise TypeError("InitVar fields are not supported in tagged union cases")
    setattr(cls, "__tagged_union_case__", discriminator.default)


def _case_discriminator(
    cls: type[object], declared: tuple[Field[object], ...], namespace: dict[str, object]
) -> Field[object]:
    discriminator = next((item for item in declared if item.name == "tag"), None)
    if discriminator is None or discriminator.init or not discriminator.metadata.get("expression.tag"):
        raise TypeError("A case must declare tag: Literal['name'] = tag('name')")
    literal = _resolve_tag_annotation(cls, discriminator.type, namespace)
    if get_origin(literal) is not Literal or get_args(literal) != (discriminator.default,):
        raise TypeError("The tag annotation must be a single Literal matching its tag() value")
    return discriminator


def _resolve_tag_annotation(cls: type[object], annotation: object, localns: dict[str, object]) -> object:
    # Resolve only the tag: other payloads may refer to this case or to a union
    # alias that does not exist until after the class declaration.
    def holder() -> None:
        pass

    holder.__annotations__ = {"return": annotation}
    module = sys.modules.get(cls.__module__)
    namespace = vars(module) if module is not None else {}
    try:
        return get_type_hints(holder, globalns=namespace, localns={**localns, **vars(cls)}, include_extras=True)[
            "return"
        ]
    except (NameError, TypeError) as error:
        raise TypeError("A case tag must use a resolvable Literal annotation") from error


__all__ = ["TaggedUnion", "case", "tag"]
