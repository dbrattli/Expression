# %% [markdown]
"""
# Getting started

Expression works with Python 3.10 and later. Install it from PyPI:

```console
python -m pip install expression
```

Install the optional Pydantic integration when an application needs it:

```console
python -m pip install "expression[pydantic]"
```

## Your first workflow

`pipe` passes a value through functions from top to bottom. This is especially helpful
when a transformation has several named steps.
"""
# %%
from expression import pipe
from expression.collections import seq

scores = [4, 7, 12, 15]

total = pipe(
    scores,
    seq.filter(lambda score: score >= 10),
    seq.map(lambda score: score * 2),
    seq.sum,
)

assert total == 54

# %% [markdown]
"""
The equivalent fluent form is useful for short transformations:
"""
# %%
from expression.collections import Seq

total = Seq.of(4, 7, 12, 15).filter(lambda score: score >= 10).map(lambda score: score * 2).sum()
assert total == 54

# %% [markdown]
"""
Both styles use ordinary Python functions, type hints, and values. Choose the style that
your team finds easiest to read; the functional form is often easier to extend one step
per line.

## Where to go next

- Learn [how to choose an Expression type](choosing-a-type).
- Build readable transformations with [pipelines](pipelines).
- Handle a missing value with [Option](optional-values).
- Model an expected failure with [Result](error-handling).
"""
