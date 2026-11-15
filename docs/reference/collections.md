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

## Async callbacks

Use `asyncseq.amap` when the mapper returns an awaitable. It accepts ordinary
iterables and async iterables, and returns a lazy async iterable:

```python
from expression import pipe
from expression.collections import asyncseq


async def enrich_inputs(value: int) -> int:
    return value * 2


async def example() -> list[int]:
    stream = pipe(
        [1, 2, 3],
        asyncseq.amap(enrich_inputs),
        asyncseq.filter(lambda value: value > 2),
    )
    return [value async for value in stream]  # [4, 6]
```

The fluent equivalent is `AsyncSeq.range(3).amap(enrich_inputs)`. Constructing
either transformation requires no `await`; iteration awaits each mapper call.
Ordinary `pipe` is sufficient because the stages return async iterables, rather
than coroutines that must be resolved before passing to the next stage.

`asyncseq.map` applies a synchronous mapper; `asyncseq.amap` awaits its mapper.
Both preserve one output per input: an awaited list remains one list element,
unlike `collect`, which flattens inner sequences. Mapping is sequential and
preserves source order, with no task scheduling or prefetching. Mapper and source
exceptions, including cancellation, propagate to the consumer. Sources supporting
both iteration protocols are consumed asynchronously.

The same convention applies to the other callback-taking operations. Each has a
module-level function for pipelines and an `AsyncSeq` method:

| Operation | Awaited callback result | Output |
| --- | --- | --- |
| `amap(mapper)` | Mapped value | One item per source item |
| `afilter(predicate)` | Boolean | Items satisfying the predicate |
| `achoose(chooser)` | `Option` | Values from `Some`, skipping `Nothing` |
| `acollect(mapping)` | Ordinary or async iterable | Items from each inner iterable |
| `ascan(scanner, state)` | Updated state | Initial state followed by each update |
| `afold(folder, state)` | Updated state | Coroutine returning the final state |
| `afold_back(folder, state)` | Updated state | Coroutine returning the reverse fold |

All accept ordinary or async sources and await callbacks sequentially. Stream
transformations are constructed synchronously and return lazy async iterables;
the fluent forms return `AsyncSeq`, allowing chaining. `acollect` awaits the
callback and fully consumes its inner iterable before requesting another source
item. An async generator function already returns an async iterable directly, so
use the existing `collect` for that kind of callback.

`ascan` yields the initial state even for empty input, without advancing the source.
Both folds return the initial state for empty input. `afold` and `ascan` call their
callback with `(state, item)`; `afold_back` calls it with `(item, state)` in reverse
source order. Reverse folding buffers the entire finite source and therefore uses
memory proportional to its length.

```python
async def add(state: int, value: int) -> int:
    return state + value


async def total() -> int:
    return await pipe([1, 2, 3], asyncseq.afold(add, 0))  # 6
```

When a fold's resolved result must feed another pipeline stage, use `apipe` to
await it between stages. Operations without callbacks, such as `take`, `skip`,
and `length`, do not need another variant.

## Additional modules

```{eval-rst}
.. automodule:: expression.collections.asyncseq
    :members:
```
