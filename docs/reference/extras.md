# Extras

These optional helpers build on the core types.

Parser repetition (`many`, `many1`, and separator combinators) processes long inputs
without adding a Python stack frame for each match. Repeated parsers must consume
input when they succeed: `many(preturn(1))("")` raises `ValueError` because it
cannot make progress. For example, `many(pchar("a"))("a" * 3000)` returns an
`Ok` containing all 3000 characters.

```{eval-rst}
.. automodule:: expression.extra
    :members:
```

```{eval-rst}
.. automodule:: expression.extra.parser
    :members:
```

Use the detailed {doc}`Option pipeline <pipeline>` and
{doc}`Result pipeline <pipeline>` APIs for composition helpers.
