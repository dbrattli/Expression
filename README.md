# Expression

[![PyPI](https://img.shields.io/pypi/v/expression.svg)](https://pypi.python.org/pypi/Expression)
![Python package](https://github.com/dbrattli/expression/workflows/Python%20package/badge.svg)
![Upload Python Package](https://github.com/dbrattli/expression/workflows/Upload%20Python%20Package/badge.svg)
[![codecov](https://codecov.io/gh/dbrattli/expression/branch/master/graph/badge.svg)](https://codecov.io/gh/dbrattli/expression)

> Expressions evaluates to a value. Statements do something.

Expression aims to be a solid library for practical functional
programming in Python 3.8+. By practical we mean that the goal of the
library if to enable you to do productive and meaningful functional
programming in Python instead of being a [Monad
tutorial](https://github.com/dbrattli/OSlash).

Python is a multi-paradigm programming language that also supports
functional programming constructs such as functions, higher-order
functions, lambdas, and in many ways favors composition over inheritance.

> Better Python with F#

Expression tries to make a better Python by providing several functional
features inspired by [F#](https://fsharp.org) into Python. This serves two purposes:

- Make it easier for Python programmers to learn F# by starting out in a
  programming language they already know. Then get inspired to [try out
  F#](https://aka.ms/fsharphome) by itself.
- Make it easier for F# developers to use Python when needed, and re-use many
  of the concepts and abstractions that they already know and love.

Expression will enable you to work with Python along with F# using many of
the same programming concepts and abstractions. This enables concepts
such as [Railway oriented
programming](https://fsharpforfunandprofit.com/rop/) (ROP) for better
and predictable error handling. Pipelining for workflows, computational
expressions, etc.

F# is a functional programming language for .NET that is succinct
(concise, readable and type-safe) and kind of
[Pythonic](https://docs.python.org/3/glossary.html). F# looks a lot more
like Python than C# and F# can also do a lot of things better than Python:

- Strongly typed, if it compiles it usually works
- Type inference, the compiler deduces types during compilation
- Expression based language

## Getting Started

You can install the latest `expression` from PyPI by running `pip` (or `pip3`).
Note that `expression` only works for Python 3.8+.

```sh
$ pip3 install expression
```

## Why

- I love F#, and know F# quite well. I'm the creator of projects such as
  [Oryx](https://github.com/cognitedata/oryx),
  [Fable.Reaction](https://github.com/dbrattli/Fable.Reaction) and
  [Feliz.ViewEngine](https://github.com/dbrattli/Feliz.ViewEngine)
- I love Python, and know Python really well. I'm the creator of both
  [RxPY](https://github.com/ReactiveX/RxPY) and
  [OSlash](https://github.com/dbrattli/OSlash), two functional style libraries
  for Python.

For a long time I'm been wanting to make a "bridge" between these two languages
and got inspired to write this library after watching "[F# as a Better
Python](https://www.youtube.com/watch?v=_QnbV6CAWXc)" - Phillip Carter - NDC
Oslo 2020. Doing a transpiler like [Fable](https://fable.io) for Python is one
option, but a Python library may give a lower barrier and a better introduction
to existing Python programmers.

Expression is an F# inspired version of my previously written
[OSlash](https://github.com/dbrattli/OSlash) monad tutorial where I ported a
number of Haskell abstractions to Python. I never felt that OSlash was really
practically usable in Python, but F# is much closer to Python than Haskell, so
it makes more sense to try and make a functional library inspired by F#
instead.

## Goals

- The resulting code should look and feel like Python. We want to make a
  better Python, not some obscure DSL or academic Monad tutorial
- Provide pipelining and pipe friendly methods. Compose all the things!
- Dot-chaining on objects as an alternative syntax to pipes.
- Avoid currying, not supported in Python by default and not a well known
  concept by Python programmers.
- Avoid operator (`|`, `>>`, etc) overloading, this usually confuses more than it helps.
- Use [type-hints](https://docs.python.org/3/library/typing.html) for all
  functions and methods.
- Code should pass strict static type checking by tools such as
  [mypy](http://mypy-lang.org/) and
  [pylance](https://devblogs.microsoft.com/python/announcing-pylance-fast-feature-rich-language-support-for-python-in-visual-studio-code/).
  Pylance is awesome, use it!

## Supported features

Expression will never provide you with all the features of F# and .NET. We are
providing a few of the features we think are useful, and will add more
on-demand as we go along.

- **Option** - for optional stuff and better `None` handling.
- **Result** - for better error handling and enables railway-oriented programming
  in Python.
- **Sequence** - a better [itertools](https://docs.python.org/3/library/itertools.html) and fully compatible with Python iterables.
- **FrozenList** - a frozen and immutable list type.
- **Effects**: - light weight computational expressions for Python. This is actually amazing stuff.
  - **option** - an optional world for working with optional values.
  - **result** - an error handling world for working with result values.
- **Mailbox Processor**: for lock free programming using the [Actor model](https://en.wikipedia.org/wiki/Actor_model).
- **Cancellation Token**: for cancellation of asynchronous (and synchronous) workflows.
- **Disposable**: For resource management.

Pattern matching is provided by [Pampy](https://github.com/santinic/pampy),
while we wait for [PEP 634](https://www.python.org/dev/peps/pep-0634/) and
structural pattern matching for Python.

### Pipelining

Expression provides a `pipe` function similar to `|>` in F#. We don't want to
overload any Python operators e.g `|` so `pipe` is a plain old function taking
N-arguments and thus lets you pipe a value though any number of functions.

```py
from expression.core import pipe

gn = lambda g: g * y
fn = lambda x: x + z
value = pipe(
    x,
    fn,
    gn
)

assert value == gn(fn(x))
```

Expression objects also have a pipe method so you can dot chain pipelines
directly on the object:

```py
from expression.core import pipe

gn = lambda g: g * y
fn = lambda x: x + z
value = x.pipe(
    fn,
    gn
)

assert value == gn(fn(x))
```

So for example with sequences you may create sequence transforming
pipelines:

```py
ys = xs.pipe(
    seq.map(lambda x: x * 10),
    seq.filter(lambda x: x > 100),
    seq.fold(lambda s, x: s + x, 0)
)
```

### Composition

Functions may even be composed directly into custom operators:

```py
from expression.core import compose

custom = compose(
    seq.map(lambda x: x * 10),
    seq.filter(lambda x: x > 100),
    seq.fold(lambda s, x: s + x, 0)
)

ys = custom(xs)

```

### Options

The option type is used when an actual value might not exist for a named
value or variable. An option has an underlying type and can hold a value of
that type `Some(value)`, or it might not have the value `Nothing`.

```py
from expression.core import Some, Nothing, Option

def keep_positive(a: int) -> Option[int]:
    if a > 0:
        return Some(a)
    else:
        return Nothing
```

```py
from pampy import _

def exists(x : Option[int]) -> bool:
    return x.match(
        Some, lambda some: True,
        _, False
    )
```

Options as decorators for computational expressions. Computational expressions
in Expression are implemented as coroutines ([enhanced
generators](https://www.python.org/dev/peps/pep-0342/)) using `yield`, `yield from`
and `return` to consume or generate optional values:

```py
from expression.builders import option
from expression.core import Some

@option
def fn():
    x = yield 42
    y = yield from Some(43)

    return x + y

xs = fn()
```

This enables ["railway oriented
programming"](https://fsharpforfunandprofit.com/rop/) e.g if one part of
the function yields from `Nothing` then the function is side-tracked
(short-circuit) and the following statements will never be executed. The
end result of the expression will be `Nothing`. Thus results from such
an option decorated function can either be `Ok(value)` or
`Error(error_value)`.

```py
from expression.core import Some, Nothing
from expression import effect

@effect.option
def fn():
    x = yield from Nothing # or a function returning Nothing

    # -- The rest of the function will never be executed --
    y = yield from Some(43)

    return x + y

xs = fn()
assert xs is Nothing
```

For more information about options:

- [Tutorial](https://github.com/dbrattli/Expression/blob/master/notebooks/Options.ipynb)
- [API reference](https://dbrattli.github.io/Expression/expression/core/option.html)

### Results

The `Result[T, TError]` type lets you write error-tolerant code that can
be composed. Result works similar to `Option` but lets you define the
value used for errors, e.g an exception type or similar. This is great
when you want to know why some operation failed (not just `Nothing`).

```py
from expression.core import Result, Ok, Error, pipe
from expression import effect

@effect.result
def fn():
    x = yield from Ok(42)
    y = yield from OK(10)
    return x + y

xs = fn()
assert isinstance(xs, Some)
```

### Sequences

Contains operations for working with iterables. Thus all the functions
in this module will work on normal Python iterables. Iterables are
already immutable by design, so they are already perfectly suited for
using with functional programming.

```py
# Normal python way. Nested functions are hard to read since you need to
# start reading from the end of the expression.
xs = range(100)
ys = functools.reduce(lambda s, x: s + x, filter(lambda x: x > 100, map(lambda x: x * 10, xs)), 0)

# With Expression you pipe the result so it flows from one operator to the next:
ys = seq.of(xs).pipe(
    seq.map(lambda x: x * 10),
    seq.filter(lambda x: x > 100),
    seq.fold(lambda s, x: s + x, 0)
)
assert ys == zs
```

## Notable Differences

In F# you modules are capitalized, in Python they are lowercase
([PEP-8](https://www.python.org/dev/peps/pep-0008/#package-and-module-names)).
E.g in F# `Option` is both a module and a type. In Python the module is
`option` and the type is capitalized i.e `Option`.

Thus in Expression you use `option` as the module to access module
functions such as `option.map` and the name `Option` for the type
itself.

```py
>>> from expression.core import Option, option
>>> Option
<class 'expression.core.option.Option'>
>>> option
<module 'expression.core.option' from '/Users/dbrattli/Developer/Github/Expression/expression/core/option.py'>
```

## Common Gotchas and Pitfalls

A list of common problems and how you may solve it:

### Expression is missing the function / operator I need

Remember that everything is a function, so you can easily implement the
function yourself and use it with Expression. If you think the function
is also usable for others, then please open a PR to include it with
Expression.

## Resources

- F# (http://fsharp.org)
- Get Started with F# (https://aka.ms/fsharphome)
- F# as a Better Python - Phillip Carter - NDC Oslo 2020
  (https://www.youtube.com/watch?v=_QnbV6CAWXc)
- Pampy: Pattern Matching for Python (https://github.com/santinic/pampy)
- OSlash (https://github.com/dbrattli/OSlash)
- RxPY (https://github.com/ReactiveX/RxPY)
- PEP 342 -- Coroutines via Enhanced Generators (https://www.python.org/dev/peps/pep-0342/)
- PEP 380 -- Syntax for Delegating to a Subgenerator (https://www.python.org/dev/peps/pep-0380)
- PEP 479 -- Change StopIteration handling inside generators

## How-to Contribute

You are very welcome to contribute with PRs :heart_eyes: It is nice if
you can try to align the code with F# modules, functions and
documentation. But submit a PR even if you should feel unsure.

Code, doc-strings and comments should also follow the [Google Python
Style Guide](https://google.github.io/styleguide/pyguide.html). Code is
formatted using [Black](https://github.com/psf/black)

## License

MIT, see [LICENSE](https://github.com/dbrattli/Expression/blob/master/LICENSE).