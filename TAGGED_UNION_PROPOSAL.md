# Tagged Unions and Computational Expressions — Major Version Proposal

**Status:** Major-version direction selected and implemented in the isolated
`feat/typed-unions-scopes` change on 2026-11-10. The minimum supported version is
Python 3.11. See the [migration guide](docs/guides/migration-major.md) for the
concrete public API. Sections describing the previous design and early probes
retain their historical context; implementation coverage is recorded below.

**Scope:** `tagged_union`, `Option`, `Result`, construction and matching, and
computational-expression typing.

**Recommendation:** Use explicit frozen, final case classes with public union
aliases, together with typed scopes as the primary API for synchronous and
asynchronous short-circuit computations. Accept breaking changes in a new major
version: preserving nominal container classes and the old generator protocol
does not constrain this design. The other candidates document alternatives;
a typed generator adapter is optional migration work, not part of the required
new core API.

## 1. Requirements and changed priorities

`Option` and `Result` should each describe a closed set of alternatives. `Some`
and `Nothing`, or `Ok` and `Error`, construct values belonging to that type.
Users should not be able to invent another case by subclassing a public base.

Expression previously used subclasses for `Option` and `Result`. Returning to an
open hierarchy would reintroduce the problem that motivated moving away from it.
Separate case classes are only a candidate if we address closure explicitly.

We want:

- A clear public `Option[T]` / `Result[T, E]` identity and a closed set of cases.
- Natural construction, fluent and pipe-friendly operations, and readable matching.
- Useful static checks for construction, case-specific access, and missing cases.
- Precise intermediate, final-return, and error types in computation expressions.
- Predictable dataclass, serialization, and tooling behavior on Python 3.11+.

An annotation such as `Option[T]` and a nominal runtime class named `Option` are
different requirements. A union alias provides the former but not the latter.
The recommended major version changes `isinstance(value, Option)`, `Option.Some`,
and `case Option(...)`. The public type is an alias of known case types, with
module namespaces for constructors and helpers. A closed set of alternatives
remains a requirement in every candidate.

The Fable-style design was previously rejected for its verbosity. With agents
writing declarations, that cost is less decisive. Reviewability, type accuracy,
and runtime simplicity now deserve more weight. Generated source still needs to
be understandable and maintainable.

## 2. Previous Expression design

The current declaration describes every case field on one class, although only
one case field exists on each instance. The following excerpt uses `T` for the
module's existing covariant type variable:

```python
@tagged_union(frozen=True, order=True)
class Option(Iterable[T], Awaitable[T], PipeMixin):
    tag: Literal["some", "none"] = tag()
    none: None = case()
    some: T = case()
```

Current construction and matching:

```python
value: Option[int] = Some(42)
empty: Option[int] = Nothing
mapped = value.map(str)

match value:
    case Option(tag="some", some=number):
        print(number)
    case Option(tag="none"):
        print("Nothing")

result: Result[int, str] = Ok(42)
match result:
    case Result(ok=number):
        print(number)
    case Result(error=message):
        print(message)
```

Pyright accepts both of these unsafe reads because `.some` is declared on every
`Option`, including in the known-empty branch:

```python
def unchecked(value: Option[int]) -> int:
    return value.some


def wrong_case(value: Option[int]) -> int:
    if value.tag == "none":
        return value.some
    return 0
```

A minimal declaration using the current decorator also accepts `Maybe()` and
`Maybe(some=1, none=None)` statically, although the runtime rejects both. The
existing `TypeGuard[Option[T]]` predicates return the same type they receive;
they do not distinguish the cases for the checker.

The implementation customizes construction, comparisons, freezing, copying,
pickling, and the active-case view of `__dataclass_fields__`. This machinery is
part of the complexity under investigation, beyond declaration verbosity.

The checkout contains uncommitted changes for unit-case caching, comparisons,
field metadata, and inactive-field errors. These are separate existing work,
not a shipped redesign. Earlier test totals and environment-specific Pyright
baselines have been removed because they were not revalidated here.

Sources: [tagged union implementation](expression/core/tagged_union.py),
[Option](expression/core/option.py), [Result](expression/core/result.py).

### Computational-expression typing gaps

`Result.__iter__` exposes `Generator[T, T, T]`, so the error type `E` is absent
from the generator contract. `ResultBuilder.__call__` also uses one success type
for yielded, sent, and returned values. This does not describe a workflow that
binds an `int`, then a `User`, and finally returns a `bool`.

The runner catches `EffectError` and casts `error.args[0]` to its expected
container. A caller-side probe accepts both of these declarations:

```python
@effect.result[int, str]()
def wrong_error_type() -> Generator[int, int, int]:
    value: int = yield from Error(123)
    return value


@effect.result[int, str]()
def wrong_family() -> Generator[int, int, int]:
    value: int = yield from Nothing
    return value
```

The declared result does not describe the possible failures. Fixing the union's
case fields alone cannot fix an error channel that the builder never receives
statically. `Result.__await__` likewise exposes the success type without `E`.

`None` also has special control-flow meaning today. A plain body returning `None`
uses `zero()`; a generator ending with `None` retains the accumulated result.
The new computation contract must distinguish a successful `None` payload from
absence or an omitted final result.

Sources: [base builder](expression/core/builder.py),
[result builder](expression/effect/result.py),
[async builder](expression/core/async_builder.py),
[result builder tests](tests/test_result_builder.py).

## 3. Current Fable Python design

### General discriminated unions

Fable emits a private common base, an explicit dataclass for each case, and a
public union alias. For example:

```fsharp
type Shape =
    | Circle of radius: float
    | Rectangle of width: float * height: float
```

The corresponding Python shape, omitting reflection declarations, is:

```python
from fable_library.union import Union, tagged_union


class _Shape(Union):
    @staticmethod
    def cases() -> list[str]:
        return ["Circle", "Rectangle"]


@tagged_union(0)
class Shape_Circle(_Shape):
    radius_: float


@tagged_union(1)
class Shape_Rectangle(_Shape):
    width_: float
    height_: float


type Shape = Shape_Circle | Shape_Rectangle
```

Handwritten Python can construct and match these cases directly:

```python
shape: Shape = Shape_Rectangle(10.0, 20.0)

match shape:
    case Shape_Circle(radius):
        print(radius)
    case Shape_Rectangle(width, height):
        print(width * height)
```

These are actual source-level case classes. Fable's `@tagged_union(index)` applies
`dataclass(eq=False)` to each, sets a numeric tag, and supplies a `fields` property.
The common `Union` implements F# equality, hashing, ordering, and formatting.
Expression would not need to adopt all that F# compatibility machinery.

The `type` statement shown here requires Python 3.12+. Expression would use
Python 3.10-compatible aliases instead.

### Result

The local generated `temp/fable-library-py/fable_library/result.py` contains this
form, with reflection omitted:

```python
class _FSharpResult_2[T, TERROR](Union):
    @staticmethod
    def cases() -> list[str]:
        return ["Ok", "Error"]


@tagged_union(0)
class Ok[T, TERROR](_FSharpResult_2[T, TERROR]):
    result_value: Any


@tagged_union(1)
class Error[T, TERROR](_FSharpResult_2[T, TERROR]):
    error_value: Any


type FSharpResult_2[T, TERROR] = Ok[T, TERROR] | Error[T, TERROR]
```

The `Any` payloads above are present in the inspected local generated artifact;
the architecture alone does not guarantee precise payload annotations everywhere.
Generated functions also use numeric-tag matches with `narrow(Ok, result)` before
reading fields. `narrow` is an identity function with a typing assertion, not a
runtime case check. Handwritten class patterns can narrow directly.

### Option is different

Fable's actual core option alias is:

```python
type Option[T] = option.SomeWrapper[T] | T | None
```

Options can be erased to a value or `None`, with wrappers where necessary, such
as nesting. This differs from the per-case representation for general unions and
`Result`. It is not a direct replacement for Expression's fluent option objects.

Sources: [Fable design](../Fable/src/Fable.Transforms/Python/PYTHON-UNION.md),
[compiler emission](../Fable/src/Fable.Transforms/Python/Fable2Python.Transforms.fs),
[runtime decorator](../Fable/src/fable-library-py/fable_library/union.py),
[option representation](../Fable/src/fable-library-py/fable_library/option.py).
Fable documents generated-code checking with Pyright's standard settings; the
strict checks below apply to the isolated Expression prototype.

## 4. Candidate A: one final concrete class and case factories

This keeps the current public model: `Some` is a function returning an `Option`,
and `Nothing` is an empty `Option` value. All cases use the same concrete class.

The intended usage remains:

```python
value: Option[int] = Some(42)
assert isinstance(value, Option)

match value:
    case Option(tag="some", some=number):
        print(number)
    case Option(tag="none"):
        print("Nothing")
```

`@final` can reject subclassing statically, and `__init_subclass__` can reject
ordinary subclass declarations at runtime. This must be implemented; the current
classes do not enforce that closure.

The unresolved part is improving storage and the static contract. Keeping every
case field annotated on one class retains the inactive-access problem. Checking
a `Literal` tag does not turn that class into a different case type. Matching on
the tag itself can check tag coverage, but does not establish the relationship
between that tag and case-specific payload attributes.

A plain factory function cannot be used as `case Some(number)`: Python class
patterns require a class object. This candidate therefore uses `case Option(...)`.

## 5. Candidate B: a closed nominal family with explicit case classes

This retains a public `Option[T]` base for annotations and `isinstance`, with
known cases implemented as subclasses. An ordinary extensible base is not an
acceptable solution: the family must be closed after defining its cases.

Illustrative declarations, with shared methods and runtime sealing omitted:

```python
from dataclasses import dataclass
from typing import Generic, NoReturn, TypeVar, final

T = TypeVar("T", covariant=True)


class Option(Generic[T]): ...  # Shared API; base construction and runtime closure need a design.


@final
@dataclass(frozen=True)
class Some(Option[T]):
    some: T


@final
@dataclass(frozen=True)
class NothingType(Option[NoReturn]):
    pass


Nothing = NothingType()
```

Desired usage:

```python
value: Option[int] = Some(42)
assert isinstance(value, Option)

match value:
    case Some(number):
        print(number)
    case NothingType():
        print("Nothing")
```

Here `Some` doubles as a constructor and a Python case type. Values belong to the
nominal `Option` family but have different concrete runtime classes. This
preserves nominal identity, but is an unselected alternative to the recommended
public union alias.

`@final` on leaves does not stop a new direct subclass of `Option`. Runtime
sealing must reject new sibling cases, leaf subclasses, and direct base
construction. That mechanism has not been prototyped here.

Even with runtime sealing, Pyright does not infer a closed set of subclasses
from `__init_subclass__`. The probe confirmed that handling both known cases
does not exhaust a parameter annotated with their common base. Case tests can
narrow, but the base alone does not provide exhaustive union checking.

## 6. Candidate C: explicit cases and a public union alias

This is the preferred general representation. Each case declares only the data
that exists in that case, and a source-level union lists the alternatives. The
examples use Python 3.10-compatible syntax; shared methods, singleton handling,
and runtime closure are omitted from the initial declarations.

### Cases parameterized by their payloads

```python
from dataclasses import dataclass
from typing import Generic, NoReturn, TypeAlias, TypeVar, final

T = TypeVar("T", covariant=True)


@final
@dataclass(frozen=True)
class Some(Generic[T]):
    some: T


@final
@dataclass(frozen=True)
class NothingType:
    pass


Nothing = NothingType()
Option: TypeAlias = Some[T] | NothingType
```

Generic annotations and exhaustive matching work:

```python
from typing_extensions import assert_never


def describe(value: Option[int]) -> str:
    match value:
        case Some(number):
            return str(number)
        case NothingType():
            return "Nothing"
        case _:
            assert_never(value)


value: Option[int] = Some(42)
empty: Option[NoReturn] = Nothing
```

The analogous Result declaration and usage would be:

```python
E = TypeVar("E", covariant=True)


@final
@dataclass(frozen=True)
class Ok(Generic[T]):
    ok: T


@final
@dataclass(frozen=True)
class Error(Generic[E]):
    error: E


Result: TypeAlias = Ok[T] | Error[E]


def describe_result(value: Result[int, str]) -> str:
    match value:
        case Ok(number):
            return str(number)
        case Error(message):
            return message
        case _:
            assert_never(value)
```

`Ok(42)` infers `Ok[int]`; `Error("message")` infers `Error[str]`. Neither
constructor requires an uninferable type argument for its absent channel.
An internal method-sharing base can use `Never` for that channel. `Never` is
available from `typing` on the Python 3.11 minimum.

The alias is a closed list of alternatives for annotations, rather than a public
nominal runtime class. It changes part of the requested type identity. Cases are
exposed as Python types as well as constructors.

### Fluent methods need their own typing contract

A shared `.map(...)` proof is insufficient to establish the whole API. With a
shared base specialized using `Never`, naive `Result[U, F]` callback signatures
can infer an unknown absent channel. Per-case precise methods worked in the
prototype: `Ok.map` returns `Ok[U]`, while `Error.map` returns the existing error.
For `bind`, a bounded result variable preserves the callback's actual result:

```python
R = TypeVar("R", bound="Ok[object] | Error[object]")


# On Ok[T]:
def bind(self, mapper: Callable[[T], R]) -> R:
    return mapper(self.ok)


# On Error[E]:
def bind(self, mapper: Callable[[Never], R]) -> Error[E]:
    return self
```

These are alternative method bodies, not standalone functions. Tests covered
callbacks returning only `Ok`, only `Error`, or their union, including chained
calls and lambda inference. A result containing an existing error and a callback
introducing another error must retain both possible error types. Recovery must
also permit `Nothing.or_else(Some(42))` without fixing the payload to `Never`.
Share implementation only where doing so retains these consumer contracts;
an internal fold is an experiment, not a required new public abstraction.

### Closure, tags, and matching

An unrelated subclass of a private method-sharing base is not a member of the
explicit alias. The base therefore does not need a family registration mechanism
for alias closure. Public leaves need `@final` for static checking and a small
runtime hook to reject ordinary subclassing:

```python
@final
@dataclass(frozen=True, slots=True)
class Some(Generic[T]):
    some: T
    tag: Literal["some"] = field(default="some", init=False)

    def __init_subclass__(cls, **kwargs: object) -> None:
        raise TypeError("Some is final")
```

Apply the same closure policy to every case. A fixed tag stays out of constructor
arguments and positional matching, so callers cannot construct a contradictory
tag and payload. A field preserves the tag in `asdict`; a `ClassVar` would not.
`slots=True` is optional and removes instance dictionaries only if the bases also
avoid them. These mechanisms protect normal use, not adversarial monkey-patching.

Use `case NothingType()` or a qualified constant such as `case option.Nothing`.
Bare `case Nothing:` captures a name. Pyright's `reportMatchNotExhaustive`, enabled
in strict mode, checks missing class cases directly; `assert_never` remains a
useful explicit check. Free predicates can narrow their argument to a case.
`TypeGuard` / `TypeIs` on an instance method do not narrow its implicit receiver.

### Alternative for compatibility: both parameters on both cases

This is not the recommended major-version representation. Retaining phantom
parameters is a viable alternative when preserving direct
`yield from value` inference matters. A phantom parameter describes the family
but is not represented by that case's stored payload. Defaults avoid unknown
constructor parameters:

```python
from typing_extensions import Never, TypeVar

T = TypeVar("T", covariant=True, default=Never)
E = TypeVar("E", covariant=True, default=Never)

# Each case inherits the same family parameters:
# Some[T] and NothingType[T] inherit _Option[T].
# Ok[T, E] and Error[T, E] inherit _Result[T, E].
Option: TypeAlias = Some[T] | NothingType[T]
Result: TypeAlias = Ok[T, E] | Error[T, E]
```

This sketch replaces the earlier case declarations. `Ok(42)` then infers
`Ok[int, Never]`, and `Error("message")` infers `Error[Never, str]`. On a parameter
annotated `Result[int, str]`, both alternatives expose the same inherited
iterator signature, and the probe infers `int` from `yield from value`.

By contrast, the payload-only case prototype inferred `Unknown` from direct
`yield from` on the union. `yield from value.__iter__()` and `await value` retained
the success type. The upstream report is
[Pyright #11881](https://github.com/microsoft/pyright/issues/11881).

This is a local inference result, not proof of compatibility with today's
builder. The mixed-type probe uses `Generator[int | str, Never, str]`; it does not
prove the existing runner can send arbitrary bound values into that signature.
`Generator[T, T, T]` still omits `E`, regardless of which case representation
exposes it. Verify runtime type-default substitution against the supported Python
and `typing_extensions` minimum versions before adopting this variant.

## 7. Candidate D: a final nominal wrapper with an explicit case union

This alternative preserves a concrete `Option[T]` class while moving case-specific
data into an explicit union. The wrapper owns the fluent API and exposes a read-only
`.case`. In this alternative, `Some` remains a factory returning the wrapper:

```python
value: Option[int] = Some(42)
assert isinstance(value, Option)

match value.case:
    case SomeCase(number):
        print(number)
    case NothingCase():
        print("Nothing")
```

The wrapper can preserve `Option.Some`, `Option.Nothing`, and existing nominal
checks. Its `.case` type is `SomeCase[T] | NothingCase`, so matching that property
is exhaustive and case-specific access is checked. Both the wrapper and its case
types should be final with ordinary runtime subclass rejection.

The cost is another object layer, distinct names for factories and case types,
and a changed matching surface. Top-level `Some` cannot also be a class pattern
when it is a factory. Exhaustiveness is established on `.case`, not on the
nominal wrapper alone. It would be a fallback if nominal identity were mandatory;
that constraint has been relaxed for the recommended major version. Candidate B
adds sealing machinery without the wrapper's static exhaustiveness on `.case`.

## 8. Typed computational expressions

The union representation and the computation protocol should have separate
contracts. Each bind needs its own payload type; the computation needs a final
return type and an explicit error type. The proposed APIs below are prototypes,
not currently exported interfaces. Names and coexistence with the existing
decorators remain part of migration design.

### Preferred common API: typed scopes

A `ResultScope[E]` owns one computation invocation. Its `bind` accepts
`Result[A, E]` and returns `A`, with `A` inferred independently on every call.
The error parameter on the scope is invariant; it is not the covariant variable
used for immutable case payloads.

```python
@effect.result
def can_access(scope: ResultScope[AppError], text: str) -> bool:
    user_id = scope.bind(parse_id(text))  # int
    user = scope.bind(load_user(user_id))  # User
    return user.is_active  # bool


# can_access(text) -> Result[bool, AppError]
```

`AppError`, `User`, and the domain functions are illustrative. The decorator
infers `E` from the scope annotation and the final result from the body's return
type. `ParamSpec` and `Concatenate` preserve the external function parameters
while supplying the scope internally. No decorator type arguments are needed.

Ordinary coroutines use the same binding operation:

```python
@effect.async_result
async def can_access(scope: ResultScope[AppError], text: str) -> bool:
    user_id = scope.bind(parse_id(text))
    user = scope.bind(await fetch_user(user_id))
    return user.is_active


# await can_access(text) -> Result[bool, AppError]
```

Async generators have no final return-value channel and cannot use `yield from`.
Ordinary coroutines retain normal `return`, exception propagation, and cleanup.
The scope checks the error type at `bind`; awaiting an I/O function alone does
not perform a result bind.

The prototype stores a typed `Error[E]` on the scope and raises a private
`BaseException` control signal carrying invocation identity. Only that scope's
runner handles the signal. Unexpected exceptions propagate, nested runners do
not consume another scope's signal, and `finally` blocks execute. No erased error
payload cast or `Any` is needed in the prototype.

The tradeoffs are the explicit scope parameter and internal nonlocal control
flow. Production work still needs guards against using an escaped or completed
scope, cancellation coverage, and a decision about decorated instance methods.
A `run(body)` callback is another possible entry point for methods. This design
targets Option/Result short-circuit computations; it is not a replacement for
the sequence builder or a general effect interpreter. An analogous Option scope
still needs its own implementation and tests.

### Optional migration candidate: typed generator adapter

The new core API does not require a generator DSL. If a migration adapter is
provided for synchronous callers retaining that syntax, use one that
keeps each payload type local and makes the error type visible to the runner:

```python
@effect.result
def can_access(text: str) -> ResultComputation[bool, AppError]:
    user_id = yield from effect.bind(parse_id(text))
    user = yield from effect.bind(load_user(user_id))
    return user.is_active
```

This is an alternative decorator surface. Its computation type expands to
`Generator[Result[object, E], None, T]`:

| Channel | Meaning |
|---|---|
| Yielded `Result[object, E]` | Effects checked by the runner, retaining the error type |
| Sent `None` | Resume execution without sending a differently typed payload |
| Returned `T` | The final successful result |

The adapter captures `Result[A, E]`, yields it, and returns its original payload
when resumed. The runner advances with `next()`, returns an error without
resuming that bind, and wraps the final return in `Ok`. It closes the generator
in `finally`. Using `object` in the yielded success channel loses no information
needed by the runner: the adapter retains the precise `A`.

The prototype has no public `Any`; an internal cast bridges the standard
`StopIteration.value` API. Overloads handle direct `Ok` and `Error` constructors
without an unknown absent channel. A named computation annotation is still
needed for strict checking of generator bodies.

For Python 3.10, the prototype declares the public parameter order explicitly:

```python
from typing_extensions import TypeAliasType

ResultComputation = TypeAliasType(
    "ResultComputation",
    Generator[Result[object, E], None, T],
    type_params=(T, E),
)
```

A plain legacy alias would discover `E` before `T` in this expression. Dependency
minimums and runtime annotation consumers need checking for the chosen alias
form. The generator adapter works with payload-only case classes and avoids the
direct union-iterator inference issue. It is not a drop-in change to today's
yielded-value, send, or final-result semantics.

### Final-return semantics

For either new protocol, `return None` should mean a successful `None` payload.
An explicit absence or failure operation should express short-circuiting.
This is a proposed behavior change requiring migration guidance. The final
return type should determine `Option[T]` or `Result[T, E]`; neither a prior yield
nor `zero()` should silently manufacture a value outside that annotation.

## 9. Evidence and language boundaries

The original investigation and subsequent review used Pyright **1.1.413** in
strict mode with a **Python 3.10** target. The key typing probes were then rerun
on **1.1.414**, with identical diagnostics across ten comparison groups.
Runtime checks used Python **3.14**; the separate closure and singleton probe also
ran on **3.11** and **3.12**. No Python 3.10 runtime or
full supported-version matrix was exercised.

| Probe | Observed result |
|---|---|
| Generic case aliases | `Option[int]` and `Result[int, str]` work |
| Class patterns and fixed literal tags | Payloads narrow to their declared types |
| Unchecked and known-empty payload access | Rejected |
| Missing match cases | Rejected by strict exhaustiveness checking and by `assert_never` |
| Nominal base with all known subclasses handled | Base remains; not exhaustive |
| Payload-only cases with precise fluent methods | Maps, binds, recovery, and lambda chains preserve types |
| Direct `yield from` on the payload-only case union | Result inferred as `Unknown` |
| Direct `yield from` with shared family parameters and defaults | Success type inferred; existing builder compatibility remains unproven |
| Current CE with wrong error type or wrong effect family | Accepted, demonstrating the lost error channel |
| Typed Result scope | Mixed intermediate types, final return, and function parameters preserved |
| Typed generator adapter | Mixed intermediate types and error channel preserved; invalid yields rejected |
| Wrapper `.case` | Exhaustive matching and payload narrowing with nominal wrapper identity |

### Pyright 1.1.414 comparison

As checked on 2026-11-10, GitHub identifies
[1.1.414 as the latest release](https://github.com/microsoft/pyright/releases/tag/1.1.414).
The original comparison installed 1.1.414 only under `/tmp`. The implementation
now pins **1.1.414** in [the pre-commit configuration](.pre-commit-config.yaml)
and checks both valid consumers and intentional type errors.

The release includes fixes for guard narrowing, dataclass field defaults, and
other typing behavior. They did not change the observed conclusions here:

- Valid union consumers, precise fluent methods, phantom-parameter inference,
  typed scopes, the typed generator adapter, and wrapper examples still pass.
- The corresponding invalid constructions, payload reads, incomplete matches,
  error types, yields, return types, and function arguments produce the same
  diagnostics in the compared negative probes.
- Direct `yield from` on the payload-only case union still infers `Unknown`.
- The current builder still accepts the wrong-error-type and wrong-family
  examples from section 2.

This is a comparison of the design probes, not a claim that every repository
diagnostic or behavior is unchanged. The complete comparison is temporarily
recorded in `/tmp/expression-pyright-comparison.json`. A repository tool upgrade
should be validated separately against the whole project.

### Runtime evidence and remaining limits

Runtime probes exercised matching, mapping, nested options, piping, iteration,
awaiting, copying, pickling, hashing, and ordinary dataclass helpers. A separate
canonical `NothingType.__new__` probe preserved identity through construction,
copying, pickling, and `replace`; a plain empty dataclass does not guarantee that.
Leaf subclass rejection worked with frozen slotted dataclasses. Scope and adapter
checks covered failure short-circuiting and cleanup; scope checks also covered
nested ownership and unexpected exception propagation.

These are bounded proofs, not a complete implementation. The fluent prototype
does not exercise every method or all pipe overloads. Documenting and testing
removal of implicit cross-case ordering, Pydantic schemas, serialization
compatibility, scope lifetime, and the full computational-expression API remain
acceptance work.

Temporary evidence locations:

- `/tmp/expression-union-investigation`: original case-alias and current-design probes.
- `/tmp/expression-union-review`: consumer checks, direct-iteration limitation,
  negative typing examples, and runtime tests.
- `/tmp/expression-runtime-review`: precise fluent methods, phantom parameters,
  generator adapter, closure, and singleton probes.
- `/tmp/expression-union-wrapper-review`: nominal wrapper and `.case` checks.
- `/tmp/expression-ce-review` and `/tmp/expression-scope-review`: current CE gaps
  and typed scope examples, including negative cases.

These directories may disappear and are not repository regression coverage.
Before implementation, preserve the chosen positive and negative consumer
contracts as maintainable project tests.

The following language boundaries still apply:

1. A generic union alias is not a nominal runtime class. Concrete `A | B`
   `isinstance` behavior does not generalize to parameterized generic aliases.
2. `dataclass_transform` describes dataclass-like behavior, not arbitrary generated
   case names or union membership. Explicit source or generated stubs are needed
   for statically visible cases. The preferred design requires no checker plugin.
3. Static finality, runtime subclass rejection, and exhaustive union checking
   are separate properties.
4. Structural views and explicit guards can improve a one-class API, but do not
   establish all the desired nominal and exhaustive properties automatically.
5. Frozen containers do not imply immutable payloads, and static annotations do
   not replace runtime parsing of untrusted data.

References: [class patterns](https://docs.python.org/3/reference/compound_stmts.html#class-patterns),
[`final`](https://docs.python.org/3/library/typing.html#typing.final),
[`__init_subclass__`](https://docs.python.org/3/reference/datamodel.html#object.__init_subclass__),
[aliases](https://typing.python.org/en/latest/spec/aliases.html),
[`dataclass_transform`](https://typing.python.org/en/latest/spec/dataclasses.html),
[type narrowing](https://typing.python.org/en/latest/spec/narrowing.html),
[generator semantics](https://docs.python.org/3/reference/expressions.html#yield-expressions),
[`typing_extensions`](https://typing-extensions.readthedocs.io/en/latest/).

## 10. Recommendation and acceptance gates

| Property | A: one class | B: nominal family | C: case alias | D: wrapper |
|---|---|---|---|---|
| Public nominal `Option` class | Yes | Yes | No | Yes |
| `Some(value)` | Factory | Case constructor | Case constructor | Factory |
| Matching | `Option(...)` | `Some(x)` | `Some(x)` | Match `.case` |
| Exhaustive checking | Not from class alone | Not from base alone | On alias | On `.case` |
| Runtime closure | Enforce on class | Seal family and leaves | Enforce on leaves | Enforce on wrapper and leaves |
| Generic `Option[T]` | Yes | Yes | Yes | Yes |

### Recommended major-version design

Choose **C with payload-only case parameters and typed scopes**. This is the
design implemented for the next major version:

1. **Ordinary case types:** frozen, statically final dataclasses with runtime
   leaf-subclass rejection. Declare `Option[T] = Some[T] | NothingType` and
   `Result[T, E] = Ok[T] | Error[E]` as public aliases. Private implementation
   sharing is allowed; an extensible public base is not the type model.
2. **Python construction and matching:** construct `Some(x)`, `Ok(x)`, and
   `Error(e)`; match their real case classes. Keep a canonical `Nothing` value
   and a `NothingType()` class pattern. Organize helpers in `option` and `result`
   modules. Do not reproduce class namespaces through a runtime facade with a
   different static identity.
3. **Precise operations:** keep fluent and pipe-friendly APIs, with per-case
   signatures where they improve inference. Every supported operation must work
   for consumers without exposing `Any` for an absent channel.
4. **Typed scopes:** infer the computation's final type from its return annotation
   and its error type from `ResultScope[E]`. Each bind has an independent payload
   type. Use ordinary functions and coroutines for the common sync/async API.
5. **Explicit outcomes:** a returned `None` is a successful payload; absence and
   failure are explicit. Keep computation binding separate from ordinary
   iteration and awaiting so those protocols need not encode the builder.
6. **Deliberate runtime contracts:** use ordinary dataclass equality and hashing
   behavior, subject to payload hashability. Do not make cross-case ordering a
   default; callers can use explicit sort keys. Prefer a tagged serialization
   contract that distinguishes all cases, including `Some(None)` and nesting,
   with codecs responsible for payload encoding.
7. **A small core:** treat `Try[T]` as a specialization of Result with exception
   errors rather than a subclass with another runtime identity. Generator
   adapters and legacy codecs are optional migration conveniences. They should
   not dictate the union or scope model.

The phantom-parameter design and nominal wrapper remain documented alternatives,
not coequal recommendations. Verbosity is acceptable when explicit source gives
the checker an accurate contract; a declaration helper must not hide case types
or require a checker plugin.

### Acceptance gates

Before delivering the major version, settle the exact API names and migration
mechanics, then verify these contracts:

- **Public identity and construction:** account for `Option.Some`,
  `Option.Nothing`, `Result.Ok`, `Result.Error`, direct keyword construction,
  `isinstance`, and old class patterns. Modules can provide constructor namespaces;
  the union alias cannot pretend to be the old class.
- **Fluent and functional APIs:** retain precise construction, map, bind,
  recovery, application, pipe overloads, and error-type composition. Test callers,
  not just the library implementation. Prefer explicit case tests or free guards
  for narrowing rather than claiming that `.is_some()` narrows its receiver.
- **Runtime values:** preserve `Nothing` identity deliberately, distinguish
  `Some(None)` and nested options, verify equality, hashing, copying, and pickling,
  and document removal of implicit cross-case ordering. `dataclass(order=True)`
  does not supply the existing `Nothing < Some` ordering across different classes.
- **Serialization:** plain dataclass unions change Pydantic schemas and wire
  shapes. Existing Option encoding is raw payload or null and cannot distinguish
  `Some(None)` from `Nothing`. Define the new tagged codec and nested payload
  behavior explicitly. Existing Result encoding already uses tagged objects;
  test the intended wire changes and document any optional legacy codec.
- **Computation behavior:** preserve existing `EffectError` short-circuit and
  generator send/return behavior in any compatibility layer. Define new final
  return and `None` semantics, reject wrong error types and effect families,
  check direct `scope.bind(Error(...))` and bottom-type inference, and
  test nesting, cleanup, cancellation, scope escape, and decorated methods.
- **Try:** replacing today's subclass with `Try[T] = Result[T, Exception]`
  changes `case Try(...)` and the `Success` / `Failure` representations. Document
  the new matching surface and decide whether convenience constructors remain.
- **Supported tools and versions:** check Python 3.11 runtime behavior and the
  full matrix, actual dependency minimums, current Pyright, and a second checker
  before claiming cross-checker portability.

Start with an isolated Option/Result and computation-protocol implementation.
Keep user-defined `@tagged_union` migration and sequence-builder changes as
separate scope decisions. Production delivery requires realistic runtime and
consumer typing regressions, the full suite, repository lint/type checks, public
examples, and versioned migration guidance.


## 11. Implementation

The core uses payload-only frozen final dataclasses and public aliases with
`Annotated` metadata for optional Pydantic validation. Cases deliberately omit
`slots`: `PipeMixin` already provides an instance dictionary, and nonslotted
frozen cases support generic construction consistently on the supported runtimes.
`NothingType` canonicalizes construction, copying, pickling, and union decoding.

The public computation entry points are `effect.option`, `effect.result`,
`effect.async_option`, and `effect.async_result`, with `OptionScope` and
`ResultScope[E]`. Callback runners support bound methods. Scopes track invocation
identity, active lifetime, thread, and task; the first bound failure remains the
outcome if its internal signal is caught. No generator compatibility adapter is
included. `Try[T]` aliases `Result[T, Exception]`; `Success` and `Failure` remain
constructor conveniences.

Tagged serialization preserves successful None and nested cases. Public aliases
provide discriminated Pydantic decoding; direct case adapters retain Pydantic's
ordinary dataclass behavior. Existing raw/null Option payloads require migration.

Runtime coverage lives in the case and scope test modules. Consumer typing
contracts live in [tests/typing_contracts.py](tests/typing_contracts.py) and
[typing_tests/negative.py](typing_tests/negative.py); the pre-commit hook checks
that every intentional invalid expression is rejected. The legacy user-defined
`@tagged_union` and sequence-builder APIs remain outside this change.

Implementation validation on 2026-11-10:

- The complete suite passes with 517 tests on each of Python 3.11, 3.12, 3.13,
  3.14, and 3.15.
- Repository pre-commit checks pass with Pyright 1.1.414. Fifteen intentionally
  invalid consumer expressions are rejected by the dedicated negative check.
- Mypy 2.4.1 accepts the selected consumer contracts, including mixed Result
  pipelines. This is consumer evidence, not a claim that the entire project is
  configured for Mypy.
- Pydantic 2.6.2 with typing-extensions 4.6.1 passes the schema and scope checks
  on Python 3.11; current locked dependencies pass the full runtime suite.
- Source and wheel builds succeed; the built wheel imports independently and
  preserves scope behavior and nested tagged Pydantic roundtrips.

The migration guide records the remaining contextual-inference limitations and
their typed alternatives. Async decorators expose coroutine return types for
`asyncio.create_task` and `asyncio.run`. Runtime introspection exposes external
parameters and omits the body's now-inaccurate return annotation; static return
types remain precise, and the original body is available through `__wrapped__`.
