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
(tutorial_continuations)=

# Callbacks and Continuations

> Don't call me. I'll call you.

```python
import threading

def long_running(callback):
    def done():
        result = 42
        callback(result)
    timer = threading.Timer(5.0, done)
    timer.start()

long_running(print)
```

# Continuation Passing Style (CPS)

This is a functional programming style where you don’t return any values from your
functions. Instead of returning the result, you pass a continuation function that will
be applied to the result.

```python
import math

def add(a, b):
    return a + b

def square(x):
    return x * x

def sqrt(x):
    return math.sqrt(x)

def pythagoras(a, b):
    return sqrt(add(square(a), square(b)))
```

```python
result = pythagoras(2,3)
print(result)
```

```python
import math

def add(a, b, cont):
    cont(a + b)

def square(x, cont):
    cont(x * x)

def sqrt(x, cont):
    cont(math.sqrt(x))

# Pythagoras rewritten in CPS
def pythagoras(a, b, cont):
    square(a, (lambda aa:
        square(b, (lambda bb:
            add(aa, bb, (lambda aabb:
                sqrt(aabb, (lambda result:
                    cont(result)
                ))
            ))
        ))
    ))
```

```python
pythagoras(2, 3, print)
```

## Nice, but unreadable. Kind of ....

How can we do better? We're not really used to pass in continuations. We like to return our results!

> Could we perhaps use currying?

So instead of taking a continuation, we could return a function that takes a continuation. It's basically the exact same thing ... just moving the `:`.

```python
import math

def add(a, b):
    return lambda cont: cont(a + b)

def square(x):
    return lambda cont: cont(x * x)

def sqrt(x):
    return lambda cont: cont(math.sqrt(x))

def pythagoras(a, b):
    def then(cont):
        then = square(a)
        def next(aa):
            then = square(b)
            def next(bb):
                then = add(aa, bb)
                def next(aabb):
                    then = sqrt(aabb)
                    def next(result):
                        cont(result)
                    then(next)
                then(next)
            then(next)
        then(next)
    return then

result = pythagoras(2,3)
result(print)
```

# Now what? Looks slightly better, kind of ...

> Could we perhaps use types to make better abstractions?

In Python we create new types using classes, so let's create a class to encapsulte the CPS function `(a -> r) -> r`.

Ref: https://wiki.haskell.org/MonadCont_under_the_hood

```python
class Cont:
    def __init__(self, cps):
        self.__cps = cps # fn: ('a -> 'r) -> 'r

    @staticmethod
    def rtn(a):
        return Cont(lambda cont: cont(a))

    def run(self, cont):
        self.__cps(cont)

    def then(self, fn):
        # Cont <| fun c -> run cont (fun a -> run (fn a) c )
        return Cont(lambda c: self.run(lambda a: fn(a).run(c)))
```

```python
import math

def add(a, b):
    return Cont.rtn(a + b)

def square(x):
    return Cont.rtn(x * x)

def sqrt(x):
    return Cont.rtn(math.sqrt(x))

def pythagoras(a, b):
    return square(a).then(
        lambda aa: square(b).then(
            lambda bb: add(aa, bb).then(
                lambda aabb: sqrt(aabb)
            )
        )
    )
```

```python
result = pythagoras(2, 3)
result.run(print)
```

```python
import asyncio

class Cont:
    def __init__(self, cps):
        self.__cps = cps # fn: ('a -> 'r) -> 'r

    @staticmethod
    def rtn(a):
        return Cont(lambda cont: cont(a))

    def run(self, cont):
        self.__cps(cont)

    def __await__(self):
        loop = asyncio.get_event_loop()
        future = loop.create_future()
        def done(value):
            future.set_result(value)
        self.run(done)
        return iter(future)

    def then(self, fn):
        # Cont <| fun c -> run cont (fun a -> run (fn a) c )
        return Cont(lambda c: self.run(lambda a: (fn(a).run(c))))
```

```python
import math

def add(a, b):
    return Cont.rtn(a + b)

def square(x):
    return Cont.rtn(x * x)

def sqrt(x):
    return Cont.rtn(math.sqrt(x))

async def pythagoras(a, b):
    aa = await square(a)
    bb = await square(b)
    aabb = await add(aa, bb)
    ab = await sqrt(aabb)

    return ab

result = await pythagoras(2,3)
print(result)
```

# Conclusion

Async / await is basically just syntactic sugar for working with effects such as
callbacks and continuations

How do we know that the "normal" syntax of a programming language is not compiled to
continuations under the hood? Maybe we have been programming with continuations all
along?


# The Mother of all Monads

> https://www.schoolofhaskell.com/school/to-infinity-and-beyond/pick-of-the-week/the-mother-of-all-monads

```python
from typing_extensions import Protocol, runtime_checkable
from abc import abstractmethod

@runtime_checkable
class Monad(Protocol):
    @staticmethod
    @abstractmethod
    def rtn(a):
        raise NotImplementedError

    @abstractmethod
    def then(self, fn):
        raise NotImplementedError
```

```python
assert issubclass(Cont, Monad)
print("Yey!!")
```
