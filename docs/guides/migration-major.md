# Migrating to case unions and typed scopes

This major version requires Python 3.11 or later. The optional Pydantic
integration requires Pydantic 2.10 or later to preserve generic payload
validation when caller and library type-variable names overlap.

Option and Result now use explicit frozen case classes. Their public types are
unions: `Option[T]` consists of `Some[T]` and `Nothing`; `Result[T, E]` consists
of `Ok[T]` and `Error[E]`. Each case has only its own payload. Both static checking
and ordinary runtime subclassing enforce final cases.

## Construct and match cases

Use `Some(value)`, `Nothing()`, `Ok(value)`, and `Error(error)` directly. Constructors
and conversion functions live in the `option` and `result` modules; aliases do
not provide the old `Option.Some`, `Result.Ok`, or keyword constructors.

```python
from expression import Nothing, Option, Some, option

def describe(value: Option[int]) -> str:
    match value:
        case Some(number):
            return str(number)
        case Nothing():
            return "missing"

value = option.of_optional(42)
assert describe(value) == "42"
```

Replace `case Option(some=x)` with `case Some(x)`, `case Result(ok=x)` with
`case Ok(x)`, and `case Result(error=e)` with `case Error(e)`. Use `case Nothing()`
for the empty case. Bare `case Nothing` captures a name and matches any subject;
it does not test the empty case.

`Nothing` is now the case class, not a preconstructed value. Replace bare value
uses such as `return Nothing` and `Some(Nothing)` with `return Nothing()` and
`Some(Nothing())`. The earlier proposal's `NothingType` name is no longer exposed;
use `Nothing` for type annotations and `Nothing()` for construction and matching.
Repeated construction preserves identity: `Nothing() is Nothing()`.

Use the shared `NOTHING` constant to avoid constructor calls. It is defined once
in `option.py` and also exported from `expression`:

```python
from expression import NOTHING, Nothing, Option

def absent() -> Option[int]:
    return NOTHING

assert NOTHING is Nothing()

match absent():
    case Nothing():
        pass
```

`NOTHING` is annotated `Final`; `Nothing` remains the class for construction,
type annotations, and patterns. Class patterns do not invoke the constructor.
You can still define a local convenience such as `Nothing_ = NOTHING` if desired.

Use `isinstance(value, Some)` or `isinstance(value, (Some, Nothing))` when a
runtime class check is necessary. Generic union aliases are not nominal classes
and cannot replace those checks. Free predicates such as `option.is_some(value)`
and `result.is_ok(value)` narrow the argument; boolean instance predicates are
convenience checks, not a promise of receiver narrowing.

Fluent and functional operations remain available, including `.map`, `.bind`,
`.pipe`, `option.map`, and `result.map_error`. Bind and recovery retain all
possible error or success types. `Nothing()` remains canonical across construction,
copying, and pickling. Cases use dataclass equality and hashing; payloads must be
hashable to hash a case. Cross-case ordering is removed; provide a sort key when
ordering is needed.

Prefer fluent operations when a lambda needs its input type inferred from the
container. A curried helper is checked before the later pipe input, so use a
named, annotated callback for more complex pipelines. For example,
`value.bind(lambda number: Ok(str(number)))` gets its argument type from `value`;
`value.pipe(result.bind(convert))` gets it from `convert`'s annotation. For an
unknown `Option[tuple[...]]`, use an annotated callback with `.starmap` as well.
Pyright also checks an optional receiver's `.pipe` separately for each case;
with `option.to_list` or `option.to_seq`, the empty branch cannot infer the
invariant container's element type. Use `pipe(value, option.to_list)`,
`option.to_list(value)`, or `items: list[int] = value.to_list()`; the equivalent
forms work for `to_seq`.

## Bind through scopes

Replace generator builders and their type arguments with ordinary functions.
The decorator supplies the first scope argument, infers the final result from
the return type, and preserves the remaining public call signature.

Static checking knows the wrapped return type. Runtime introspection exposes
the external parameters and omits the return annotation, since the body's
annotation describes the unwrapped payload. The original function and its full
annotations remain accessible through `__wrapped__`.

```python
from expression import Error, Ok, Result, effect

def parse_count(text: str) -> Result[int, str]:
    return Ok(int(text)) if text.isdigit() else Error("invalid count")

@effect.result
def describe_count(scope: effect.ResultScope[str], text: str) -> str:
    count = scope.bind(parse_count(text))
    label = scope.bind(Ok("items"))
    return f"{count} {label}"

assert describe_count("3") == Ok("3 items")
assert describe_count("bad") == Error("invalid count")
```

Every binding has its own payload type. The scope's error type constrains every
bound Result. `OptionScope` accepts only Option cases. Binding an error or
`Nothing()` ends that invocation and executes normal `finally` cleanup. The first
failure remains the outcome even if a broad exception handler catches the
internal control signal. Ordinary exceptions propagate.

A scope belongs to one invocation and execution context. Do not store it for
later use or pass it into another task or thread; such binds raise `RuntimeError`.
Nested computations receive independent scopes.

For methods, use `effect.run_result(self.compute)` or `effect.run_option(...)`,
where the bound method accepts a scope and returns its successful value. Async
callback runners are `async_run_result` and `async_run_option`.

## Async computations and successful None

Use ordinary coroutines with `@effect.async_result` or `@effect.async_option`.
Await I/O to retrieve a container, then bind it:

```python
async def fetch_count() -> Result[int, str]:
    return Ok(42)

@effect.async_result
async def positive(scope: effect.ResultScope[str]) -> bool:
    count = scope.bind(await fetch_count())
    return count > 0

# await positive() returns Ok(True).
```

Containers themselves are no longer awaitable. Their iteration is ordinary:
`list(Some(42)) == [42]`, `list(Nothing()) == []`, `list(Ok(42)) == [42]`, and
`list(Error("failed")) == []`. Iterating does not perform an effect bind.
Replace `yield from container` and `yield await container` with `scope.bind`.
The sequence builder `@effect.seq[T]()` keeps its existing generator behavior.

The final `return` determines the successful payload, including `None`:
an Option computation returning `None` produces `Some(None)`, and a Result
computation returning `None` produces `Ok(None)`. Bind `Nothing()` or `Error(...)`
to express absence or failure. Implicit fall-through also returns `None` under
ordinary Python rules; annotate the intended return type so the checker catches
missing returns where appropriate.

`Try[T]` is now the alias `Result[T, Exception]`. `Success` and `Failure` remain
convenience constructors returning `Ok` and `Error`; they no longer have a
distinct class or string representation. Match `Ok` / `Error`. `effect.try_` and
`effect.async_try` constrain explicit errors to exceptions; they do not catch
unexpected exceptions from the body. Use `catch` when that conversion is intended.

## Tagged serialization

Option serialization now includes a tag. These values remain distinct:

```python
from expression import Nothing, Some

assert Nothing().dict() == {"tag": "none"}
assert Some(None).dict() == {"tag": "some", "some": None}
assert Some(Nothing()).dict() == {"tag": "some", "some": {"tag": "none"}}
```

Result uses `{"tag": "ok", "ok": value}` or
`{"tag": "error", "error": error}`. `.dict()` recursively encodes dataclasses,
lists, tuples, mappings, and payloads exposing `model_dump`; unsupported payload
leaves remain the responsibility of the caller's encoder.

With optional Pydantic support, annotate fields with `Option[T]` / `Result[T, E]`
or use `TypeAdapter` on those aliases. Their metadata selects the exact tagged
case before validating the payload, rejects missing/unknown tags and extra case
fields, and restores canonical `Nothing()`. This preserves nested case identities.
Direct `TypeAdapter(Some[int])` uses Pydantic's ordinary dataclass behavior and
does not provide the union's wire validation; use the public union alias at the
decoding boundary. Existing raw-value/null Option data needs an explicit migration.

## Define custom tagged unions

Replace the old one-class `@tagged_union` declarations with explicit cases and a
`TaggedUnion` alias. Option and Result use this same case implementation.

```python
from typing import Literal, TypeAlias, final
from expression import TaggedUnion, case, tag

@final
@case
class Card:
    last_four: str
    tag: Literal["card"] = tag("card")

@final
@case
class Cash:
    tag: Literal["cash"] = tag("cash")

Payment: TypeAlias = TaggedUnion[Card | Cash]

def describe(payment: Payment) -> str:
    match payment:
        case Card(last_four):
            return f"Card ending in {last_four}"
        case Cash():
            return "Cash"
```

Construct `Card("1234")` and `Cash()` directly. The alias is a closed list of
alternatives, not a class or a constructor namespace. `tagged_union` is now the
module namespace; its old decorator and the old `case()` field marker are
removed. The `tag` field is required and must declare one matching string literal.
It is excluded from construction and positional patterns. Use a class pattern or
compare `.tag` to narrow the payload type.

`@case` generates a frozen dataclass and rejects runtime subclasses. Keep
`@final` explicit so type checkers also reject subclasses; a custom decorator
cannot imply static finality. Each case declares only its own fields. Generic
cases work normally: `Maybe: TypeAlias = TaggedUnion[Present[T] | Missing]`.
Payload annotations may refer forward to the enclosing union alias.

Use ordinary field defaults and `dataclasses.field(default_factory=...)` for
payloads. `@case(kw_only=True)` makes payload parameters keyword-only;
`@case(repr=False)` supports a custom representation. Payloads must be constructor
fields: `InitVar`, non-tag `init=False` fields, custom constructors, and dataclass
inheritance are rejected. Plain mixins and ordinary methods remain supported.
For alternatives with no data, an ordinary `Enum` is also suitable.

Unit cases such as `Cash()` have value equality; they are not automatically
singletons. `Nothing()` retains its explicit singleton contract. Custom cases use
ordinary dataclass copying, pickling, hashing and `asdict`, and do not provide
cross-case ordering or the old active-field metadata mutation.

Use `TypeAdapter(Payment)` or a Pydantic field annotated with `Payment` for tagged
decoding. The codec checks distinct tags and declared case membership, requires
the tag on wire objects, and rejects extra fields. Payloads use their declared
Python field names; Pydantic field aliases are rejected. Case-level validation
metadata is supported; union-level validators on an alias nested inside another
union are rejected rather than silently discarded. Ordinary constructor type
annotations are static contracts;
use a decoding boundary to validate external data.

The sequence builder retains its existing generator protocol.

## Unit cases, shared values, and singletons

A case with no payload is a **unit case**. Use the case class's name for both
construction and matching, just as for a case with payloads:

```python
from typing import Literal, TypeAlias, final
from expression import TaggedUnion, case, tag

@final
@case
class Missing:
    tag: Literal["missing"] = tag("missing")

@final
@case
class Found:
    value: str
    tag: Literal["found"] = tag("found")

Lookup: TypeAlias = TaggedUnion[Found | Missing]
Missing_ = Missing()  # Optional shared value to avoid repeated construction.

def describe_lookup(value: Lookup) -> str:
    match value:
        case Found(text):
            return text
        case Missing():
            return "missing"

assert describe_lookup(Missing_) == "missing"
assert describe_lookup(Missing()) == "missing"
```

`Missing()` in an expression calls the constructor and normally allocates a
new case. `case Missing():` is a class pattern: it checks the subject's type
without calling the constructor or allocating a case. See Python's
[class pattern semantics](https://docs.python.org/3/reference/compound_stmts.html#class-patterns).

A shared constant is not a guaranteed singleton: `Missing() == Missing_`, but
`Missing() is not Missing_`. Copies, pickle roundtrips, and decoding need not
preserve its identity. Use class patterns or equality for ordinary unit cases.
A `Final` annotation can prevent reassignment statically; it does not prevent
other instances. Keep the class and shared value under distinct names, so the
class remains available for patterns and annotations. Bare `case Missing_` is a
capture pattern, not a test of the shared value.

Expression's `Nothing` has a stronger, specialized contract: its constructor
returns one canonical instance, and Option's schema metadata restores that
instance after validation. Copying and pickling preserve its identity too.
The general `@case` / `TaggedUnion` API does not currently provide a singleton
option. For custom unions, prefer ordinary unit cases and optionally a shared
constant; guaranteeing identity across construction and serialization requires
additional lifecycle behavior.
