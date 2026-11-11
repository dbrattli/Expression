# Effects

Effect builders let a generator-based or asynchronous workflow stop as soon as an
`Option` is absent or a `Result` is an error. Prefer ordinary `map` and `bind` for short
workflows; see [Use effect builders](../guides/effects) for an example.

```{eval-rst}
.. automodule:: expression.effect
    :members:
```

```{eval-rst}
.. automodule:: expression.core.builder
    :members:
```

## Synchronous builder contract

`Builder` interprets generators eagerly. Custom `bind` implementations must call
their continuation exactly once, synchronously. Skipping the continuation, calling
it more than once, or retaining it for later execution raises `RuntimeError`.
Built-in Option/Result failures still short-circuit through their existing iterator
protocol. The builder closes its generator on completion or failure, running its
`finally` blocks and context-manager cleanup.

Builder-hook exceptions propagate, including `StopIteration`; only generator
exhaustion counts as normal completion. `zero()` is used for empty computations,
not as an initial accumulator for computations that produce values.

For compatibility, a generator ending with `return None` or falling off its end
retains its last yielded result. An empty body uses `zero()`. An explicit `yield
None` produces a successful value. `yield from Some(value)` and `yield from
Ok(value)` unwrap through Python's iterator protocol; they are not general F#
`Bind` operations. Failure uses `EffectError`, so a broad `except Exception` inside
the body can intercept it.

The current `delay` hook receives an already computed step, and sequence builders
are eager. Deferred, reusable, and branching computations are outside this
interpreter's contract. These rules describe synchronous `Builder`; `AsyncBuilder`
has a separate implementation.
