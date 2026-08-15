# %% [markdown]
"""
# Tutorial: choose a collection

Expression has a lazy sequence type and immutable collections. Use them when their
behaviour is part of the contract; otherwise, ordinary Python collections are a good
default.

`Seq` is useful when a value flows through several iterable transformations. It does not
materialize its values until a consumer asks for them.
"""

# %%
from expression.collections import Block, Map, Seq

source = Seq.of(1, 2, 3, 4, 5)
even_squares = source.filter(lambda value: value % 2 == 0).map(lambda value: value**2)

assert list(even_squares) == [4, 16]

# %% [markdown]
"""
## Use immutable values for shared domain state

`Block` is an immutable ordered collection, and `Map` is an immutable mapping. Operations
return a new value, leaving the original available for callers that still need it.
"""

# %%
tags = Block.of("new", "featured")
catalog = Map.of_seq([("book", 12), ("pen", 3)])

sale_tags = tags.cons("sale")
expensive_items = catalog.filter(lambda _name, price: price >= 10)

assert tags == Block.of("new", "featured")
assert sale_tags == Block.of("sale", "new", "featured")
assert expensive_items.contains_key("book")
assert not expensive_items.contains_key("pen")

# %% [markdown]
"""
Materialize a `Seq` with `list` or `Block.of_seq` when a result must be traversed more
than once. Avoid reusing a sequence backed by a one-shot iterator.
"""
