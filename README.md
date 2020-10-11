# F/

[![PyPI](https://img.shields.io/pypi/v/fslash.svg)](https://pypi.python.org/pypi/FSlash)
![Python package](https://github.com/dbrattli/fslash/workflows/Python%20package/badge.svg)
![Upload Python Package](https://github.com/dbrattli/fslash/workflows/Upload%20Python%20Package/badge.svg)
[![codecov](https://codecov.io/gh/dbrattli/FSlash/branch/master/graph/badge.svg)](https://codecov.io/gh/dbrattli/FSlash)

> Python :heart: F#

FSlash (F/) aims to be a solid library for practical functional programming in
Python 3.8+ inspired by [F#](https://fsharp.org). By practical we mean that the
goal of the library if to enable you to do meaningful and productive functional
programming in Python instead of being a [Monad
tutorial](https://github.com/dbrattli/OSlash).

Python is a multi-paradigm programming language that also supports
functional programming constructs such as functions, higher-order
functions, lambdas, and in many ways favors composition over inheritance.

F# is a functional programming language for .NET that is succinct
(concise, readable and type-safe) and kind of
[Pythonic](https://docs.python.org/3/glossary.html). F# looks a lot more
like Python than C# and F# can also do a lot of things better than Python:

- Strongly typed, if it compiles it usually works
- Type inference, the compiler deduces types during compilation
- Expression based language

> Better Python with F#

FSlash tries to make a better Python by providing several functional
features inspired by F# into Python. This serves two purposes:

- Make it easier for Python programmers to learn F# by starting out in a
  programming language they already know. Then get inspired to [try out
  F#](https://aka.ms/fsharphome) by itself.
- Make it easier for F# developers to use Python when needed, and re-use many
  of the concepts and abstractions that they already know and love.

FSlash will enable you to work with Python along with F# using many of
the same programming concepts and abstractions. This enables concepts
such as [Railway oriented
programming](https://fsharpforfunandprofit.com/rop/) (ROP) for better
and predictable error handling. Pipelining for workflows, computational
expressions, etc.

## Getting Started

You can install the latest `fslash` from PyPI by running `pip` (or `pip3`).
Note that `fslash` only works for Python 3.8+.

```sh
$ pip3 install fslash
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

I named the project FSlash since it's an F# inspired version of my previously
written [OSlash](https://github.com/dbrattli/OSlash) monad tutorial where I
ported a number of Haskell abstractions to Python. I never felt that OSlash was
really practically usable in Python, but F# is much closer to Python than
Haskell, so it makes more sense to try and make a functional library inspired
by F# instead.

## Goals

- The resulting code should look and feel like Python. We want to make a
  better Python, not some obscure DSL or academic Monad tutorial
- Provide pipelining and pipe friendly methods.
- Dot-chaining on objects as an alternative syntax to pipes.
- Avoid currying, not supported in Python by default and not a well known
  concept by Python programmers.
- Avoid operator (`|`, `>>`, etc) overloading, this usually confuses more than it helps.
- Use [type-hints](https://docs.python.org/3/library/typing.html) for all
  functions and methods.
- Code should pass static type checking by tools such as
  [mypy](http://mypy-lang.org/) and
  [pylance](https://devblogs.microsoft.com/python/announcing-pylance-fast-feature-rich-language-support-for-python-in-visual-studio-code/). Pylance is awesome, use it!

## Non Goals

- Provide all features of F# and .NET to Python, see [Supported
  Features](https://github.com/dbrattli/fslash#supported-features).

## Supported features

FSlash will never provide you with all the features of F# and .NET. We are
providing a few of the features we think are useful, and will add more
on-demand as we go along.

- **Option** - for optional stuff and better `None` handling.
- **Result** - for better error handling and enables railway-oriented programming
  in Python.
- **Sequence** - a better [itertools](https://docs.python.org/3/library/itertools.html) and fully compatible with Python iterables.
- **List** - an immutable list type.
- **Computational Expressions**: this is actually amazing stuff
  - **option** - an optional world for working with optional values
  - **result** - an error handling world for working with result values
- Pattern matching - provided by [Pampy](https://github.com/santinic/pampy).

### Pipelining

OSlash provides a `pipe` function similar to `|>` in F#. We don't want to
overload any Python operators e.g `|` so `pipe` is a plain old function taking
N-arguments and thus lets you pipe a value though any number of functions.

```py
from fslash.core import pipe

gn = lambda g: g * y
fn = lambda x: x + z
value = pipe(
    x,
    fn,
    gn
)

assert value == gn(fn(x))
```

F/ objects also have a pipe method so you can dot chain pipelines
directly on the object:

```py
from fslash.core import pipe

gn = lambda g: g * y
fn = lambda x: x + z
value = x.pipe(
    fn,
    gn
)

assert value == gn(fn(x))
```


### Options

The option type is used when an actual value might not exist for a named
value or variable. An option has an underlying type and can hold a value of
that type `Some(value)`, or it might not have the value `Nothing`.

```py
from fslash.core import Some, Nothing, Option_

def keep_positive(a: int) -> Option_[int]:
    if a > 0:
        return Some(a)
    else:
        return Nothing
```

```py
from pampy import match

def exists (x : Option_[int]) -> bool:
    return match(
        x,
        Some, lambda some: True,
        Nothing, False
    )
```

Options as decorators for computational expressions. Computational expressions
in OSlash are implemented as coroutines ([enhanced
generators](https://www.python.org/dev/peps/pep-0342/)) using `yield`, `yield from`
and `return` to consume or generate optional values:

```py
from fslash.builders import option
from fslash.core import Some

@option
def fn():
    x = yield 42
    y = yield from Some(43)

    return x + y

xs = fn()
```

This enables ["railway oriented
programming"](https://fsharpforfunandprofit.com/rop/) e.g if one part of the
function yields from `Nothing` then the function is side-tracked
(short-circuit) and the following statements will never be executed. The end
result of the expression will be `Nothing`. Thus results from such a option
decorated function can either be `Ok(value)` or `Error(error_value)`.

```py
from fslash.core import Some, Nothing
from fslash.builders import option

@option
def fn():
    x = yield from Nothing # or a function returning Nothing

    # -- The rest of the function will never be executed --
    y = yield from Some(43)

    return x + y

xs = fn()
assert xs is Nothing
```

For more information about options:

- [Tutorial](https://github.com/dbrattli/FSlash/blob/master/notebooks/Options.ipynb)
- [API reference](https://dbrattli.github.io/FSlash/fslash/core/option.html)

### Results

The `Result[T,TError]` type lets you write error-tolerant code that can be
composed. Result works similar to `Option` but lets you define the value used
for errors, e.g an exception type or similar. This is great when you want to
know why some operation failed (not just `Nothing`).

```py
from fslash.core import Result, Ok, Error, pipe
from fslash.builders import result

@result
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
ys = functools.reduce(lambda s, x: s + x, filter(lambda x: x > 100, map(lambda x: x * 10, xs)), 0)

# With F/ you pipe the result flows from one operator to the next:
zs = pipe(
    xs,
    Seq.map(lambda x: x * 10),
    Seq.filter(lambda x: x > 100),
    Seq.fold(lambda s, x: s + x, 0)
)
assert ys == zs
```

## Notable Differences

In F# you can have a type and a module with the same name, e.g `Option`
is both a module and a type. This is not possible with Python, so
instead we use `Option` as the module to access module functions such as
`Option.map` and the primed `Option_`for the type itself.

## Common Gotchas and Pitfalls

A list of common problems and how you may solve it:

### / The FSlash List type has the same name as the builtin List type in Python

You can import the FSlash list module with e.g a different name:

```py
from fslash.collections import List as FList
```

## / Why are types primed with `_`?

This is because e.g `Option` and `Result` are imported as modules in
order to easily access module functions e.g `Option.map`. We cannot have
types with the same name as modules in Python, so that's why the types
are available as primed `_` names e.g `Option_` and `Result_`.

### / FSlash is missing the function / operator I need

Remember that everything is a function, so you can easily implement the
function yourself and use it with FSlash. If you think the function is
also usable for others, you can open a PR to include it with FSlash.

## Resources

- F# (http://fsharp.org)
- Get Started with F# (https://aka.ms/fsharphome)
- F# as a Better Python - Phillip Carter - NDC Oslo 2020
  (https://www.youtube.com/watch?v=_QnbV6CAWXc)
- Pampy: Pattern Matching for Python (https://github.com/santinic/pampy)
- OSlash (https://github.com/dbrattli/OSlash)
- RxPY (https://github.com/ReactiveX/RxPY)
- PEP 342 -- Coroutines via Enhanced Generators (https://www.python.org/dev/peps/pep-0342/)

## How-to Contribute

You are very welcome to contribute with PRs :heart_eyes: It is nice if you can try
to align the code with F# modules, functions and documentation.

Code, doc-strings and comments should also follow the [Google Python
Style Guide](https://google.github.io/styleguide/pyguide.html).

## License

MIT, see [LICENSE](https://github.com/dbrattli/FSlash/blob/master/LICENSE).