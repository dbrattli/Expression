# Containers

In Python a container is something that contains something. Containers may be sequences, sets or mappings. Thus a collection is an **abstraction** of **"something"** that:

- May contain **something**
- Sequences are iterable
- Collections have a size

We usually talk about generic container types such as `List[T]`, `Set[T]`, `Tuple[T, ...]`. But we can also imagine taking the abstraction to a higher-order making the left side generic as well, e.g `Something[T]`. What do types of `Something` have in common?

> *A something within a something*

A container is really just some kind of box that you can pull values out of. Can values be pushed out of a container?

## Mapping

A mapping object maps immutable values to arbitrary objects. There is both `Mapping` and `MutableMapping`. The most known mutable mapping is the `dict` type.

## Sequence

A sequence is an iterable container such as `List`, `Tuple`, `str`, ...

## Immutable data types

Immutable data types are important in functional programming. Immutable means that it's not possible to make any changes after the type have been created. Most data structures in Python are mutable such as `List` and `Dict`, but Python also have a few immutable data types:

* Strings
* Tuples
* Iterable

The advantages of immutable data types are:

* Thread-safe. Multiple threads cannot modify or corrupt the state.
* Safe to share and reuse
* Easy to reason about. Reduces the cognitive load
* Easier to debug

Expression extends Python with a couple of more immutable data types:

## FrozenList

A FrozenList is an immutable List type. The implementation is based on the already immutable tuple type but gives it a list feeling and lots of functions and methods to work with it.

```python
from expression.collections import FrozenList

xs = FrozenList.of_seq(range(10))
print(xs)

ys = xs.cons(10)
print(ys)

zs = xs.tail()
print(zs)
```

## Map

The Expression Map module is an immutable Dict type. The implementation is based on map type from F# and uses a balanced binary tree implementation.

```python
from expression.collections import Map

items = dict(a=10, b=20).items()
xs = Map.of_seq(items)
print(xs)

ys = xs.filter(lambda k, v: v>10)
print(ys)
```

## Functions are Containers

It might not be obvious at first, but functions can also be containers. This is because values might be stored in function closures. That means that a value might be visible in the scope of the function.

> A closure is a poor man's object. An object is a poor man's closure.

In functional programming we often use function arguments to store values instead of objects

```python
def hat(item):
    def pull():
        return item
    return pull

small_hat = lambda item: lambda pull: item
```

```python
pull = hat("rabbit")
pull()
```

## List out of lambda (LOL)

We can even create a fully functional list implementation using only functions:

```python
empty_list = None

def prepend(el, lst):
    return lambda selector: selector(el, lst)

def head(lst):
    return lst(lambda h, t: h)

def tail(lst):
    return lst(lambda h, t: t)

def is_empty(lst):
    return (lst == empty_list)
```

```python
a = prepend("a", prepend("b", empty_list))

assert("a" == head(a))
assert("b" == head(tail(a)))
assert(tail(tail(a))==empty_list)
assert(not is_empty(a))
assert(is_empty(empty_list))

print("all tests are green!")
```

## LOL (more compact)

A list can be created using only lambda functions:

```python
empty_list = None
prepend = lambda el, lst: lambda selector: selector(el, lst)
head = lambda lst: lst(lambda h, t: h)
tail = lambda lst: lst(lambda h, t: t)
is_empty = lambda lst: lst is empty_list
```

```python
a = prepend("a", prepend("b", empty_list))

assert("a" == head(a))
assert("b" == head(tail(a)))
assert(tail(tail(a))==empty_list)
assert(not is_empty(a))
assert(is_empty(empty_list))

print("all tests are green!")
```

## Pull vs Push

List, iterables, mappings, strings etc are what we call "pull" collections. This is because we are actively pulling the values out of the collection by calling the `next()` function on the Iterator.

```python
iterable = [1, 2, 3]
iterator = iter(iterable)  # get iterator

value = next(iterator)
print(value)

value = next(iterator)
print(value)

value = next(iterator)
print(value)

# value = next(iterator)
```

## Push Collections

A push collection is something that pushes values out of the collection. This can be seen as temporal (push) containers vs spatial (pull) collections. This collection is called an Observable and is the dual (or the opposite) of an Iterable.

An `Iterable` have getter for getting an `Iterator` (__iter__)
An `Obserable` have a setter for setting an `Observer` (subscribe)

An `Iterator` have a getter for getting the next value (__next__)
An `Observer` have a setter for setting the next value (on_next, or send)

Summarized:

* Iterable is a getter-getter function
* Observable is a setter-setter function

Let's try to implement an Observable using only functions:

```python
import sys

def observer(value):
    print(f"got value: {value}")

def infinite():
    def subscribe(obv):
        for x in range(1000):
            obv(x)

    return subscribe

def take(count):
    def obs(source):
        def subscribe(obv):
            n = count
            def observer(value):
                nonlocal n
                if n > 0:
                    obv(value)
                n -= 1

            source(observer)
        return subscribe
    return obs

take(10)(infinite())(observer)
```

```python
def pipe(arg, *fns):
    for fn in fns:
        arg = fn(arg)
    return arg


observable = pipe(
    infinite(),  # infinite sequence of values
    take(10)     # take the first 10
)

observable(observer)
```

[RxPY](https://github.com/ReactiveX/RxPY) is an implementation of `Observable` and [aioreactive](https://github.com/dbrattli/aioreactive) project is an implementation of `AsyncObservable`.
