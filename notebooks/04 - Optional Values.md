# Missing Values

Sometimes we don't have a value for a given variable. Perhaps the value is not known or available yet. In Python we represent the absence of a value with the special value `None`. In other languages there is usually a `null` value.

```python
xs = None
print(xs)
```

Without type hints we don't really know if the value is supposed to be `None´ or something else.


## Null Reference Exceptions

> The billion-dollar mistake

Speaking at a software conference in 2009, Tony Hoare apologized for inventing the null reference:

> I call it my billion-dollar mistake. It was the invention of the null reference in 1965. At that time, I was designing the first comprehensive type system for references in an object-oriented language (ALGOL W). My goal was to ensure that all use of references should be absolutely safe, with checking performed automatically by the compiler. But I couldn't resist the temptation to put in a null reference, simply because it was so easy to implement. This has led to innumerable errors, vulnerabilities, and system crashes, which have probably caused a billion dollars of pain and damage in the last forty years.

We don't have null-values in Python, but we have `None` values. Dereferencing a `None` value will lead to a `NameError`:

```python
xs.run()
```

 With type hints we can say that this is supposed to be an integer, but we don't know that integer yet:

```python
from typing import Optional

xs: Optional[int] = None

print(xs)
```

## Testing for optional values

We can test for optional values using `is None` or `is not None`:

```python
xs = None
assert xs is None
y = 42
assert y is not None
```

In addition we have a number of *falsy* values:

```python
assert not None
assert not 0
assert not []
assert not {}
assert not ()
assert not ""
```

## Problems with Nullable Types

Using `Optional` and nullable types in general has a lot of advantages since a compiler or static type checker can help us avoid using optional values before we have done proper testing first. The type `Optional[A]` is the same as `Union[A, None]` which means that there still a few more problems:

* It's easy to forget to check for `None`, but a type checker will help
* Extensive `None` checking can create a lot of noise in the code, increasing the cognitive load
* Optional types cannot be nested. How do we  differ between `None` and `None` i.e `Union[None, None]`? There is no equivalent of e.g a list containing an empty list e.g `[[]]`.

Example: for dictionaries, how do we know if the key is missing or if the value is `None`?

```python
mapping = dict(a=None)
mapping.get("a")
```

## Options

In functional programming we use the Option (or Maybe) type instead of `None` and `null`. The Option type is used when a value is missing, that is when an actual value might not exist for a named value or variable.

An Option has an underlying type and can hold a value of that type `Some(value)`, or it might not have the value and be `Nothing`.


The Expression library provides an `option` module in the `expression.core` package:

```python
from expression.core import Option, option, Some, Nothing
```

## Create option values


Create some values using the `Some` constructor:

```python
xs = Some(42)
xs
```

You should not normally want to retrieve the value of an option since you do not know if it's successful or not. But if you are sure it's `Some` value then you retrieve the value again using the `value` property:

```python
xs = Some(42)
assert isinstance(xs, Some) # important!
xs.value
```

To create the `Nothing` case, you should use the `Nothing` singleton value. In the same way as with `None`, this value will never change, so it's safe to share it for all the code you write.

```python
xs = Nothing
xs
```

To test if an option is nothing you use `is` test:

```python
xs = Nothing
assert xs is Nothing
```

## Option returning functions

Values are great, but the real power of options comes when you create option returning functions

```python
def keep_positive(a: int) -> Option[int]:
    if a > 0:
        return Some(a)

    return Nothing
```

```python
keep_positive(42)
```

```python
keep_positive(-1)
```

We can now make pure functions of potentially unsafe operations, i.e no more exceptions:

```python
def divide(a: float, divisor: float) -> Option[int]:
    try:
        return Some(a/divisor)
    except ZeroDivisionError:
        return Nothing
```

```python
divide(42, 2)
```

```python
divide(10, 0)
```

## Transforming Option Values

The great thing with options is that we can transform them without looking into the box. This eliminates the need for error checking at every step.

```python
from expression.core import Some, option, pipe, Nothing

xs = Some(42)
ys = pipe(
    xs,
    option.map(lambda x: x*10)
)
ys
```

```python
xs = Nothing
ys = pipe(
    xs,
    option.map(lambda x: x*10)
)
ys
```

```python
xs.map(lambda x: x*10)
```

```python

```
