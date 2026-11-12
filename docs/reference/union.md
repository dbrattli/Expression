(reference_union)=

# Tagged Unions

`TaggedUnion[Circle | Rectangle]` is a type alias over explicit case classes.
`Option` and `Result` use the same representation. Define cases with `@case`,
declare their fixed literal tags, and use `@final` for static subclass checking:

```python
from typing import Literal, TypeAlias, assert_never, final

from expression import TaggedUnion, case, tag

@final
@case
class Circle:
    radius: float
    tag: Literal["circle"] = tag()

@final
@case
class Rectangle:
    width: float
    height: float
    tag: Literal["rectangle"] = tag()

Shape: TypeAlias = TaggedUnion[Circle | Rectangle]

def area(shape: Shape) -> float:
    match shape:
        case Circle(radius):
            return 3.14159 * radius**2
        case Rectangle(width, height):
            return width * height
        case _:
            assert_never(shape)
```

Construct `Circle(2.0)` or `Rectangle(2.0, 3.0)`. The alias is used in annotations;
it is not a constructor or a pattern-matching class. `isinstance(shape, Circle)`
narrows the value to that case. Each case has only its own payload fields.

## Case declarations

`@case` creates a frozen dataclass and rejects runtime subclassing. Explicit
`@final` makes static checking reject subclassing as well. Cases have standard
dataclass equality, representation, copying, pickling, and hashing. Hashing
requires hashable payloads; ordering is not generated.

Every case declares one `tag: Literal["..."] = tag()`. The decorator derives the
tag value from its annotation; `tag()` does not accept a value argument.
Tags must be unique within a union. The tag is excluded from the constructor,
representation, and positional patterns. Payloads use ordinary annotations and may have defaults
or `dataclasses.field(default_factory=...)`. `InitVar` and payload fields with
`init=False` are not supported.

The annotation must contain exactly one string literal. Inference happens when
`@case` executes the class declaration, normally once during module import for
global cases. Instance construction, tag access, and pattern matching do not
repeat this work. A class declared inside a function is recreated each time
execution reaches its declaration.

Use `@case(kw_only=True)` for keyword-only payloads and `@case(repr=False)` when
providing a custom representation, for example to redact a password. A case
with no payload declares only its tag; separate instances compare equal but
are not automatically singletons. For families of named constants without
payloads, standard Python enums are usually sufficient.

## Tagged serialization

`dataclasses.asdict(Circle(2.0))` returns `{"radius": 2.0, "tag": "circle"}`.
With the optional Pydantic extra (Pydantic 2.11+), use the public alias at decoding
boundaries:

```python
from pydantic import TypeAdapter

adapter = TypeAdapter(Shape)
shape = adapter.validate_python({"tag": "circle", "radius": 2.0})
assert shape == Circle(2.0)
assert adapter.validate_json(adapter.dump_json(shape)) == shape
```

The tag selects the case before its payload is validated. Missing or unknown
tags and extra fields are rejected. Nested aliases and generic case payloads
retain their types. Direct adapters for individual case classes use Pydantic's
ordinary dataclass behavior; use `TaggedUnion[...]` for tagged decoding, even
when it contains a single case. Payloads use their Python field names; Pydantic
field aliases are rejected. Case-level validation metadata is preserved. A nested
union alias carrying additional union-level validators is rejected explicitly.

The lowercase `tagged_union` export is the module namespace for `TaggedUnion`,
`case`, and `tag`. It is no longer a decorator. See the
[migration guide](../guides/migration-major.md) for the former declaration syntax.

```{eval-rst}
.. automodule:: expression.core.tagged_union
    :members:
```
