# Collections

The collection modules provide functional operations over Python iterables plus immutable
collection types. See [Work with collections](../guides/collection-types) before choosing an
API.

Detailed module references are available for {doc}`Seq <seq>`, {doc}`Block <block>`,
{doc}`Map <map>`, and {doc}`TypedArray <array>`.

For both `Block` and `TypedArray`, `take_last(0)` returns an empty collection,
while `skip_last(0)` preserves all elements. For example,
`list(Block.of(1, 2, 3).take_last(0))` is `[]`.

`AsyncSeq.take(n)` consumes at most `n` source items. Taking zero items does not
advance the source, and completing the result does not request an extra item.

`sum` and `sum_by` use Python's summation behavior: empty input returns integer
`0`, even when the element or projection type is `float` or `Decimal`. Their
return annotations include this empty-input case. `sum_by` requires summable
projection results, not summable source elements; for example,
`Block.of("one", "four").sum_by(len)` returns `7`.

## Additional modules

```{eval-rst}
.. automodule:: expression.collections.asyncseq
    :members:
```
