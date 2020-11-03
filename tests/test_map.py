from typing import Callable, Container, Dict, Generator, ItemsView, Iterable, List, Optional, Tuple

import pytest
from expression import effect
from expression.collections import Map, map
from hypothesis import given
from hypothesis import strategies as st

from .utils import CustomException, throw


@given(st.dictionaries(keys=st.text(), values=st.integers()))
def test_map_create(xs: Dict[str, int]):
    items: ItemsView[str, int] = xs.items()
    m = Map.create(items)
    assert m.count() == len(xs)


@given(st.dictionaries(keys=st.text(), values=st.integers()))
def test_map_of_seq(xs: Dict[str, int]):
    items: ItemsView[str, int] = xs.items()
    m = map.of_seq(items)
    assert m.count() == len(xs)


@given(st.dictionaries(keys=st.text(), values=st.integers()))
def test_map_remove(xs: Dict[str, int]):
    items: ItemsView[str, int] = xs.items()
    m = Map.create(items)

    keys = xs.keys()
    count = m.count()
    for key in keys:
        m = m.remove(key)
        count -= 1
    assert m.count() == count == 0
