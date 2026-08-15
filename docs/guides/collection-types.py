# %% [markdown]
"""
# Work with collections

Expression supplies a lazy `Seq` plus immutable `Block`, `Map`, and `TypedArray`
collections. Choose the smallest abstraction that matches the job.

| Type | Best for |
| --- | --- |
| `Seq[T]` | Lazy transformations over any iterable. |
| `Block[T]` | An immutable, list-like ordered collection. |
| `Map[K, V]` | An immutable key-value mapping. |
| `TypedArray[T]` | Typed numeric or byte-oriented arrays. |

## Start with `Seq`

`Seq` wraps an iterable. Transformations remain lazy until you consume them, which is
useful for a large input or a multi-stage workflow.
"""
# %%
from expression.collections import Seq

numbers = Seq.of(1, 2, 3, 4, 5)
even_squares = numbers.filter(lambda value: value % 2 == 0).map(lambda value: value**2)

assert list(even_squares) == [4, 16]

# %% [markdown]
"""
Do not reuse a `Seq` backed by a one-shot iterator unless you control that iterator's
lifetime. Materialize it with `list`, `Block.of_seq`, or another collection when values
must be traversed repeatedly.

## Prefer immutable domain data

Use `Block` and `Map` when sharing a collection without mutation makes an API easier to
reason about. Operations return a new collection rather than changing the old one.
"""
# %%
from expression.collections import Block, Map

tags = Block.of("new", "featured")
catalog = Map.of_seq([("book", 12)])

assert tags.cons("sale") == Block.of("sale", "new", "featured")
assert catalog.contains_key("book")

# %% [markdown]
"""
See the [collections overview](../reference/collections) for module links and detailed APIs.
"""
