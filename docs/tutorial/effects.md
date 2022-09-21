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
(tutorial_effects)=

# Effects and Side-effects

What are effects? What are side-effects?


## Referential Transparency

Is the result of an expression the same every time you evaluate it? Can you substitute an expression with the value? In functional programming the answer is always yes!

What about Python?

```python
z = [42]

def expr(a):
    #return a + 1

    a += int(input())
    return a
    #print(a)
    #z[0] += a
    #return z[0]
```

Are these programs the same?

```python
a = expr(42)
a, a
```

```python
expr(42), expr(42)
```

We need to be very careful with non-pure functions. Always look out for code smell:

1. Functions or methods that takes no arguments, i.e `Callable[[None], Result]`
2. Functions or methods that returns nothing, i.e `Callable[..., None]`
3. Functions that takes nothing and returns nothing `Callable[[], None]`


## Side Effects

Functions that are not referenctial transparent

Look out for functions that either takes or returns `None`. They are not composable. What do these two functions do?

```python
def get() -> str:
    ...


def put(text: str) -> None:
    ...
```

How can we fix the problem? The solution is that the functions should take and return something to make them pure

```python
from typing import Generic, Tuple, TypeVar

TSource = TypeVar("TSource")

class Io(Generic[TSource]):
    def __init__(self, fn):
        self.__fn = fn  # a world changing function

    def rtn(a) -> "Io[TSource]":
        return Io(lambda world: (a, world + 1))

    def run(self, world: int=0) -> Tuple[TSource, int]:
        return self.__fn(world)

    def bind(self, fn: Callable[[TSource], "Io[TSource]"]) -> "Io[TSource]":
        def run(world):
            a, newWorld = self.run(world)
            return fn(a).run(newWorld)
        return Io(run)

    def __repr__(self):
        return "Io"
```

```python
from typing import Callable

def put(string) -> Io[str]:
    def side_effect(_):
        return Io.rtn(print(string))

    return Io.rtn(None).bind(side_effect)

def get(fn: Callable[[str], Io[str]]) -> Io[str]:
    def side_effect(_):
        return fn(input())
    return Io.rtn(None).bind(side_effect)
```

```python
io = put("Hello, what is your name?").bind(
    lambda _: get(
        lambda name: put("What is your age?").bind(
            lambda _: get(
                lambda age: put("Hello %s, your age is %d." % (name, int(age)))
            )
        )
    ))

(io, io)
```

Are they the same? We really don't know. We are not allowed to look inside the box. But we can run the effect:

```python
io.run(world=0)
```

## Effects

Effects are not the same as side-effects. Effects are just values with a context. The context is different for every effect.

* Option
* Result
* Block
* Observable
* Async
* AsyncObservable
* Io
* ...

## Effects in Expression

Expression have a nice way of dealing with effects and lets you safely work with wrapped values wihout having to error check:

```python
from expression import effect, Option, Some, Nothing


def divide(a: float, divisor: float) -> Option[float]:
    try:
        return Some(a / divisor)
    except ZeroDivisionError:
        return Nothing


@effect.option()
def comp(x: float):
    result: float = yield from divide(42, x)
    result += 32
    print(f"The result is {result}")
    return result


comp(42)
```

## Living on the edge ...

We have seen that we can create other wrapped worlds such as sequences, lists, results
and options. On the edge of such a world you will find other objects that we usually do
not want to work with:

* None,
* Exceptions
* Callbacks, continuations and `run`
* Iterators and `__iter__`
* Observers and `subscribe`

## Summary

- Effects are what we call *elevated* worlds
- An elevated world is a strange place where basically anything is possible.
- Two elevated worlds may e.g `Result`, `Option`, `Map` and `Io` may be completely
  different, but they still have the same basic structure.
- But still every normal value has a corresponding elevated value.
- Every function has a corresponding elevated function.

