# Expression

[![PyPI](https://img.shields.io/pypi/v/expression.svg)](https://pypi.python.org/pypi/Expression)
![Python package](https://github.com/cognitedata/expression/workflows/Python%20package/badge.svg)
![Upload Python Package](https://github.com/cognitedata/expression/workflows/Upload%20Python%20Package/badge.svg)
[![codecov](https://codecov.io/gh/cognitedata/expression/branch/main/graph/badge.svg)](https://codecov.io/gh/cognitedata/expression)

> Pragmatic functional programming

Expression aims to be a solid, type-safe, pragmatic, and high performance
library for frictionless and practical functional programming in Python 3.8+.

By pragmatic we mean that the goal of the library is to use simple abstractions
to enable you to do practical and productive functional programming in Python
(instead of being a [Monad tutorial](https://github.com/dbrattli/OSlash)).

Python is a multi-paradigm programming language that also supports functional
programming constructs such as functions, higher-order functions, lambdas, and
in many ways favors composition over inheritance.

> Better Python with F#

Expression tries to make a better Python by providing several functional
features inspired by [F#](https://fsharp.org) into Python. This serves several
purposes:

- Enable functional programming in a Pythonic way. I.e make sure we are not
  over-abstracting things. Expressions will not be anywhere close to e.g
  Haskell.
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

> *Expressions evaluate to a value. Statements do something.*

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
`pip3`). Note that `expression` only works for Python 3.8+.

```sh
$ pip3 install expression
```

## Tutorial

> Functional Programming in Python:

1. [Introduction](https://github.com/cognitedata/Expression/blob/main/notebooks/01%20-%20Introduction.md)
2. [Collections](https://github.com/cognitedata/Expression/blob/main/notebooks/02%20-%20Containers.md)
3. [Lambda Calculus](https://github.com/cognitedata/Expression/blob/main/notebooks/03%20-%20Lambda%20Calculus.md)
4. [Optional Values](https://github.com/cognitedata/Expression/blob/main/notebooks/04%20-%20Optional%20Values.md)
5. [Railway Oriented Programming](https://github.com/cognitedata/Expression/blob/main/notebooks/05%20-%20Railway%20Oriented%20Programming.md)
6. [Effects and Side-effects](https://github.com/cognitedata/Expression/blob/main/notebooks/06%20-%20Effects%20and%20Side-Effects.md)

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
- Code must pass strict static type checking by [pylance](https://devblogs.microsoft.com/python/announcing-pylance-fast-feature-rich-language-support-for-python-in-visual-studio-code/). Pylance is awesome, use it!

## Supported features

Expression will never provide you with all the features of F# and .NET. We are
providing a few of the features we think are useful, and will add more
on-demand as we go along.

- **Pipelining** - for creating workflows.
- **Composition** - for composing and creating new operators
- **Fluent or Functional** syntax, i.e dot chain or pipeline operators.
- **Pattern Matching** - an alternative flow control to
  `if-elif-else`.
- **Error Handling** - Several error handling types
  - **Option** - for optional stuff and better `None` handling.
  - **Result** - for better error handling and enables railway-oriented
    programming in Python.
  - **Try** - a simpler result type that pins the error to an Exception.
- **Collections** - immutable collections.
  - **Sequence** - a better
    [itertools](https://docs.python.org/3/library/itertools.html) and
    fully compatible with Python iterables.
  - **FrozenList** - a frozen and immutable list type.
  - **Map** - a frozen and immutable dictionary type.
  - **AsyncSeq** - Asynchronous iterables.
  - **AsyncObservable** - Asynchronous observables. Provided separately
    by [aioreactive](https://github.com/dbrattli/aioreactive).
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
overload any Python operators e.g `|` so `pipe` is a plain old function taking
N-arguments, and will let you pipe a value through any number of functions.

```py
from expression import pipe

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
from expression import pipe

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

```python
from expression import compose

custom = compose(
    seq.map(lambda x: x * 10),
    seq.filter(lambda x: x > 100),
    seq.fold(lambda s, x: s + x, 0)
)

ys = custom(xs)
```
## Fluent and Functional

Expression can be used both with a fluent or functional syntax (or both.)

### Fluent syntax

The fluent syntax uses methods and is very compact. But it might get you into
trouble for large pipelines since it's not a natural way of adding line breaks.

```python
xs = Seq.of(1, 2, 3)
ys = xs.map(lambda x: x * 100).filter(lambda x: x > 100).fold(lambda s, x: s + x, 0)
```

Note that fluent syntax is probably the better choice if you use mypy
for type checking since mypy may have problems inferring types through
larger pipelines.
### Functional syntax

The functional syntax is a bit more verbose but you can easily add new
operations on new lines. The functional syntax is great to use together
with pylance/pyright.

```python
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
xs = Seq.of(1, 2, 3).pipe(seq.map(...))
````

### Options

The option type is used when a function or method cannot produce a meaningful
output for a given input.

An option value may have a value of a given type i.e `Some(value)`, or it might
not have any meaningful value, i.e `Nothing`.

```py
from expression import Some, Nothing, Option

def keep_positive(a: int) -> Option[int]:
    if a > 0:
        return Some(a)

    return Nothing
```

```py
def exists(x : Option[int]) -> bool:
    for value in x.match(Ok):
        return True

    return False
```

## Options as effects

Effects in Expression is implemented as specially decorated coroutines
([enhanced generators](https://www.python.org/dev/peps/pep-0342/)) using
`yield`, `yield from` and `return` to consume or generate optional values:

```py
from expression import effect, Some

@effect.option
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
result of the expression will be `Nothing`. Thus results from such an option
decorated function can either be `Ok(value)` or `Error(error_value)`.

```py
from expression import effect, Some, Nothing

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

- [Tutorial](https://github.com/cognitedata/Expression/blob/main/notebooks/04%20-%20Optional%20Values.ipynb)
- [API reference](https://cognitedata.github.io/Expression/expression/core/option.html)

### Results

The `Result[T, TError]` type lets you write error-tolerant code that can be
composed. A Result works similar to `Option` but lets you define the value used
for errors, e.g an exception type or similar. This is great when you want to
know why some operation failed (not just `Nothing`).

```py
from expression import effect, Result, Ok, Error, pipe

@effect.result
def fn():
    x = yield from Ok(42)
    y = yield from OK(10)
    return x + y

xs = fn()
assert isinstance(xs, Some)
```

A simplified type called `Try` is also available. It's a result type that is
pinned to `Exception` i.e `Result[TSource, Exception]`.

### Sequences

Contains operations for working with iterables so all the functions in the
sequence module will work with Python iterables. Iterables are immutable by
design, and perfectly suited for functional programming.

```py
# Normal python way. Nested functions are hard to read since you need to
# start reading from the end of the expression.
xs = range(100)
ys = functools.reduce(lambda s, x: s + x, filter(lambda x: x > 100, map(lambda x: x * 10, xs)), 0)

# With Expression you pipe the result so it flows from one operator to the next:
ys = pipe(
    xs,
    seq.map(lambda x: x * 10),
    seq.filter(lambda x: x > 100),
    seq.fold(lambda s, x: s + x, 0),
)
assert ys == zs
```

### Pattern Matching

Pattern matching is tricky for a language like Python. We are waiting for [PEP
634](https://www.python.org/dev/peps/pep-0634/) and structural pattern matching
for Python. But we need something that can by handled by static type checkers
and will also decompose or unwrap inner values.

What we want to achieve with pattern matching:

- Check multiple cases with default handling if no match is found.
- Only one case will ever match. This reduces the cognitive load on the
  programmer.
- Type safety. We need the code to pass static type checkers.
- Decomposing of wrapped values, e.g options, and results.
- Case handling must be inline, i.e we want to avoid lambdas which would make
  things difficult for e.g async code.
- Pythonic. Is it possible to use something that still looks like Python code?

The solution we propose is based on loops, singleton iterables and resource
management. This lets us write our code inline, decompose, and unwrap inner
values, and also effectively skip the cases that do not match.

```py
from expression import match

with match("expression") as case:
    if case("rxpy"):  # will not match
        assert False

    for value in case(str):  # will match
        assert value == "expression"

    for value in case(float):  # will not match
        assert False

    if case._:  # will run if any previous case does not match
        assert False
```

Using `match` as a context manager will make sure that a case was actually
found. You might need to have a default handler to avoid `MatchFailureError`.

Test cases may be additionally be wrapped in a function to have a match
expression that returns a value:

```py
def matcher(value) -> Option[int]:
    with match(value) as case:
        for value in case(Some[int]):
            return Some(42)

        if case._:
            return Some(2)

    return Nothing

result = matcher(42).
```

Classes may also support `match` fluently, i.e:
`xs.match(pattern)`. If you add generic types to the pattern then
unwrapped values will get the right type without having to cast.

```py
    xs = Some(42)
    ys = xs.map(lambda x: x + 1)

    for value in ys.match(Some[int]):
        assert value == 43
        break
    else:
        assert False
```

Pattern matching can also be used with destructuring of e.g iterables:

```py
xs: FrozenList[int] = empty.cons(42)
for (head, *tail) in xs.match(FrozenList):
    assert head == 42
```

Classes can support more advanced pattern matching and decompose inner values
by subclassing or implementing the matching protocol.

```py
class SupportsMatch(Protocol[TSource]):
    """Pattern matching protocol."""

    @abstractmethod
    def __match__(self, pattern: Any) -> Iterable[TSource]:
        """Return a singleton iterable item (e.g `[value]`) if pattern
        matches, else an empty iterable (e.g. `[]`)."""
        raise NotImplementedError
```

This significantly simplifies the decomposition and type handling
compared to using `isinstance` directly. E.g code from
[aioreactive](https://github.com/dbrattli/aioreactive/blob/master/aioreactive/combine.py#L64):

```py
if isinstance(msg, InnerObservableMsg):
    msg = cast(InnerObservableMsg[TSource], msg)
    xs: AsyncObservable[TSource] = msg.inner_observable
    ...
```

Now becomes:

```py
with match(msg) as case:
    for xs in case(InnerObservableMsg[TSource]):
        ...
```

Note that the matching protocol may be implemented by both values and
patterns. Patterns implementing the matching protocol effectively
becomes active patterns.

```python
class ParseInteger_(SupportsMatch[int]):
    """Active pattern for parsing integers."""

    def __match__(self, pattern: Any) -> Iterable[int]:
        """Match value with pattern."""

        try:
            number = int(pattern)
        except ValueError:
            return []
        else:
            return [number]

ParseInteger = ParseInteger_()  # Pattern singleton instance

text = "42"
with match(text) as case:
    for value in case(ParseInteger):
        assert value == int(text)

    if case._:
        assert False
```

## Notable Differences

In F# modules are capitalized, in Python they are lowercase
([PEP-8](https://www.python.org/dev/peps/pep-0008/#package-and-module-names)).
E.g in F# `Option` is both a module (`OptionModule` internally) and a
type. In Python the module is `option` and the type is capitalized i.e
`Option`.

Thus in Expression you use `option` as the module to access module functions
such as `option.map` and the name `Option` for the type itself.

```py
>>> from expression import Option, option
>>> Option
<class 'expression.core.option.Option'>
>>> option
<module 'expression.core.option' from '/Users/dbrattli/Developer/Github/Expression/expression/core/option.py'>
```

F# pattern matching is awesome and the alternative we present here
cannot be compared. But it helps us match and decompose without having
to type-cast every time.

## Common Gotchas and Pitfalls

A list of common problems and how you may solve it:

### Expression is missing the function/operator I need

Remember that everything is a function, so you can easily implement the
function yourself and use it with Expression. If you think the function
is also usable for others, then please open a PR to include it with
Expression.

## Resources and References

A collection of resources that were used as reference and inspiration
for creating this library.

- F# (http://fsharp.org)
- Get Started with F# (https://aka.ms/fsharphome)
- F# as a Better Python - Phillip Carter - NDC Oslo 2020
  (https://www.youtube.com/watch?v=_QnbV6CAWXc)
- OSlash (https://github.com/dbrattli/OSlash)
- RxPY (https://github.com/ReactiveX/RxPY)
- PEP 8 -- Style Guide for Python Code (https://www.python.org/dev/peps/pep-0008/)
- PEP 342 -- Coroutines via Enhanced Generators
  (https://www.python.org/dev/peps/pep-0342/)
- PEP 380 -- Syntax for Delegating to a Subgenerator
  (https://www.python.org/dev/peps/pep-0380)
- PEP 479 -- Change StopIteration handling inside generators (https://www.python.org/dev/peps/pep-0479/)
- PEP 634 -- Structural Pattern Matching (https://www.python.org/dev/peps/pep-0634/)
- Thunks, Trampolines and Continuation Passing
  (https://jtauber.com/blog/2008/03/30/thunks,_trampolines_and_continuation_passing/)
- Tail Recursion Elimination
  (http://neopythonic.blogspot.com/2009/04/tail-recursion-elimination.html)
- Final Words on Tail Calls
  (http://neopythonic.blogspot.com/2009/04/final-words-on-tail-calls.html)
- Python is the Haskell You Never Knew You Had: Tail Call Optimization
  (https://sagnibak.github.io/blog/python-is-haskell-tail-recursion/)

## How-to Contribute

You are very welcome to contribute with suggestions or PRs :heart_eyes: It is
nice if you can try to align the code and naming with F# modules, functions,
and documentation if possible. But submit a PR even if you should feel unsure.

Code, doc-strings, and comments should also follow the [Google Python Style
Guide](https://google.github.io/styleguide/pyguide.html).

Code checks are done using
- [Black](https://github.com/psf/black)
- [flake8](https://github.com/PyCQA/flake8)
- [isort](https://github.com/PyCQA/isort)

To run code checks on changed files every time you commit, install the pre-commit hooks by running:
```
pre-commit install
```

## Code of Conduct

This project follows https://www.contributor-covenant.org, see our [Code
of
Conduct](https://github.com/cognitedata/Expression/blob/main/CODE_OF_CONDUCT.md).

## License

MIT, see [LICENSE](https://github.com/cognitedata/Expression/blob/main/LICENSE).