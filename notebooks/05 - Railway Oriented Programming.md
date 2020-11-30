# Railway Oriented Programming (ROP)

- We don't really want to raise exceptions since it makes the code bloated with error checking
- It's also easy to forget to handle exceptions
- Dependencies might even change the kind of exceptions they throw
- Let's model errors using types instead

```python
class Result:
    pass
```

```python
class Ok(Result):
    def __init__(self, value):
        self._value = value
    
    def __str__(self):
        return "Ok: %s" % str(self._value)

class Error(Result):
    def __init__(self, exn):
        self._exn = exn
    
    def __str__(self):
        return "Error: %s" % str(self._exn)
```

```python
def fetch(url):
    try:
        if not "http://" in url:
            raise Exception("Error: unable to fetch from: '%s'" % url)
            
        value = url.replace("http://", "")
        return Ok(value)
    except Exception as exn:
        return Error(exn)
```

```python
result = fetch("http://42")
print(result)
```

```python
def parse(string):
    try:
        value = float(string)
        return Ok(value)
    except Exception as exn:
        return Error(exn)
```

```python
result = parse("42")
print(result)
```

# Composition 

How should we compose Result returning functions? How can we make a `fetch_parse` from `fetch` and `parse`. 

Cannot use functional composition since signatures don't match.

```py
def compose(fn: Callable[[A], Result[B, TError]], gn: Callable[[B], Result[C, TError]]) -> Callable[[A], Result[C, TError]]:
    fun x -> ???
```

First we can try to solve this with an "imperative" implementation using type-checks and `if-else` statements:

```python
def fetch_parse(url):
    b = fetch(url)
    if isinstance(b, Ok):
        val_b = b._value # <--- Don't look inside the box!!!
        return parse(val_b)            
    else: # Must be error
        return b

result = fetch_parse("http://42")
print(result)
```

This works, but the code is not easy to read. We have also hard-coded the logic to it's not possible to easily reuse without copy/paste. Here is a nice example on how to solve this by mixing object-oriented code with functional thinking:

```python
class Ok(Result):
    def __init__(self, value):
        self._value = value

    def bind(self, fn):
        return fn(self._value)

    def __str__(self):
        return "Ok: %s" % str(self._value)

class Error(Result):
    def __init__(self, exn):
        self._exn = exn
        
    def bind(self, fn):
        return self
    
    def __str__(self):
        return "Error: %s" % str(self._exn)
    
def bind(fn, result):
    """We don't want method chaining in Python."""
    return result.bind(fn)
```

```python
result = bind(parse, fetch("http://42"))
print(result)
```

```python
def compose(f, g):
    return lambda x: f(x).bind(g)
```

```python
fetch_parse = compose(fetch, parse)
result = fetch_parse("http://123.0")
print(result)
```

```python
result = fetch("http://invalid").bind(parse)
print(result)
```

### But what if we wanted to call fetch 10 times in a row?

This is what's called the "Pyramide of Doom":

```python
result = bind(parse, 
          bind(lambda x: fetch("http://%s" % x),
           bind(lambda x: fetch("http://%s" % x),
            bind(lambda x: fetch("http://%s" % x),
             bind(lambda x: fetch("http://%s" % x),
              bind(lambda x: fetch("http://%s" % x),
               bind(lambda x: fetch("http://%s" % x),
                fetch("http://123")
               )
              )
             )
            )
           )
          )
         )
print(result)
```

## Can we make a general compose?

Let's try to make a general compose function that composes two result returning functions:

```python
def compose(f, g):
    return lambda x: f(x).bind(g)

fetch_parse = compose(fetch, parse)
result = fetch_parse("http://42")
print(result)
```

## Kleisli composition

Functional compose of functions that returns wrapped values is called Kleisli composition. Using a reducer we can compose any number of functions:

```python
from functools import reduce

def kleisli(*fns):
    return reduce(lambda res, fn: lambda x: res(x).bind(fn), fns)
```

Now, make `fetch_and_parse` using kleisli:

```python
fetch_and_parse = kleisli(fetch, parse)
result = fetch_and_parse("http://123")
print(result)
```

### What if we wanted to call fetch 10 times in a row?

```python
fetch_with_value = lambda x: fetch("http://%s" % x)

request = kleisli(
            fetch,
            fetch_with_value,
            fetch_with_value,
            fetch_with_value,
            fetch_with_value,
            fetch_with_value,
            fetch_with_value,
            parse
          )

result = request("http://123")
print(result)
```
