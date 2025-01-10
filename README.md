# Expression

[![PyPI](https://img.shields.io/pypi/v/expression.svg)](https://pypi.python.org/pypi/Expression)
![Python package](https://github.com/cognitedata/expression/workflows/Python%20package/badge.svg)
[![Publish Package](https://github.com/dbrattli/Expression/actions/workflows/python-publish.yml/badge.svg)](https://github.com/dbrattli/Expression/actions/workflows/python-publish.yml)
[![Documentation Status](https://readthedocs.org/projects/expression/badge/?version=latest)](https://expression.readthedocs.io/en/latest/?badge=latest)
[![codecov](https://codecov.io/gh/cognitedata/expression/branch/main/graph/badge.svg)](https://codecov.io/gh/cognitedata/expression)

> Pragmatic functional programming

Expression aims to be a solid, type-safe, pragmatic, and high performance
library for frictionless and practical functional programming in Python 3.10+.

By pragmatic, we mean that the goal of the library is to use simple abstractions
to enable you to do practical and productive functional programming in Python
(instead of being a [Monad tutorial](https://github.com/dbrattli/OSlash)).

Python is a multi-paradigm programming language that also supports functional
programming constructs such as functions, higher-order functions, lambdas, and
in many ways favors composition over inheritance.

> Better Python with F#

Expression tries to make a better Python by providing several functional
features inspired by [F#](https://fsharp.org). This serves several
purposes:

- Enable functional programming in a Pythonic way, i.e., make sure we are not
  over-abstracting things. Expression will not require purely functional
  programming as would a language like Haskell.
- Everything you learn with Expression can also be used with F#. Learn F# by
  starting in a programming language they already know. Perhaps get inspired to
  also [try out F#](https://aka.ms/fsharphome) by itself.
- Make it easier for F# developers to use Python when needed, and re-use many
  of the concepts and abstractions they already know and love.

Expression will enable you to work with Python using many of the same
programming concepts and abstractions. This enables concepts such as [Railway
oriented programming](https://fsharpforfunandprofit.com/rop/) (ROP) for better
and predictable error handling. Pipelining for workflows, computational
expressions, etc.

> _Expressions evaluate to a value. Statements do something._

F# is a functional programming language for .NET that is succinct (concise,
readable, and type-safe) and kind of
[Pythonic](https://docs.python.org/3/glossary.html). F# is in many ways very
similar to Python, but F# can also do a lot of things better than Python:

- Strongly typed, if it compiles it usually works making refactoring much
  safer. You can trust the type-system. With [mypy](http://mypy-lang.org/) or
  [Pylance](https://github.com/microsoft/pylance-release) you often wonder who
  is right and who is wrong.
- Type inference, the compiler deduces types during compilation
- Expression based language

## Getting Started

You can install the latest `expression` from PyPI by running `pip` (or
`pip3`). Note that `expression` only works for Python 3.10+.

```console
> pip install expression
```

To add Pydantic v2 support, install the `pydantic` extra:

```console
> pip install expression[pydantic]
```

## Goals

- Industrial strength library for functional programming in Python.
- The resulting code should look and feel like Python
  ([PEP-8](https://www.python.org/dev/peps/pep-0008/)). We want to make a
  better Python, not some obscure DSL or academic Monad tutorial.
- Provide pipelining and pipe friendly methods. Compose all the things!
- Dot-chaining on objects as an alternative syntax to pipes.
- Lower the cognitive load on the programmer by:
  - Avoid currying, not supported in Python by default and not a well known
    concept by Python programmers.
  - Avoid operator (`|`, `>>`, etc) overloading, this usually confuses more
    than it helps.
  - Avoid recursion. Recursion is not normally used in Python and any use of it
    should be hidden within the SDK.
- Provide [type-hints](https://docs.python.org/3/library/typing.html) for all
  functions and methods.
- Support PEP 634 and structural pattern matching.
- Code must pass strict static type checking by
  [Pylance](https://devblogs.microsoft.com/python/announcing-pylance-fast-feature-rich-language-support-for-python-in-visual-studio-code/).
  Pylance is awesome, use it!
- [Pydantic](https://pydantic-docs.helpmanual.io/) friendly data types. Use Expression
  types as part of your Pydantic data model and (de)serialize to/from JSON.

## Supported features

Expression will never provide you with all the features of F# and .NET. We are
providing a few of the features we think are useful, and will add more
on-demand as we go along.

- **Pipelining** - for creating workflows.
- **Composition** - for composing and creating new operators.
- **Fluent or Functional** syntax, i.e., dot chain or pipeline operators.
- **Pattern Matching** - an alternative flow control to `if-elif-else`.
- **Error Handling** - Several error handling types.
  - **Option** - for optional stuff and better `None` handling.
  - **Result** - for better error handling and enables railway-oriented
    programming in Python.
  - **Try** - a simpler result type that pins the error to an Exception.
- **Collections** - immutable collections.
  - **TypedArray** - a generic array type that abstracts the details of
    `bytearray`, `array.array` and `list` modules.
  - **Sequence** - a better
    [itertools](https://docs.python.org/3/library/itertools.html) and
    fully compatible with Python iterables.
  - **Block** - a frozen and immutable list type.
  - **Map** - a frozen and immutable dictionary type.
  - **AsyncSeq** - Asynchronous iterables.
  - **AsyncObservable** - Asynchronous observables. Provided separately
    by [aioreactive](https://github.com/dbrattli/aioreactive).
- **Data Modelling** - sum and product types
  - **@tagged_union** - A tagged (discriminated) union type decorator.
- **Parser Combinators** - A recursive decent string parser combinator
  library.
- **Effects**: - lightweight computational expressions for Python. This
  is amazing stuff.
  - **option** - an optional world for working with optional values.
  - **result** - an error handling world for working with result values.
- **Mailbox Processor**: for lock free programming using the [Actor
  model](https://en.wikipedia.org/wiki/Actor_model).
- **Cancellation Token**: for cancellation of asynchronous (and
  synchronous) workflows.
- **Disposable**: For resource management.

### Pipelining

Expression provides a `pipe` function similar to `|>` in F#. We don't want to
overload any Python operators, e.g., `|` so `pipe` is a plain old function taking
N-arguments, and will let you pipe a value through any number of functions.

```python
from expression import pipe

v = 1
fn = lambda x: x + 1
gn = lambda x: x * 2

assert pipe(v, fn, gn) == gn(fn(v))
```

Expression objects (e.g., `Some`, `Seq`, `Result`) also have a `pipe` method, so you can dot chain pipelines
directly on the object:

```python
from expression import Some

v = Some(1)
fn = lambda x: x.map(lambda y: y + 1)
gn = lambda x: x.map(lambda y: y * 2)

assert v.pipe(fn, gn) == gn(fn(v))
```

So for example with sequences you may create sequence transforming
pipelines:

```python
from expression.collections import seq, Seq

# Since static type checkes aren't good good at inferring lambda types
mapper: Callable[[int], int] = lambda x: x * 10
predicate: Callable[[int], bool] = lambda x: x > 100
folder: Callable[[int, int], int] = lambda s, x: s + x

xs = Seq.of(9, 10, 11)
ys = xs.pipe(
    seq.map(mapper),
    seq.filter(predicate),
    seq.fold(folder, 0),
)

assert ys == 110
```

### Composition

Functions may even be composed directly into custom operators:

```python
from expression import compose
from expression.collections import seq, Seq

xs = Seq.of(9, 10, 11)
custom = compose(
    seq.map(lambda x: x * 10),
    seq.filter(lambda x: x > 100),
    seq.fold(lambda s, x: s + x, 0)
)
ys = custom(xs)

assert ys == 110
```

### Fluent and Functional

Expression can be used both with a fluent or functional syntax (or both.)

#### Fluent syntax

The fluent syntax uses methods and is very compact. But it might get you into
trouble for large pipelines since it's not a natural way of adding line breaks.

```python
from expression.collections import Seq

xs = Seq.of(1, 2, 3)
ys = xs.map(lambda x: x * 100).filter(lambda x: x > 100).fold(lambda s, x: s + x, 0)
```

Note that fluent syntax is probably the better choice if you use mypy
for type checking since mypy may have problems inferring types through
larger pipelines.

#### Functional syntax

The functional syntax is a bit more verbose but you can easily add new
operations on new lines. The functional syntax is great to use together
with pylance/pyright.

```python
from expression import pipe
from expression.collections import seq, Seq

xs = Seq.of(1, 2, 3)
ys = pipe(xs,
    seq.map(lambda x: x * 100),
    seq.filter(lambda x: x > 100),
    seq.fold(lambda s, x: s + x, 0),
)
```

Both fluent and functional syntax may be mixed and even pipe can be used
fluently.

```python
from expression.collections import seq, Seq
xs = Seq.of(1, 2, 3).pipe(seq.map(...))
```

### Option

The `Option` type is used when a function or method cannot produce a meaningful
output for a given input.

An option value may have a value of a given type, i.e., `Some(value)`, or it might
not have any meaningful value, i.e., `Nothing`.

```python
from expression import Some, Nothing, Option

def keep_positive(a: int) -> Option[int]:
    if a > 0:
        return Some(a)

    return Nothing
```

```python
from expression import Option, Ok
def exists(x : Option[int]) -> bool:
    match x:
        case Some(_):
            return True
    return False
```

### Option as an effect

Effects in Expression is implemented as specially decorated coroutines
([enhanced generators](https://www.python.org/dev/peps/pep-0342/)) using
`yield`, `yield from` and `return` to consume or generate optional values:

```python
from expression import effect, Some

@effect.option[int]()
def fn():
    x = yield 42
    y = yield from Some(43)

    return x + y

xs = fn()
```

This enables ["railway oriented
programming"](https://fsharpforfunandprofit.com/rop/), e.g., if one part of the
function yields from `Nothing` then the function is side-tracked
(short-circuit) and the following statements will never be executed. The end
result of the expression will be `Nothing`. Thus results from such an option
decorated function can either be `Ok(value)` or `Error(error_value)`.

```python
from expression import effect, Some, Nothing

@effect.option[int]()
def fn():
    x = yield from Nothing # or a function returning Nothing

    # -- The rest of the function will never be executed --
    y = yield from Some(43)

    return x + y

xs = fn()
assert xs is Nothing
```

### Option as an applicative

In functional programming, we sometimes want to combine two Option values into a new Option. However, this combination
should only happen if both Options are Some. If either Option is None, the resulting value should also be None.

The map2 function allows us to achieve this behavior. It takes two Option values and a function as arguments. The
function is applied only if both Options are Some, and the result becomes the new Some value. Otherwise, map2 returns
None.

This approach ensures that our combined value reflects the presence or absence of data in the original Options.

```python
from expression import Some, Nothing, Option
from operator import add

def keep_positive(a: int) -> Option[int]:
    if a > 0:
        return Some(a)
    else:
      return Nothing

def add_options(a: Option[int], b: Option[int]):
  return a.map2(add, b)

assert add_options(
  keep_positive(4),
  keep_positive(-2)
) is Nothing

assert add_options(
  keep_positive(3),
  keep_positive(2)
) == Some(5)

```

For more information about options:

- [Tutorial](https://expression.readthedocs.io/en/latest/tutorial/optional_values.html)
- [API reference](https://expression.readthedocs.io/en/latest/reference/option.html)

### Result

The `Result[T, TError]` type lets you write error-tolerant code that can be
composed. A Result works similar to `Option`, but lets you define the value used
for errors, e.g., an exception type or similar. This is great when you want to
know why some operation failed (not just `Nothing`). This type serves the same
purpose of an `Either` type where `Left` is used for the error condition and `Right`
for a success value.

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

A simplified type called `Try` is also available. It's a result type that is
pinned to `Exception` i.e., `Result[TSource, Exception]`.

### Sequence

Sequences is a thin wrapper on top of iterables and contains operations for working with
Python iterables. Iterables are immutable by design, and perfectly suited for functional
programming.

```python
import functools
from expression import pipe
from expression.collections import seq

# Normal python way. Nested functions are hard to read since you need to
# start reading from the end of the expression.
xs = range(100)
ys = functools.reduce(lambda s, x: s + x, filter(lambda x: x > 100, map(lambda x: x * 10, xs)), 0)

# With Expression, you pipe the result, so it flows from one operator to the next:
zs = pipe(
    xs,
    seq.map(lambda x: x * 10),
    seq.filter(lambda x: x > 100),
    seq.fold(lambda s, x: s + x, 0),
)
assert ys == zs
```

## Tagged Unions

Tagged Unions (aka discriminated unions) may look similar to normal Python Unions. But
they are [different](https://stackoverflow.com/a/61646841) in that the operands in a
type union `(A | B)` are both types, while the cases in a tagged union type `U = A | B`
are both constructors for the type U and are not types themselves. One consequence is
that tagged unions can be nested in a way union types might not.

In Expression you make a tagged union by defining your type similar to a `dataclass` and
decorate it with `@tagged_union` and add the appropriate generic types that this union
represent for each case. Then you optionally define static or class-method constructors
for creating each of the tagged union cases.

```python
from dataclasses import dataclass
from expression import TaggedUnion, tag

@dataclass
class Rectangle:
    width: float
    length: float

@dataclass
class Circle:
    radius: float

@tagged_union
class Shape:
    tag: Literal["rectangle", "circle"] = tag()

    rectangle: Rectangle = case()
    circle: Circle = case()

    @staticmethod
    def Rectangle(width: float, length: float) -> Shape:
        """Optional static method for creating a tagged union case"""
        return Shape(rectangle=Rectangle(width, length))

    @staticmethod
    def Circle(radius: float) -> Shape:
        """Optional static method for creating a tagged union case"""
        return Shape(circle=Circle(radius))
```

Note that the tag field is optional, but recommended. If you don't specify a tag field
then then it will be created for you, but static type checkers will not be able to type
check correctly when pattern matching. The `tag` field if specified should be a literal
type with all the possible values for the tag. This is used by static type checkers to
check exhaustiveness of pattern matching.

Each case is given the `case()` field initializer. This is optional, but recommended for
static type checkers to work correctly. It's not required for the code to work properly,

Now you may pattern match the shape to get back the actual value:

```python
    shape = Shape.Rectangle(2.3, 3.3)

    match shape:
        case Shape(tag="rectangle", rectangle=Rectangle(width=2.3)):
            assert shape.value.width == 2.3
        case _:
            assert False
```

Note that when matching keyword arguments, then the `tag` keyword argument must be
specified for static type checkers to check exhaustiveness correctly. It's not required
for the code to work properly, but it's recommended to avoid typing errors.

## Notable differences between Expression and F\#

In F# modules are capitalized, in Python they are lowercase
([PEP-8](https://www.python.org/dev/peps/pep-0008/#package-and-module-names)).
E.g in F# `Option` is both a module (`OptionModule` internally) and a
type. In Python the module is `option` and the type is capitalized i.e
`Option`.

Thus in Expression you use `option` as the module to access module functions
such as `option.map` and the name `Option` for the type itself.

```pycon
>>> from expression import Option, option
>>> Option
<class 'expression.core.option.Option'>
>>> option
<module 'expression.core.option' from '/Users/dbrattli/Developer/Github/Expression/expression/core/option.py'>
```

## Common Gotchas and Pitfalls

A list of common problems and how you may solve it:

### Expression is missing the function/operator I need

Remember that everything is just a function, so you can easily implement
a custom function yourself and use it with Expression. If you think the
function is also usable for others, then please open a PR to include it
with Expression.

## Resources and References

A collection of resources that were used as reference and inspiration
for creating this library.

- F# (<http://fsharp.org>)
- Get Started with F# (<https://aka.ms/fsharphome>)
- F# as a Better Python - Phillip Carter - NDC Oslo 2020
  (<https://www.youtube.com/watch?v=_QnbV6CAWXc>)
- OSlash (<https://github.com/dbrattli/OSlash>)
- RxPY (<https://github.com/ReactiveX/RxPY>)
- PEP 8 -- Style Guide for Python Code (<https://www.python.org/dev/peps/pep-0008/>)
- PEP 342 -- Coroutines via Enhanced Generators
  (<https://www.python.org/dev/peps/pep-0342/>)
- PEP 380 -- Syntax for Delegating to a Subgenerator
  (<https://www.python.org/dev/peps/pep-0380>)
- PEP 479 -- Change StopIteration handling inside generators (<https://www.python.org/dev/peps/pep-0479/>)
- PEP 634 -- Structural Pattern Matching (<https://www.python.org/dev/peps/pep-0634/>)
- Thunks, Trampolines and Continuation Passing
  (<https://jtauber.com/blog/2008/03/30/thunks,_trampolines_and_continuation_passing/>)
- Tail Recursion Elimination
  (<http://neopythonic.blogspot.com/2009/04/tail-recursion-elimination.html>)
- Final Words on Tail Calls
  (<http://neopythonic.blogspot.com/2009/04/final-words-on-tail-calls.html>)
- Python is the Haskell You Never Knew You Had: Tail Call Optimization
  (<https://sagnibak.github.io/blog/python-is-haskell-tail-recursion/>)

## How-to Contribute

You are very welcome to contribute with suggestions or PRs :heart_eyes: It is
nice if you can try to align the code and naming with F# modules, functions,
and documentation if possible. But submit a PR even if you should feel unsure.

Code, doc-strings, and comments should also follow the [Google Python Style
Guide](https://google.github.io/styleguide/pyguide.html).

Code checks are done using

- [Ruff](https://github.com/astral-sh/ruff)

To run code checks on changed files every time you commit, install the pre-commit hooks
by running:

```console
> pre-commit install
```

## Code of Conduct

This project follows <https://www.contributor-covenant.org>, see our [Code
of
Conduct](https://github.com/cognitedata/Expression/blob/main/CODE_OF_CONDUCT.md).

## License

MIT, see [LICENSE](https://github.com/cognitedata/Expression/blob/main/LICENSE).
