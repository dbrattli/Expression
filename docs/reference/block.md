(reference_block)=

# Block

`Block` is shallowly immutable: its backing tuple cannot be reassigned or deleted,
and instances have no writable `__dict__`. Operations return new blocks.
Objects stored in a block retain their own mutability:

```python
from expression.collections import Block

items = Block([[]])
items[0].append(42)  # The contained list is still mutable.
```

These protections prevent ordinary attribute mutation; they do not prevent
deliberate bypasses such as `object.__setattr__`.

```{eval-rst}
.. automodule:: expression.collections.block
    :members:
```
