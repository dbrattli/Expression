
# Functional Programming in Python

> Do you know Python and would like to learn more about functional programming? Are you wondering what the Scala, F#, and Haskell developers are talking about? Let's do some functional programming in a language that you already know!

This tutoral that will get you up to speed with functinal programming in Python using the [Expression](https://github.com/dbrattli/Expression) functional programming library.

## Functional Programming

Functional programming is about programming with functions, or *expressions*. An expression is a combination of functions and values that evaluates to a value.

Functional programming can sometimes be seen as difficult, scary or even intimidating. Talks about functional programming are often about Applicatives, Functors, and you might have heard about Category Theory or the infamous Monad. But you don't need to know about category theory and Monads to do functional programming.

Note that object-oriented programming can in the same way be just as scary with words such as Inheritance, Interfaces, Abstract Base Classes, Covariance, Contravariance and Liskovs substitution principle. 

Lets look at how some object oriented programming patterns maps to functional programming:

<img src="images/fppatterns.png" alt="Fp Patterns" style="zoom: 67%;" />

*(ref: https://fsharpforfunandprofit.com/fppatterns/)*

If there is one takeaway from reading this, it is that functional programming is about expressions (functions and values) that evaluates to a value. This is stuff you most likely already know, and it don't have to be more difficult than that.

## Python

Python is a multi-paradigm language:

- **Imperative**: `assert a == 10`
- **Object-oriented**: `class B: ...`
- **Procedural**: `print("test")`
- ... and **Functional**: `xs = map(lambda x: x*2, [1, 2, 3])`

So Python is not a functional first programming language, but it has some functional programming features that we will explore in this tutorial. 

## Functions

A function `f : A → B` takes some input `A` and produces some output `B`:

```python
def add(a, b):
    return a + b
```

```python
add(10, 20)
```

## Lambda functions

Using lambda we can create anonymous functions that we can assing to
variables:

```python
add = lambda a, b: a + b
```

```python
add(10, 20)
```

## Pure functions

Another aspect of functional programming is the concept of pure functions. A pure function is a function where the same input always gives the same output . Pure functions are  important for several reasons:

- Pure functions are deteministic
- Pure function can be unit-tested
- Pure functions are thread safe
- Pure functions can be memoized
- Pure functions lowers the cognitive load. I.e they can be reasoned about.
- Pure functions have no side-effects

We will explore this further when we talk about "Effects and Side-effects".

## Higher-Order Functions

A function that takes another function as an argument, or returns a
function as a result, is called a **higher-order** function. In order to
pass functions around, they need to be what’s called **first-class**. A
first-class function can be used the same way as any other Python value:

- Assign a function or a method to a variable or object property.
- Pass functions as arguments to other functions or methods.
- Return functions as the result from other functions.
- Create functions dynamically at runtime.


### Assign a function to a variable

```python
multiply = lambda a, b: a * b
```

```python
def add(a, b):
    return a + b

adding = add
```

### A function returning a function

```python
def add_n(n):
    def partial(x):
        return x+n
    return partial
```

```python
lambda n: lambda x: x+n
```

### A function that takes a function as an argument

```python
def square(x, multiply):
    return multiply(x, x)
```

### Create function dynamically at runtime

*WARNING: you should normally never use eval because of security risks related
to code injection*

```python
add_10 = eval("lambda x: x+10")
add_10(20)
```

## Currying

A function that takes two arguments is basically exactly the same as a function that takes one argument and returns a function that takes the second argument. 

Some languages like F# supports automatic currying of functions. Python does not support automatic currying of functions, but we can define functions that return functions.

Here is a function that takes two arguments:

```python
add = lambda a, b: a + b
add(10, 20)
```

We can write this function as a function that takes one argument and returns a
function that takes the second argument:

```python
add = lambda a: lambda b: a + b
add(10)(20)
```

<!-- #region -->

## Pipelining

Making pipelines of operations is well known from the Unix terminal and shell programming.

```bash
command_1 | command_2 | command_3 | .... | command_N 
```

F# uses the `|>` operator for piping. The definition of the pipe operator is suprisingly simple:

```fsharp
let (|>) x f = f x
```

The main idea of pipelining is simply to bring the argument to the left side of the function (instead of the right). The main reason for this is that we are teached to read from left to right. Thus the traditional way of nesting functions is not very easy to read:

```python
functools.reduce(lambda s, x: s + x, filter(lambda x: x > 100, map(lambda x: x * 10, xs)), 0)
```

Python do not have a pipe operators and overloading existing operators e.g `|` is not recommended. Expression provides a [pipe](https://github.com/dbrattli/Expression/blob/main/expression/core/pipe.py) function that we can use instead:

```python
pipe(
    xs,
    seq.map(lambda x: x * 10),
    seq.filter(lambda x: x > 100),
    seq.fold(lambda s, x: s + x, 0),
)
```

The key thing to note is that for pipelining to work, then every function can only take a single argument. So how can we provide both e.g a mapper and an iterable for the `seq.map` function? The answer is to use currying or higher order functions. Remember that a function that takes two arguments is the same as a function that takes the first argument and returns a function that takes the second argument. Here is how the `map` function in the sequence module is defined:

```python
def map(mapper: Callable[[TSource], TResult]) -> Callable[[Iterable[TSource]], Iterable[TResult]]:
    def _map(source: Iterable[TSource]) -> Iterable[TResult]:
        return (mapper(x) for x in source)

    return _map
```

This allows us to do partial application of functions and have the last function take a single argument. The `pipe` operator in Expression is defined as follows:

```python
def pipe(value: Any, *fns: Callable[[Any], Any]) -> Any:
    """Functional pipe (`|>`)

    Allows the use of function argument on the left side of the function.

    Example:
        >>> pipe(x, fn) == fn(x)  # Same as x |> fn
        >>> pipe(x, fn, gn) == gn(fn(x))  # Same as x |> fn |> gn
        ...
    """

    return compose(*fns)(value)
```

We see that piping is a one-liner that uses a composition operator. Let's look more into function composition.

## Composition

In programming we are building programs by combining smaller pieces of code into larger ones. This is very similar to building with lego bricks. Combining many small lego bricks into larger constructions, is more flexible than having a few fixed large
size pieces to start with.

> *Composition is the essence of programming - Bartosz Milewski*

```fsharp
// F#
let compose (f: 'a -> 'b) (g: 'b -> 'c) : 'a -> 'c =
    f >> g
```

```python
# Python
let compose(f: Callable[[A], B], g: Callable[[B], C]) -> Callable[[A], C]:
    lambda x: g(f(x))
```
<!-- #endregion -->

```python
def f(x):
    return x+1

def g(x):
    return x*2

# Procedural / imperative composition. The function `h` becomes hard-coded to `f` ang `g`
def h(x):
    y = f(x)
    z = g(y)
    return z
h(42)
```

```python
# Functional compose. Inject all dependencies.
def compose(f, g):
    return lambda x: g(f(x))

h = compose(f, g)
h(42)
```

## Functional Composition is Associative

```python
def test(x):
    f = lambda x: x + 1
    g = lambda x: x * 2
    h = lambda x: x - 10

    right = compose(f, compose(g, h))
    left = compose(compose(f, g), h)

    assert right(x) == left(x)
    
test(10)
```

The `compose` operator in Expression is defined as follows:

```py
def compose(*fns: Callable[[Any], Any]) -> Callable[[Any], Any]:
    """Compose multiple functions left to right."""

    def _compose(source: Any) -> Any:
        return reduce(lambda acc, f: f(acc), fns, source)

    return _compose
```

It is basically iteration of the functions keeping an accumulator with the currently composed functions.

## Believe the Type

Python is a strongly typed dynamic programming language. This means that the type of a variable is only checked at runtime. Other languages such as F#, Scala, Haskell to type checking at compile time.

```python
def run():
    return "abc" + 10
```

```python
run()
```

<!-- #region -->
But there are a several static type checkers for Python that we can use:

* **Mypy:** https://github.com/python/mypy
* **Pyre-check:** https://github.com/facebook/pyre-check
* **Pylance:** https://github.com/microsoft/pylance-release

Static type checkers can significantly improve the quality of the code. The problem with Python is that the type checkers have not been able to really say if your code is correct or not. So you really don't know if it's the code or the type checker that is right (or wrong).

## Industrial Strength Code

With Expression we are aiming for industral strength code. What is industrial strength?

> Marked by more than usual power, durability, or intensity 

The difference with "more than usual" and "usual" can be subtle, but even a subtle difference can have a significant effect when you start deploing to 100.000 servers (e.g Exchange, Facebook, etc) instead of a single server. You need to plan for more than being lucky.

- Use simple well tested abstractions. Don't reinvent the wheel.
- Use immutable data types whenever possible.
- Use pure functions. Avoid None-taking/returning methods or functions
- Use a static type checker like Pylance (in strict mode)
- Use unit-testing and property-based testing for core logic. E.g a library like Hypotheses
- Use single threaded code to avoid Heisenbugs

Cost of failure increases exponentially the further the bug 

- Type checks (instant)
- Unit tests (seconds)
- Integration tests (minutes and hours)
- Test deployment (hours and days)
- Production deployment (days and months)
- Dedicated deployment on-prem at customer location (💸)

<img src="images/art-of-bugfixing.png" alt="art of bugfixing" style="zoom:150%;" />

*"A Heisenbug is a classification of an unusual software bug that disappears or alters its behavior when an attempt to isolate it is made. Due to the unpredictable nature of a Heisenbug, when trying to recreate the bug or using a debugger, the error may change or even vanish on a retry."*

<!-- #endregion -->

```python

```
