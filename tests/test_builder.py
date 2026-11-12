"""Contracts for the eager generator interpreter, independent of built-in effects."""

from collections.abc import Callable
from typing import NoReturn

import pytest

from expression.core import Builder


class IdentityBuilder(Builder[int, int]):
    def bind(self, xs: int, fn: Callable[[int], int]) -> int:
        return fn(xs)

    def return_(self, x: int) -> int:
        return x

    def return_from(self, xs: int) -> int:
        return xs

    def combine(self, xs: int, ys: int) -> int:
        return ys

    def zero(self) -> int:
        return 0


@pytest.mark.parametrize("hook", ["bind", "return_", "return_from", "combine", "delay", "run", "zero"])
def test_hook_stop_iteration_propagates(hook: str):
    from expression.core import EffectError

    builder = IdentityBuilder()
    error = StopIteration("hook failure")

    def fail(*args: object) -> NoReturn:
        raise error

    setattr(builder, hook, fail)

    @builder
    def computation():
        if hook == "zero":
            return
        if hook == "return_from":
            raise EffectError(1)
        yield 1
        yield 2

    with pytest.raises(StopIteration) as raised:
        computation()
    assert raised.value is error


@pytest.mark.parametrize("mode", ["skip", "twice", "raise"])
def test_invalid_bind_closes_generator(mode: str):
    closed: list[bool] = []
    resumed: list[int] = []

    class InvalidBuilder(IdentityBuilder):
        def bind(self, xs: int, fn: Callable[[int], int]) -> int:
            if mode == "skip":
                return xs
            if mode == "raise":
                raise RuntimeError("hook failure")
            fn(xs)
            return fn(xs)

    @InvalidBuilder()
    def computation():
        try:
            yield 1
            resumed.append(1)
            yield 2
            resumed.append(2)
        finally:
            closed.append(True)

    with pytest.raises(RuntimeError):
        computation()
    assert closed == [True]
    assert resumed == ([1] if mode == "twice" else [])


def test_retained_continuation_cannot_resume_later_iteration():
    callbacks: list[Callable[[int], int]] = []

    class RetainingBuilder(IdentityBuilder):
        def bind(self, xs: int, fn: Callable[[int], int]) -> int:
            callbacks.append(fn)
            if len(callbacks) == 2:
                callbacks[0](xs)
            return fn(xs)

    @RetainingBuilder()
    def computation():
        yield 1
        yield 2
        return 3

    with pytest.raises(RuntimeError, match="single-use"):
        computation()
    with pytest.raises(RuntimeError, match="single-use"):
        callbacks[-1](4)


def test_generator_runtime_error_is_not_completion():
    @IdentityBuilder()
    def computation():
        yield 1
        raise StopIteration("body bug")

    with pytest.raises(RuntimeError, match="generator raised StopIteration"):
        computation()


def test_many_steps_remain_stack_safe():
    @IdentityBuilder()
    def computation():
        for value in range(20_000):  # noqa: UP028 - exercise individual send/yield steps
            yield value
        return 42

    assert computation() == 42


def test_zero_only_needed_for_empty_computation():
    class NonemptyBuilder(IdentityBuilder):
        def zero(self):
            raise AssertionError("zero is not a seed")

    @NonemptyBuilder()
    def computation():
        yield 1
        return 2

    assert computation() == 2
