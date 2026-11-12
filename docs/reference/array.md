(reference_array)=

# Typed Array

Integer indexing preserves the element type: `TypedArray[int]([1, 2])[0]`
has type `int`. Slice indexing returns the underlying storage's mutable sequence,
not another `TypedArray`. Type checking also checks individual assignments and
slice replacement elements against the array's element type.

```{eval-rst}
.. automodule:: expression.collections.array
    :members:
```
