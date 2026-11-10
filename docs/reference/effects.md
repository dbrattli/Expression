# Effects

Typed scopes let an ordinary function or coroutine stop as soon as an `Option` is
absent or a `Result` is an error. Each `scope.bind` retains its payload type, and
the function's return annotation describes the final successful value. Prefer
ordinary `map` and `bind` for short workflows; see [Use effects](../guides/effects)
and the [major-version migration guide](../guides/migration-major.md).

The sequence builder retains its existing generator protocol.

```{eval-rst}
.. automodule:: expression.effect
    :members:
```

```{eval-rst}
.. automodule:: expression.core.builder
    :members:
```
