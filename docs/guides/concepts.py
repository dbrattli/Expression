# %% [markdown]
"""
# Concepts and terminology

You can use Expression without learning functional-programming vocabulary. This page
defines terms you may encounter in API documentation or other resources.

## Composition

Composition connects small functions so one function's output becomes the next function's
input. `pipe` applies a value through functions; `compose` creates a reusable function.
Use `pipeable` to partially apply a function's parameters after its pipeline value when
the function is not already curried.

## Immutable values

An immutable value cannot be changed after creation. Instead, an operation returns a new
value. `Block` and `Map` are immutable collections.

## Structural sharing

`Map` uses a persistent balanced tree. Adding, changing, or removing a key creates the
nodes on the affected path and reuses untouched branches from the original map. Values
themselves are not copied.

`Block` creates new tuple storage for operations that change its contents, although its
elements remain shared Python object references. `TypedArray` owns mutable array storage
and should not be treated as persistent. `Seq` is lazy: it evaluates its source as it is
iterated rather than copying it into a collection.

## Mapping and binding

`map` transforms a value inside a wrapper such as `Option` or `Result`. `bind` is for a
transformation that itself returns a wrapper, and prevents nested wrappers.

## Effect builders

An effect builder uses a generator or async generator to write a short-circuiting
workflow in a direct style. In other functional-programming material this may be called
a computational expression or monadic workflow. The practical question is simply:
does this make a chain of `Option` or `Result` operations easier to read?

## Further background

The older, theory-oriented tutorials remain available in the repository for historical
context, but they are intentionally not part of the recommended learning path.
"""
