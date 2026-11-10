# Typed generator computations: investigation

**Status:** A synchronous prototype, not an exported Expression API. The library
continues to use typed scopes. This directory records executable evidence for an
optional generator interface alongside them.

## Finding

We can recover typed `yield from` with a small adapter, without changing Option,
Result, their iteration, or their case classes. The crucial change from the old
builder is that the outer generator yields **typed containers**, not payloads.
Each bind keeps its payload locally and returns it when the runner resumes.

```python
from expression import Error, Ok, Result
from investigations.typed_generators import adapter as gen


def parse_number(text: str) -> Result[int, str]:
    return Ok(int(text)) if text.isdigit() else Error("invalid number")


@gen.result
def describe(text: str) -> gen.ResultComputation[str, str]:
    number = yield from gen.bind(parse_number(text))
    label = yield from gen.bind(Ok("items"))
    return f"{number} {label}"


assert describe("3") == Ok("3 items")
assert describe("bad") == Error("invalid number")
```

`number` is an `int`, `label` is a `str`, and callers see `Result[str, str]`.
The Option equivalent uses `@gen.option`, `OptionComputation[T]`, and the same
`bind` overloads for `Some` / `Nothing`.

## How the typing works

The computation aliases describe these generator channels:

| Channel | Result computation | Purpose |
|---|---|---|
| Yield | `Result[object, E]` | Expose the effect family and error type to the outer checker/runner. |
| Send | `None` | Resume without sending a differently typed payload. |
| Return | `T` | Describe the final successful result. |

For Option, the yield channel is `Option[object]`. The bind helper retains the
precise payload type even though the outer runner needs only `object` for success.
It yields the container, then returns the captured payload if resumed. A failed
bind is never resumed by the runner; a manual attempt raises `RuntimeError`.
The runners use `next()`, not `send(payload)`.

Overloads for direct `Ok`, `Error`, `Some`, and `Nothing` construction avoid
inventing types for absent channels. Public signatures contain no `Any`. The
runner uses an internal cast for Python's untyped `StopIteration.value` boundary.
`TypeAliasType` from the existing `typing_extensions` dependency fixes public
parameter order to `[T, E]` on Python 3.11; an ordinary alias encounters `E` first
in the generator expression.

This does not change the containers' ordinary zero-or-one iteration. In
particular, `yield from Ok(42)` is not the new bind protocol: it yields the integer
and is rejected for a declared Result computation. Use `yield from bind(...)`.

## What bare yield can and cannot mean

A bare `yield Ok(42)` is legal in this protocol. It asks the runner to check the
effect, discards its success payload, and receives `None`. A bare `yield Error(e)`
short-circuits, with `e` still checked against the declared error type.

However, `number: int = yield Ok(42)` is rejected, as is the old `yield 42` syntax.
Python gives a generator one send type, rather than a separate send type for
each yield expression. Restoring the old send-the-payload behavior would lose
the guarantee that successive binds can return independently typed values.
[Python's generator annotations](https://docs.python.org/3/library/typing.html#annotating-generators-and-coroutines)
describe these three channels.

## Runtime contract and differences from scopes

The prototype verifies success/failure propagation, mixed payloads, parameters,
methods, loops, nested computations, nested container payloads, and `None` as a
successful final value. Failure preserves the original Error or canonical
NOTHING. Earlier yielded values never replace the final return.

The runner closes the generator in `finally`, including delegated generators.
That runs cleanup after short-circuiting and exceptions. A body catching
`GeneratorExit` and returning success cannot replace the already-selected failure.
Exceptions from cleanup propagate. Yielding another effect during failure cleanup
raises Python's `RuntimeError` for ignoring `GeneratorExit`; cleanup should use
ordinary statements and context managers, not new binds.

This is a Python generator protocol, not an invocation-owned capability. An
adapter created and stored without delegation can later be driven manually; the
regression suite records this difference from scope lifetime checks. There is
no scope-like cross-thread/task ownership guard. Raw generator composition is
useful, but the adapter must not promise the same misuse detection as scopes.

Other boundaries remain explicit:

- A body must be a generator and must declare its computation return type for
  the intended strict contract. A plain function returning a value is rejected.
  An empty generator can use `yield from ()`; this is less natural than a scope body.
- Pyright 1.1.414 does not treat `yield from` a `Never`-returning adapter as
  terminating control flow in a `ResultComputation[Never, E]` body. Declare the
  intended success type and `return (yield from bind(Error(...)))` instead. The
  negative fixture records this checker limitation separately from invalid API use.
- Wrappers currently use `functools.wraps`; runtime introspection still exposes
  the body's generator return annotation. Production decorators would need an
  explicit introspection contract, as the scope decorators already have.
- Async generators cannot use `yield from` or a value-bearing `return`. Therefore
  this protocol has no equivalent async spelling. Keep async scopes, where
  `scope.bind(await operation())` works with ordinary coroutines.
  [Python's async generator restrictions](https://docs.python.org/3/reference/expressions.html#asynchronous-generator-functions)
  are also checked with syntax probes in the test suite.

## Recommendation

Keep scopes as the common synchronous/asynchronous API. If preserving generator
syntax is valuable, add this as an **optional synchronous adapter**. A distinct
namespace such as `effect.gen.result`, `effect.gen.option`, and `effect.gen.bind`
would make the protocol explicit while preserving familiar decorator names.
That namespace is a proposal, not implemented public API.

Avoid making one decorator guess between scoped functions and generators based
on incidental runtime inspection. Prefer a separate entry point unless a robust
combined dispatch contract is demonstrated. Do not change `Option.__iter__` or
`Result.__iter__`, and do not restore the old yielded-value/send semantics.

Before public integration, settle naming, runtime introspection, plain-body
policy, documentation of ownership/cleanup limits, and supported-version CI.
Bring the positive and negative typing contracts into the main typing check.
The existing scope implementation and production tests remain unchanged by this
investigation.

## Evidence and reproduction

- [adapter.py](adapter.py): the full synchronous prototype.
- [positive.py](positive.py): precise intermediate, final, and callable types.
- [negative.py](negative.py): marked invalid uses and the error-only `Never` limitation.
- [test_adapter.py](test_adapter.py): runtime contracts and language-boundary probes.
- [check_typing.py](check_typing.py): checks positives and requires diagnostics on
  every marked negative line, with no unexpected error locations.

From the repository root:

```sh
uv run pytest investigations/typed_generators/test_adapter.py
npx --yes --package=pyright@1.1.414 -c 'uv run python investigations/typed_generators/check_typing.py'
uv tool run --from mypy==2.4.1 mypy --strict --explicit-package-bases --follow-imports=silent investigations/typed_generators/adapter.py investigations/typed_generators/positive.py
```

Recorded results: strict Pyright 1.1.414 accepts positive consumers and rejects
all 13 marked negative lines. Mypy 2.4.1 accepts the adapter and positive consumers
with imported modules' diagnostics suppressed; this is not a whole-library Mypy
claim. All 20 runtime/language-boundary cases pass on Python 3.11–3.15,
including the minimum Pydantic stack on 3.11.

ESA reports no findings in the adapter or runtime tests. Its 12 low-severity
findings concern illustrative literals in typing fixtures and Pyright JSON field
names in the checking script; these remain intentional, without suppressions.
