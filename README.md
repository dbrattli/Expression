# FSlash

![Python package](https://github.com/dbrattli/fslash/workflows/Python%20package/badge.svg)
![Upload Python Package](https://github.com/dbrattli/fslash/workflows/Upload%20Python%20Package/badge.svg)

> Python :heart: F#

FSlash aims to be a solid library for practical functional programming in
Python inspired by [F#](https://fsharp.org). By practical we mean that the goal
of the library if to enable you to do meaningful and productive functional
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

FSlash tries to make a better Python by providing several functional
features inspired by F# into Python. This serves two purposes:

- Make it easier for Python programmers to learn F# by starting out in a
  programming language they already know. Then get inspired to try out
  F# by itself.
- Make it easier for F# developers to use Python when needed, and re-use many
  of the concepts and abstractions that they already know and love.

FSlash will enable you to work with Python along with F# using many of
the same programming concepts and abstractions. This enables concepts
such as [Railway oriented
programming](https://fsharpforfunandprofit.com/rop/) (ROP) for better
and predictable error handling. Pipelining for workflows, computational
expressions, etc.

## Why

- I love F#, and know F# quite well. I'm the creator of projects such as
  [Oryx](https://github.com/cognitedata/oryx),
  [Fable.Reaction](https://github.com/dbrattli/Fable.Reaction) and
  [Feliz.ViewEngine](https://github.com/dbrattli/Feliz.ViewEngine)
- I love Python, and know Python really well. I'm the creator of both
  [RxPY](https://github.com/ReactiveX/RxPY) and
  [OSlash](https://github.com/dbrattli/OSlash), two functional style libraries
  for Python. So I already know that Python can do anything that F# can. The
  challenge is how to make it look nice (syntactic sugar).

For a long time I'm been wanting to make a "bridge" between these two worlds
and got inspired to write this library after watching "F# as a Better Python" -
Phillip Carter - NDC Oslo 2020 (https://www.youtube.com/watch?v=_QnbV6CAWXc).

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
  [pylance](https://devblogs.microsoft.com/python/announcing-pylance-fast-feature-rich-language-support-for-python-in-visual-studio-code/).

## Non Goals

- Provide all features of F# and .NET to Python, see [Supported Features](https://github.com/dbrattli/fslash#supported-features).

## Supported features

FSlash will never provide you with all the features of F# and .NET. We are
providing a few of the features we think are useful, and will add more on-demand as
we go along.

- Options - for optional stuff and better `None` handling.
- Result - for better error handling and enables railway-oriented programming in Python.
- Sequences - a better [itertools](https://docs.python.org/3/library/itertools.html)
- Computational Expressions:
  - option - an optional world for working with optional values
  - result - an error handling world for working with result values
- Pattern matching - provided by [Pampy](https://github.com/santinic/pampy).

## Resources

- F# (http://fsharp.org)
- Get Started with F# (https://aka.ms/fsharphome)
- F# as a Better Python - Phillip Carter - NDC Oslo 2020
  (https://www.youtube.com/watch?v=_QnbV6CAWXc)
- Pampy: Pattern Matching for Python (https://github.com/santinic/pampy)
- OSlash (https://github.com/dbrattli/OSlash)
- RxPY (https://github.com/ReactiveX/RxPY)

## License

MIT, see [LICENSE](https://github.com/dbrattli/FSlash/blob/master/LICENSE).