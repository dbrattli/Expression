# F# computation-expression semantics in Python

**Goal:** Choose the API by its correspondence with F# computation expressions,
then assess Python syntax and typing limitations. This supersedes the earlier
scope-first recommendation as the design criterion. It does not change the
production API: both implementations here are investigations.

## Reference contract

F# translates computation expressions into builder operations. `let!` calls
`Bind`, `return` calls `Return`, and `return!` calls `ReturnFrom`. `yield` and
`yield!` are separate operations (`Yield` and `YieldFrom`), normally used for
producing sequences. Their meanings must not be conflated merely because Python
has a `yield` keyword.

F# also delegates sequencing, empty branches, loops, and resource handling to
`Combine`, `Zero`, `For`, `While`, `TryFinally`, and `Using`. There is no single
universal Option/Result CE contract: the builder chooses its operations and their
types. See the [F# language reference](https://learn.microsoft.com/en-us/dotnet/fsharp/language-reference/computation-expressions).

[reference.fsx](reference.fsx) defines concrete short-circuit Result and Option
builders for comparison. Both lift successful returns, forward returned
computations, and stop binding on failure. Their `Combine` accepts a successful
unit prefix; Result's `Zero` is `Ok ()`, while Option's is `None`.

The reference checks also demonstrate that F# `return` is **not** an imperative
function exit: a successful `return ()` can be followed by another expression
through `Combine`. Therefore our prior mapping to Python `return` is valid for
terminal returns, not for arbitrary CE expressions.

## A computation is distinct from its result

The prototype introduces delayed `ResultComputation[T, E]` and
`OptionComputation[T]` objects. They are not replacements for the data unions.
A computation can be bound by delegation; its `.run()` realizes an ordinary
Result or Option. Repeated `.run()` calls execute a fresh generator. Adapting an
already-created Result or Option with `computation(value)` captures that value;
it cannot make its earlier evaluation lazy.

This separates two protocols that the original Expression containers combined:

- `Result` / `Option` iteration enumerates zero or one payloads.
- Computation iteration delegates an effect and returns its precise payload.

The latter supports direct `yield from operation()` when `operation` returns a
computation, with no extra `bind(...)` at each nested call.

```python
from expression import Error, Ok
from investigations.fsharp_ce.computation import (
    ResultBody,
    ResultComputation,
    computation,
    result,
)


def parse_number(text: str) -> ResultComputation[int, str]:
    return computation(Ok(int(text)) if text.isdigit() else Error("invalid number"))


@result
def describe(text: str) -> ResultBody[str, str]:
    number = yield from parse_number(text)  # let!
    label = yield from computation(Ok("items"))  # boundary to an existing Result
    return f"{number} {label}"  # terminal return


@result
def forward(text: str) -> ResultBody[str, str]:
    return (yield from describe(text))  # terminal return!


assert describe("3").run() == Ok("3 items")
assert forward("bad").run() == Error("invalid number")
```

`ResultBody[T, E]` describes the generator body; `ResultComputation[T, E]`
describes the delayed object exposed to callers. Distinguishing these avoids
pretending that the decorated callable returns a generator or an already-run
Result. This is an additional public concept and a compatibility tradeoff, not
just a spelling change. Factory arguments are evaluated normally by Python;
the decorated generator body is delayed until execution.

## Which semantics are established?

| F# operation | Prototype spelling | Evidence and boundary |
|---|---|---|
| `let x = computation` | `pending = operation()` | Creates a reusable object without executing the decorated body. |
| `let! x = computation` | `x = yield from operation()` | Executes once per bind; success type remains local and failure stops the outer body. |
| `do! computation` | `yield from operation()` | Sequences unit computations. Python also permits discarding non-unit payloads; it does not enforce F#'s unit constraint. |
| Terminal `return x` | `return x` | Lifts exactly once, including None and nested containers. |
| Terminal `return! computation` | `return (yield from operation())` | Equivalent success/failure values for these Option/Result builders. Success is rewrapped; this is Bind-plus-Return, not a general custom-builder ReturnFrom implementation. |
| `Delay` / `Run` | Decorated factory / `.run()` | A fresh execution per run. F# builders can choose other eager/delayed policies. |
| Sequencing / loops | Statements, `for`, `while` | Sequential short-circuit behavior verified; Python controls execution rather than invoking user-defined For/While/Combine methods. |
| `try/with` | `try/except` | Ordinary exceptions can be handled; a Result failure stays in the Result channel. |
| `try/finally`, `use` | `try/finally`, `with` | Generator closing runs cleanup and resource disposal after failure. |
| `Zero` | No general equivalent | Fallthrough returns Python None; the return-based runner lifts it. This differs from the reference Option builder's Zero=None. |
| Nonterminal `Return` | No direct equivalent | Python return exits the function. The reference builder can continue after Return(unit). |
| `and!`, custom operations, async CEs | Not implemented | This prototype is not a generic F# CE compiler or an async scheduler. |

The tests also check left/right identity and associativity examples, nested
failure, evaluation count, and the distinction between returning a failed
container as a payload and delegating that container as a computation.

The return-based protocol is `Generator[ResultStep[E], None, T]` (and the Option
analogue). It uses the same local-payload insight as the earlier adapter, but
puts iteration on the computation object where delegation has domain meaning.
The error type is visible in the yielded step; the runner never sends arbitrary
payloads back into the outer generator.

The earlier [generator investigation](../typed_generators/README.md) still
applies to generator-closing restrictions, the absence of scope-style ownership
checks, and async-generator language restrictions. Runtime introspection and
plain nongenerator bodies still need an explicit production design.

## Can we keep the original `yield value` spelling?

The separate `yield_result` probe uses `yield value` as a Return-like operation
and keeps the last successful value, approximating Expression's earlier Combine
policy. It can bind an int, then a string, and yield a string with precise local
payload types. It is deliberately **not a sound public API candidate as written**.

Three executable counterexamples explain the limitations:

1. **Arbitrary output types can hide the error channel.** Its body type contains
   `T | ResultStep[E]`. With `T=object`, every step is also an acceptable raw
   output. Pyright accepts a computation declared with string errors that binds
   `Error(123)`; execution returns that integer error. This happens with ordinary
   delegation, without forging a protocol event. Reserved internal envelopes do
   not restore the lost static constraint.
2. **None and fallthrough are indistinguishable.** After `yield 42`, both an
   omitted return and explicit `return None` finish with the same generator
   return value. The legacy last-value policy returns `Ok(42)` for both.
   `yield None` can explicitly produce a successful None, but this is a different
   contract from the return-based variant.
3. **A typed generator need not produce any yields.** A conditional `yield "x"`
   passes static checks even when the condition is false. Returning `Ok(None)`
   would violate the declared string payload type. The probe raises a runtime
   error rather than claim that type. F# can type-check its translated Zero
   branch; Python's Generator annotation does not describe that path property.

Furthermore, yielding multiple arbitrary values and keeping the last is not the
reference Result builder's unit-prefix Combine contract. The old syntax was
convenient, but it was already a particular approximation of F#.

Explicitly wrapping return events (rather than yielding arbitrary raw payloads)
would separate payloads from bind events, at the cost of additional syntax. It
would not by itself prove that every path produces an output. Source/AST
translation or a checker extension could recover more compiler-level guarantees,
but would materially increase implementation and tooling complexity.

## Recommended next design direction

Use **computation values as the basis for further CE design**, with direct
`yield from operation()` binding, rather than promoting the prior
`yield from bind(...)` surface. Preserve Option and Result as independently useful
data unions. Keep the existing production scopes while this design is evaluated;
they are not presented as a substitute for the requested CE vocabulary.

The return-based prototype is a credible typed subset of common Option/Result CE
usage. It is not full F# CE semantics. Before production integration, explicitly
choose:

- Whether terminal `return` / `return!` and ordinary Python control flow are the
  intended subset, or whether nonterminal Return, Zero, and customizable Combine
  must also be modeled.
- Whether callers should receive delayed computation objects with `.run()`, or
  whether an eager runner plus explicit adapters better fits Expression.
- Whether preserving bare `yield value` outweighs its demonstrated typing limits,
  or explicit return-operation syntax is acceptable.

Do not claim all three at once: unchanged legacy spelling, arbitrary payload
and error types checked precisely, and full builder-controlled F# semantics.
The experiments show where those goals diverge under Python's generator protocol.

## Reproduction

From the repository root:

```sh
dotnet fsi --exec investigations/fsharp_ce/reference.fsx
uv run pytest investigations/fsharp_ce/test_computation.py
npx --yes --package=pyright@1.1.414 -c 'uv run python investigations/fsharp_ce/check_typing.py'
uv tool run --from mypy==2.4.1 mypy --strict --explicit-package-bases --follow-imports=silent investigations/fsharp_ce/computation.py investigations/fsharp_ce/positive.py
```

[positive.py](positive.py), [negative.py](negative.py), and
[test_computation.py](test_computation.py) preserve the evidence. The counterexample
that escapes checking is deliberately a passing runtime test, not a claimed
negative-check success. The Mypy command checks the implementation and positive
consumer contracts while suppressing imported library diagnostics.

Recorded checks: the F# reference passes on .NET SDK 10.0.400; all 15 Python
runtime/counterexample cases pass on Python 3.11–3.15. Strict Pyright 1.1.414
accepts the positive contracts and rejects all 10 marked invalid uses. Mypy 2.4.1
accepts the implementation and positive consumers. The combined production and
investigation suite passes 611 cases.

ESA's remaining findings are intentional experiment/test structure: two coherence
heuristics for the related protocol classes and overloads, thirteen illustrative
literal/diagnostic-key findings, and the F# assertion helper's validation finding.
The interpreter's complexity findings were addressed by separating decorator
construction, execution, and completion policy. No rules were suppressed.
