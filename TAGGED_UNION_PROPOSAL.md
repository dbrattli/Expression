# Tagged unions and typed computations: implementation and rationale

**Status:** Implemented for the next major version of Expression.
**Minimum Python:** 3.11. **Optional Pydantic:** 2.10 or later, below 3.

Expression now represents tagged unions as explicit, frozen, final case classes
combined in public type aliases. Each case declares only its own payload. The
same public declaration API defines custom unions and the built-in `Some`,
`Nothing`, `Ok`, and `Error` cases. Computations use typed scopes with ordinary
functions and coroutines.

This document records the implemented design and its tradeoffs. It replaces the
candidate comparison from the original proposal: the selected representation was
previously called **Candidate C**, not Candidate A. The migration steps and
additional usage examples are in the [migration guide](docs/guides/migration-major.md).

## Follow-up: computation-expression direction

The current code uses typed scopes, but the design goal has been clarified:
Expression should preserve the meaning of F# computation expressions rather
than treat scopes as their replacement. The [F# CE investigation](investigations/fsharp_ce/README.md)
compares executable F# builders with Python computation objects, direct
`yield from operation()` binding, terminal return/return-from, and the original
`yield value` spelling. It records both working typed behavior and concrete
limits involving Zero, Combine, None, and error-channel checking. No new CE API
has been exported; the scope implementation remains the current implementation
while that semantic contract is settled.

## Why we changed the representation

The previous `@tagged_union` decorator declared every alternative's payload on
one class, even though an instance held only one alternative. For example,
`Option[T]` declared both `.some` and `.none`. A type checker could therefore
accept `.some` on an empty option: the class annotation said that attribute
existed. Runtime checks could reject the access, but could not repair that static
contract. The decorator also had to implement active-case construction and
customize dataclass behavior.

The new representation makes the alternatives visible in Python source. A
`Some[T]` has `.some`; a `Nothing` does not. A checker can narrow the union
using class patterns, `isinstance`, or literal tags and verify exhaustive handling.
The implementation uses Python's dataclass and union typing mechanisms without a
checker plugin or generated case types hidden behind a decorator.

We accepted breaking changes to runtime identity, construction, matching, and
computation syntax to make that contract accurate.

## The public tagged-union abstraction

```python
from typing import Literal, TypeAlias, final

from expression import TaggedUnion, case, tag


@final
@case
class Circle:
    radius: float
    tag: Literal["circle"] = tag("circle")


@final
@case
class Rectangle:
    width: float
    height: float
    tag: Literal["rectangle"] = tag("rectangle")


Shape: TypeAlias = TaggedUnion[Circle | Rectangle]


def area(shape: Shape) -> float:
    match shape:
        case Circle(radius):
            return 3.14159 * radius * radius
        case Rectangle(width, height):
            return width * height


assert area(Rectangle(3.0, 4.0)) == 12.0
```

The three helpers have distinct responsibilities:

| API | Responsibility |
|---|---|
| `@case` | Generate a frozen dataclass, validate the case declaration, and reject ordinary runtime subclassing. |
| `tag("circle")` | Define a fixed discriminator excluded from constructor arguments and positional class patterns. |
| `TaggedUnion[Circle \| Rectangle]` | Keep the alternatives visible to checkers and attach metadata for optional Pydantic decoding. |

`@final` remains explicit because `dataclass_transform` describes fields and
constructors; it cannot tell checkers that a custom decorator makes a class final.
There are three separate guarantees: the alias enumerates alternatives, `@final`
rejects subclassing statically, and `@case` rejects it at runtime. Defining another
case does not add it to an existing alias.

`TaggedUnion` is implemented as `Annotated` metadata over its argument. It does
not create a nominal class, registry, constructor namespace, or new inheritance
hierarchy. Its structural typing bound requires a tag, while schema construction
checks actual `@case` membership and distinct tag values. Static typing alone
does not prove those runtime declaration properties.

Cases support generics, multiple payload fields, defaults, default factories,
keyword-only construction, methods, and plain mixins. Recursive payload
annotations may refer to the union alias declared later. Only the tag annotation
needs resolving while the decorator runs.

Custom constructors, dataclass inheritance, `InitVar`, and non-tag `init=False`
fields are rejected. Keeping payloads in the generated constructor gives parsing
a consistent account of the data being validated. Use `__post_init__` for custom
payload checks. Frozen cases do not make mutable payloads immutable, and ordinary
constructor annotations do not validate arbitrary external input.

Cases use ordinary dataclass equality, copying, pickling, and hashing, subject to
payload hashability. They do not define cross-case ordering. Unit cases have
value semantics and are not automatically singletons. The implementation does
not request slots: built-in cases inherit `PipeMixin`, which already supplies an
instance dictionary, and the nonslotted representation supports generic
construction across the supported runtimes.

Source: [public declarations](expression/core/tagged_union.py),
[schema metadata](expression/core/_union_schema.py).

## How Option actually works

`Some` is now a class and constructor, not a factory returning a shared `Option`
class. `Nothing` is a separate, nongeneric case class; `Nothing()` is its
canonical instance. Both classes use the public `@case` decorator and fixed tags.

The following is the declaration structure, with methods and singleton machinery
omitted. `UnionSchema` is an internal implementation detail, not an additional
helper users need for ordinary custom unions:

```python
from typing import Annotated, Generic, Literal, TypeAlias, TypeVar, final

from expression import case, tag
from expression.core._union_schema import UnionSchema

T = TypeVar("T", covariant=True)


@final
@case
class Some(Generic[T]):
    some: T
    tag: Literal["some"] = tag("some")


@final
@case
class Nothing:
    tag: Literal["none"] = tag("none")


Option: TypeAlias = Annotated[
    Some[T] | Nothing,
    UnionSchema(canonical_values=(Nothing(),)),
]
```

The actual classes also inherit `PipeMixin` and implement their fluent methods.
The alias means `Some[T] | Nothing` to the checker. Its metadata uses the same
schema implementation as `TaggedUnion`, with one deliberate specialization:
decoding the empty case must restore the canonical `Nothing()` instance.
`Nothing` itself preserves identity through construction, copying, and
pickling. Ordinary custom unit cases do not acquire this singleton contract.

Consequently, Option is neither the former single container class nor an erased
`T | None` representation. `Some(None)`, `Nothing()`, and `Some(Nothing())` remain
three distinct values. The wrapped representation preserves fluent operations
and nested options without interpreting a payload's value as absence.

```python
from typing import assert_never

from expression import Nothing, Option, Some


def describe(value: Option[int]) -> str:
    match value:
        case Some(number):
            return str(number)
        case Nothing():
            return "missing"
        case _:
            assert_never(value)


assert describe(Some(42)) == "42"
assert describe(Nothing()) == "missing"
assert Some(42).map(str) == Some("42")
```

`Nothing` is the case class, so construction and matching use the same name:
`Nothing()` and `case Nothing()`. This avoids a separate `NothingType` pattern
name. Construction calls the class but reuses its canonical instance; matching
does not call the constructor. `NOTHING: Final = Nothing()` is defined once in
`option.py` and exported from `expression` as the shared value. Library operations and callers can return
`NOTHING` without a constructor call while still matching `case Nothing()`.
A local alias such as `Nothing_ = NOTHING` is also possible.

Use `Nothing()` in a class pattern. Bare `case Nothing` is a capture pattern;
it does not test the singleton. For runtime checks, use case classes such as
`Some` or `(Some, Nothing)`. `Option[T]` is an annotation, not a nominal class
for construction, subclassing, or runtime instance checks.

The same naming pattern can be used for custom unit cases: export a case class
and optionally a shared instance under distinct names. Merely assigning an
instance does not guarantee singleton identity. A class pattern such as
`case Nothing()` does not invoke the constructor; only an expression such as
`Nothing()` does. The public `TaggedUnion` API currently supplies ordinary
unit cases, not general singleton lifecycle support. See
[unit cases, shared values, and singletons](docs/guides/migration-major.md#unit-cases-shared-values-and-singletons)
for the supported custom-union pattern and its tradeoffs.

Source: [Option and its cases](expression/core/option.py).

## Result, Try, and precise fluent operations

`Ok[T]` contains `.ok`; `Error[E]` contains `.error`. Their implemented alias is
`Result: TypeAlias = TaggedUnion[Ok[T] | Error[E]]`. Both cases use `@final`,
`@case`, and a fixed literal tag, just like user-defined cases.

Each class is parameterized only by its own payload. `Ok(42)` infers `Ok[int]`
and `Error("failed")` infers `Error[str]`; constructing either requires no type
argument for a channel it does not contain. `Try[T]` is `Result[T, Exception]`.
`Success` and `Failure` remain convenience constructors producing `Ok` and `Error`.

Fluent methods have case-specific signatures. For example, `Some.map` returns a
`Some` of the mapped type, while `Nothing.map` returns `Nothing` without
calling the mapper. Similarly, `Ok.map` transforms success and `Error.map`
preserves the error. Their signatures combine correctly when the receiver is a
union. Bind and recovery retain the possible outcomes of both the original
value and the callback. `Never` describes an impossible callback input where
appropriate; no phantom success/error parameter is added to the case class.

Functional helpers and piping remain available. Python's contextual inference
still has limits: complex curried callbacks can require named, annotated
functions, and empty-case conversion to invariant collections may need a result
annotation or a free helper. The migration guide documents those forms. Boolean
instance predicates do not promise to narrow their receiver; use class/tag tests
or free guards such as `option.is_some` and `result.is_ok`.

Source: [Result](expression/core/result.py), [Try](expression/core/try_.py),
[consumer typing contracts](tests/typing_contracts.py).

## Why computations use typed scopes

Correct case types alone cannot fix the old generator computation protocol.
Its yielded, sent, and returned types coupled unrelated intermediate payloads,
and its Result iteration contract did not carry the error type to the runner.
That allowed computations to bind the wrong error type or effect family without
an accurate static description of the resulting failure.

The implemented API uses ordinary functions. A scope fixes the effect family
and, for Result, the error type. Each call to `bind` independently infers its
payload type. The body's return annotation describes the final successful value;
the decorator exposes the corresponding container to callers.

```python
from expression import Error, Ok, Result, effect


def parse_count(text: str) -> Result[int, str]:
    return Ok(int(text)) if text.isdigit() else Error("invalid count")


@effect.result
def describe_count(scope: effect.ResultScope[str], text: str) -> str:
    count = scope.bind(parse_count(text))  # int
    label = scope.bind(Ok("items"))  # str
    return f"{count} {label}"


assert describe_count("3") == Ok("3 items")
assert describe_count("bad") == Error("invalid count")
```

`@effect.option` supplies `OptionScope`. The async variants are
`@effect.async_result` and `@effect.async_option`: await the I/O operation to
obtain a container, then call `scope.bind(container)`. There is no requirement
that different binds have the same payload type.

Binding `Error` or `Nothing()` aborts that invocation using an internal,
owner-specific control signal. Normal `finally` cleanup runs; unrelated
exceptions and cancellation propagate. The first bound failure remains the
outcome even if user code catches the internal signal. Each scope checks its
active lifetime, thread, and task, so it cannot be reused after completion or
bound from another execution context. Nested invocations have separate scopes.

Callback runners (`run_result`, `run_option`, and their async equivalents)
support bound methods. Decorators preserve external parameter typing. Runtime
introspection hides the supplied scope parameter and omits the body's return
annotation, which describes the payload rather than the wrapped result; the
original annotations remain available through `__wrapped__`.

A normal return, including `None`, is success: `Some(None)` or `Ok(None)`.
Absence and failure require binding `Nothing()` or `Error`. Ordinary Python
fall-through still returns `None`, so return annotations remain important.
Containers are no longer awaitable, and iteration simply yields zero or one
successful payloads; it does not bind an effect.

No generator compatibility adapter is included. The sequence computation builder
retains its existing generator behavior. `effect.try_` and `effect.async_try`
constrain explicit Result errors to exceptions; they do not automatically catch
unexpected exceptions from the body.

Source: [Result scopes](expression/effect/result.py),
[Option scopes](expression/effect/option.py),
[invocation ownership](expression/effect/_scope.py).

## Serialization is part of the contract

The public union aliases carry optional Pydantic metadata so external data is
validated as a tagged case, including its payload types. Option's former raw
payload/null encoding could not distinguish an absent value from `Some(None)`.
The new encoding preserves that distinction and nesting:

| Value | Tagged representation |
|---|---|
| `Nothing()` | `{"tag": "none"}` |
| `Some(None)` | `{"tag": "some", "some": None}` |
| `Some(Nothing())` | `{"tag": "some", "some": {"tag": "none"}}` |
| `Ok(42)` | `{"tag": "ok", "ok": 42}` |
| `Error("failed")` | `{"tag": "error", "error": "failed"}` |

Use a Pydantic field annotated with the public alias, or `TypeAdapter(Option[int])`,
`TypeAdapter(Result[int, str])`, or `TypeAdapter(Shape)`. The schema requires a
known tag, rejects extra case fields, validates generic and nested payloads, and
preserves canonical `Nothing()`. Direct adapters for case classes retain ordinary
Pydantic dataclass behavior; they do not supply the union's wire contract.

Custom cases serialize with their declared Python field names. Pydantic field
aliases are rejected. Case-level validation metadata is supported; union-level
validation metadata on an alias nested in another union is rejected rather than
discarded. Recursive schemas preserve references and closed case shapes.

The built-in `.dict()` methods recursively encode supported containers and
payloads; arbitrary leaf encoding remains the caller's responsibility. Custom
cases retain ordinary dataclass facilities such as `asdict` rather than gaining
a built-in `.dict()` method.

Pydantic is optional. The minimum is 2.10.0 because earlier versions could resolve
Expression's deferred generic annotations against caller-local type variables,
silently losing payload validation. A repository regression covers that name
collision. Old raw/null Option data requires explicit migration; no legacy codec
is included.

Source: [schema construction](expression/core/_union_schema.py),
[built-in encoding](expression/core/_serialization.py),
[schema regressions](tests/test_union_schema.py).

## Alternatives and the choices we made

| Alternative | Why it was not selected |
|---|---|
| One concrete class with case factories (former Candidate A) | Keeps inactive payload attributes in the static class contract; a literal tag does not turn one class into separate payload types. |
| Public nominal base with sealed subclasses | Runtime sealing does not teach a checker that the base's subclass set is exhaustive. |
| Nominal wrapper containing a case union | Gives accurate narrowing through an extra `.case` layer, but adds indirection and a second representation to the public API. |
| Case classes with phantom family type parameters | Couples a constructor to types absent from its payload, mainly to accommodate the old computation protocol. |
| Erasing Option to a payload or `None` | Loses the uniform wrapped API and requires special handling of successful `None` and nesting. |
| Typed generator adapter | An isolated synchronous prototype recovers typed `yield from bind(...)`; it is not part of the public API. See the [investigation](investigations/typed_generators/README.md) for evidence and limits. |

Explicit cases cost more declaration lines than the old field-marker syntax and
repeat some fluent methods. We accept that cost because users and type checkers
see the same payload model, constructors are ordinary class constructors, and
matching uses standard Python patterns. The common decorator and schema layer
provide the reusable mechanics without hiding the alternatives.

## Compatibility and maintained evidence

This is a breaking major-version change. The old `@tagged_union` decorator and
`case()` field marker are removed; lowercase `tagged_union` is now a module
namespace. `Option.Some`, `Result.Ok`, direct union-class construction, and old
`case Option(...)` / `case Result(...)` patterns must be migrated. Cross-case
ordering, container awaiting, and generator-based Option/Result computations are
also removed. See the [migration guide](docs/guides/migration-major.md) for replacements.

The supported minimum is Python 3.11. The repository pins Pyright **1.1.414** in
[pre-commit](.pre-commit-config.yaml); the design relies on explicit unions and
dataclass typing, not on a checker-specific plugin. Versioned dependency
requirements live in [pyproject.toml](pyproject.toml).

The maintained evidence is executable repository coverage:

- [Case declarations](tests/test_tagged_union.py): construction, finality,
  defaults, generics, recursive annotations, dataclass behavior, and invalid declarations.
- [Option](tests/test_option.py) and [Result](tests/test_result.py): fluent and
  functional APIs, singleton behavior, nesting, and serialization.
- [Union schemas](tests/test_union_schema.py): tagged decoding, generic payloads,
  recursive references, exact fields, metadata isolation, and caller-name collisions.
- [Synchronous Result](tests/test_result_builder.py) and
  [Option](tests/test_option_builder.py) computations, their
  [async Result](tests/test_async_result_builder.py) and
  [async Option](tests/test_async_option_builder.py) counterparts, and
  [introspection](tests/test_scope_introspection.py): outcomes, ownership,
  cleanup, and callable contracts.
- [Positive typing contracts](tests/typing_contracts.py) and
  [negative consumers](typing_tests/negative.py), enforced by
  [the typing check](scripts/check_typing.py): inferred payloads, narrowing,
  exhaustive matching, invalid construction, and invalid computation bindings.

These tests, the implementation, and the migration guide define the delivered
contract. Historical experiments and their machine-local artifacts are not
prerequisites for reviewing or maintaining it.
