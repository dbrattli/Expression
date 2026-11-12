(reference_map)=

# Map

`Map` is shallowly immutable: its tree reference and internal tree nodes cannot
be reassigned or deleted through ordinary attribute access. Instances and tree
nodes have no writable `__dict__`. Updates return new maps and safely share
unchanged nodes with earlier maps:

```python
from expression.collections import Map

original = Map.create([(1, "one")])
updated = original.add(2, "two")
assert 2 not in original
assert updated[2] == "two"
```

Keys and values retain their own mutability. Keys must keep stable comparison
behavior, and hashing a map requires keys and values with stable hashes.
These protections do not prevent deliberate bypasses such as `object.__setattr__`.

```{eval-rst}
.. automodule:: expression.collections.map
    :members:
```
