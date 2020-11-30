# λ Calculus

Lambda calculus was introduced by mathematician Alonzo Church in the 1930s as part of an investigation into the foundations of mathematics

- Lambda calculus is a formal language
- The expressions of the language are called lambda terms
- Everything is a function, there are no literals

In lambda calculus, we write `(f x)` instead of the more traditional `f(x)`.

Many real-world programming languages can be regarded as extensions of the lambda calculus. This is true for all functional programming languages, a class that includes Lisp, Scheme, Haskell, and ML (OCaml, F#).


## Lambda calculus in Python

```python
identity = lambda x: x

zero = lambda f: identity
one = lambda f: lambda x: f(x)
two = lambda f: lambda x: f(f(x))
three = lambda f: lambda x: f(f(f(x)))
```

```python
# Don't repeat yourself (DRY)
succ = lambda numeral: lambda f: lambda x: f(numeral(f)(x))
two = succ(one)
three = succ(two)

three(lambda x: x+1)(0)
```

# Tools of lambda calculus

Substitution rules of programming

- **α-conversion:** changing bound variables (alpha);
- **β-reduction:** applying functions to their arguments (beta);
- **η-conversion:** which captures a notion of extensionality (eta).


## Alpha Conversion

Alpha-conversion is about renaming of bound variables

```python
(lambda x: x)(42) == (lambda y: y)(42) # Renaming
```

## Beta Reduction

A beta reduction (also written β reduction) is the process of calculating a result from the application of a function to an expression. 

((λn.n×2) 7) → 7×2.


```python
(lambda n: n*2)(7) == 7*2
```

## Eta-conversion

An eta conversion (also written η-conversion) is adding or dropping of an abstraction over a function. 

```python
# Eta-conversion
# λx.(f x) and f
f = lambda x: x

(lambda x: f(x)) == f
```

Extensive use of η-*reduction* can lead to what's called *point-free* programming. 

> Extensive use of point-free programming can lead to *point-less* programming.

```python
from functools import reduce

xs = reduce(lambda acc, x: max(acc, x), range(10))
print(xs)

xs = reduce(max, range(10))
print(xs)
```



## Do we need to know about lambda calculus?

You usually do not need to know about lambda calculus. But look out for point-free programming which may both simplify or over complicate your code. Lambda calculus is a must have knowledge when dealing with compilers and expression trees (ASTs).
