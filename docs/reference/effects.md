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
