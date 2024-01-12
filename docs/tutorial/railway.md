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
(tutorial_railway)=

# Railway Oriented Programming (ROP)

- We don't really want to raise exceptions since it makes the code bloated with error
  checking
- It's easy to forget to handle exceptions, or handle the wrong type of exception
- Dependencies might even change the kind of exceptions they throw
- Let's model errors using types instead

```{code-cell} python
class Result:
    pass

class Ok(Result):
    def __init__(self, value):
        self._value = value

    def __str__(self):
        return "Ok %s" % str(self._value)

class Error(Result):
    def __init__(self, exn):
        self._exn = exn

    def __str__(self):
        return "Error %s" % str(self._exn)
```

The Expression library contains a similar but more feature complete Result class we can
use:

```{code-cell} python
from expression import Ok, Error

def fetch(url):
    try:
        if not "http://" in url:
            raise Exception("Error: unable to fetch from: '%s'" % url)

        value = url.replace("http://", "")
        return Ok(value)
    except Exception as exn:
        return Error(exn)
```

```{code-cell} python
result = fetch("http://42")

print(result)
```

```{code-cell} python
def parse(string):
    try:
        value = float(string)
        return Ok(value)
    except Exception as exn:
        return Error(exn)
```

```{code-cell} python
result = parse("42")

print(result)
```

## Composition

How should we compose Result returning functions? How can we make a `fetch_parse` from
`fetch` and `parse`.

We cannot use functional composition here since signatures don't match.

```python
def compose(fn: Callable[[A], Result[B, TError]], gn: Callable[[B], Result[C, TError]]) -> Callable[[A], Result[C, TError]]:
    lambda x: ...
```

First we can try to solve this with an "imperative" implementation using type-checks and
`if-else` statements:

```{code-cell} python
def fetch_parse(url):
    b = fetch(url)
    if isinstance(b, Ok):
        val_b = b._value # <--- Don't look inside the box!!!
        return parse(val_b)
    else: # Must be error
        return b

result = fetch_parse("http://42")
print(result)
```

This works, but the code is not easy to read. We have also hard-coded the logic to it's
not possible to easily reuse without copy/paste. Here is a nice example on how to solve
this by mixing object-oriented code with functional thinking:

```{code-cell} python
class Ok(Result):
    def __init__(self, value):
        self._value = value

    def bind(self, fn):
        return fn(self._value)

    def __str__(self):
        return "Ok %s" % str(self._value)

class Error(Result):
    def __init__(self, exn):
        self._exn = exn

    def bind(self, fn):
        return self

    def __str__(self):
        return "Error %s" % str(self._exn)

def bind(fn, result):
    """We don't want method chaining in Python."""
    return result.bind(fn)
```

```{code-cell} python
result = bind(parse, fetch("http://42"))
print(result)
```

```{code-cell} python
def compose(f, g):
    return lambda x: f(x).bind(g)

fetch_parse = compose(fetch, parse)
result = fetch_parse("http://123.0")
print(result)
```

```{code-cell} python
result = fetch("http://invalid").bind(parse)
print(result)
```

### But what if we wanted to call fetch 10 times in a row?

This is what's called the "Pyramide of Doom":

```{code-cell} python
from expression.core import result

result = bind(parse,
            bind(lambda x: fetch("http://%s" % x),
               bind(lambda x: fetch("http://%s" % x),
                  bind(lambda x: fetch("http://%s" % x),
                     bind(lambda x: fetch("http://%s" % x),
                         bind(lambda x: fetch("http://%s" % x),
                             bind(lambda x: fetch("http://%s" % x),
                                 fetch("http://123")
                            )
                         )
                     )
                  )
               )
            )
         )
print(result)
```

## Can we make a more generic compose?

Let's try to make a general compose function that composes two result returning functions:

```{code-cell} python
def compose(f, g):
    return lambda x: f(x).bind(g)

fetch_parse = compose(fetch, parse)
result = fetch_parse("http://42")
print(result)
```

## Pipelining

Functional compose of functions that returns wrapped values is called pipeling in the
Expression library. Other languages calls this "Kleisli composition". Using a reducer we
can compose any number of functions:

```{code-cell} python
from functools import reduce

def pipeline(*fns):
    return reduce(lambda res, fn: lambda x: res(x).bind(fn), fns)
```

Now, make `fetch_and_parse` using kleisli:

```{code-cell} python
fetch_and_parse = pipeline(fetch, parse)
result = fetch_and_parse("http://123")
print(result)
```

### What if we wanted to call fetch 10 times in a row?

```{code-cell} python
from expression.extra.result import pipeline

fetch_with_value = lambda x: fetch("http://%s" % x)

request = pipeline(
            fetch,
            fetch_with_value,
            fetch_with_value,
            fetch_with_value,
            fetch_with_value,
            fetch_with_value,
            fetch_with_value,
            parse
          )

result = request("http://123")
print(result)
```

## Result in Expression

The `Result[T, TError]` type in Expression lets you write error-tolerant code that can
be composed. A Result works similar to `Option`, but lets you define the value used for
errors, e.g., an exception type or similar. This is great when you want to know why some
operation failed (not just `Nothing`). This type serves the same purpose of an `Either`
type where `Left` is used for the error condition and `Right` for a success value.

```python
from expression import effect, Ok, Result

@effect.result[int, Exception]()
def fn():
    x = yield from Ok(42)
    y = yield from Ok(10)
    return x + y

xs = fn()
assert isinstance(xs, Result)
```

A simplified type called [`Try`](reference_try) is also available. It's a result type
that is pinned to `Exception` i.e., `Result[TSource, Exception]`. This makes the code
simpler since you don't have specify the error type every time you declare the type of
your result.
