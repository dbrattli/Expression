---
jupytext:
  cell_metadata_filter: -all
  formats: md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.11.5
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---
(tutorial_optional_values)=

# Optional Values

Sometimes we don't have a value for a given variable. Perhaps the value is not known or
available yet. In Python we represent the absence of a value with the special value
`None`. In other languages there is usually a `null` value.

```{code-cell} python
xs = None
print(xs)
```

Without type hints we don't really know if the value is supposed to be `None´ or
something else.


## Null Reference Exceptions

> The billion-dollar mistake

Speaking at a software conference in 2009, Tony Hoare apologized for inventing the null
reference:

> I call it my billion-dollar mistake. It was the invention of the null reference in
> 1965. At that time, I was designing the first comprehensive type system for references
> in an object-oriented language (ALGOL W). My goal was to ensure that all use of
> references should be absolutely safe, with checking performed automatically by the
> compiler. But I couldn't resist the temptation to put in a null reference, simply
> because it was so easy to implement. This has led to innumerable errors,
> vulnerabilities, and system crashes, which have probably caused a billion dollars of
> pain and damage in the last forty years.

We don't have null-values in Python, but we have `None` values. Dereferencing a `None`
value will lead to a `NameError`:

```{code-cell} python
:tags: ["raises-exception"]
xs.run()
```

With type hints we can say that this is supposed to be an integer, but the value is
missing, so we currently don't know what integer just yet:

```{code-cell} python
from typing import Optional

xs: Optional[int] = None

print(xs)
```

## Testing for optional values

We can test for optional values using `is None` or `is not None`:

```{code-cell} python
xs = None
assert xs is None
y = 42
assert y is not None
```

In addition we have a number of *falsy* values:

```{code-cell} python
assert not None
assert not 0
assert not []
assert not {}
assert not ()
assert not ""
```

## Problems with Nullable Types

Using `Optional` and nullable types in general has a lot of advantages since a compiler
or static type checker can help us avoid using optional values before we have done
proper testing first. The type `Optional[A]` is the same as `Union[A, None]` which means
that there still a few more problems:

* It's easy to forget to check for `None`, but a static type checker will help
* Extensive `None` checking can create a lot of noise in the code, increasing the
  cognitive load
* Optional types cannot be nested. How do we differ between `None` being a proper values
  and `None` for telling that the value is missing i.e `Union[None, None]`? There is no
  equivalent of e.g a list containing an empty list e.g `[[]]`.

**Example:** for dictionaries, how do we know if the key is missing or if the value is
`None`?

```{code-cell} python
mapping = dict(a=None)
mapping.get("a")
```

## Options

In functional programming we use the Option (or Maybe) type instead of `None` and
`null`. The Option type is used when a value could be missing, that is when an actual
value might not exist for a named value or variable.

An Option has an underlying type and can hold a value of that type `Some(value)`, or it
might not have the value and be `Nothing`.


The Expression library provides an `option` module in the `expression.core` package:

```{code-cell} python
from expression import Option, option, Some, Nothing
```

## Create option values

Create some values using the `Some` constructor:

```{code-cell} python
from expression import Some

xs = Some(42)
xs
```

You should not normally want to retrieve the value of an option since you do not know if
it's successful or not. But if you are sure it's `Some` value then you retrieve the
value back using the `value` property:

```python
from expression import Some

xs = Some(42)
assert isinstance(xs, Some) # important!
xs.value
```

To create the `Nothing` case, you should use the `Nothing` singleton value. In the same
way as with `None`, this value will never change, so it's safe to re-use it for all the
code you write.

```{code-cell} python
from expression import Nothing

xs = Nothing
xs
```

To test if an option is nothing you use `is` test:

```{code-cell} python
xs = Nothing
assert xs is Nothing
```

## Option returning functions

Values are great, but the real power of options comes when you create option returning
functions

```{code-cell} python
def keep_positive(a: int) -> Option[int]:
    if a > 0:
        return Some(a)

    return Nothing
```

```{code-cell} python
keep_positive(42)
```

```{code-cell} python
keep_positive(-1)
```

We can now make pure functions of potentially unsafe operations, i.e no more exceptions:

```{code-cell} python
def divide(a: float, divisor: float) -> Option[int]:
    try:
        return Some(a/divisor)
    except ZeroDivisionError:
        return Nothing
```

```{code-cell} python
divide(42, 2)
```

```{code-cell} python
divide(10, 0)
```

## Transforming option values

The great thing with options is that we can transform them without looking into the box.
This eliminates the need for error checking at every step.

```{code-cell} python
from expression import Some, option, pipe, Nothing

xs = Some(42)
ys = pipe(
    xs,
    option.map(lambda x: x*10)
)
ys
```

If we map a value that is `Nothing` then the result is also `Nothing`. Nothing in,
nothing out:

```{code-cell} python
xs = Nothing
ys = pipe(
    xs,
    option.map(lambda x: x*10)
)
ys
```

## Option as an effect

Effects in Expression is implemented as specially decorated coroutines ([enhanced
generators](https://www.python.org/dev/peps/pep-0342/)) using `yield`, `yield from` and
`return` to consume or generate optional values:

```{code-cell} python
from expression import effect, Some

@effect.option[int]()
def fn():
    x = yield 42
    y = yield from Some(43)

    return x + y

fn()
```

This enables ["railway oriented programming"](https://fsharpforfunandprofit.com/rop/),
e.g., if one part of the function yields from `Nothing` then the function is
side-tracked (short-circuit) and the following statements will never be executed. The
end result of the expression will be `Nothing`. Thus results from such an option
decorated function can either be `Ok(value)` or `Error(error_value)`.

```{code-cell} python
from expression import effect, Some, Nothing

@effect.option[int]()
def fn():
    x = yield from Nothing # or a function returning Nothing

    # -- The rest of the function will never be executed --
    y = yield from Some(43)

    return x + y

fn()
```

For more information about options:

- [API reference](https://expression.readthedocs.io/en/latest/reference/option.html)
