# %% [markdown]
"""
# Concepts and terminology

You can use Expression without learning functional-programming vocabulary. This page
defines terms you may encounter in API documentation or other resources.

## Composition

Composition connects small functions so one function's output becomes the next function's
input. `pipe` applies a value through functions; `compose` creates a reusable function.

## Immutable values

An immutable value cannot be changed after creation. Instead, an operation returns a new
value. `Block` and `Map` are immutable collections.

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
