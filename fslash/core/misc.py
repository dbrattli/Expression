from typing import TypeVar, Tuple, Any

A = TypeVar("A")


def identity(value: A) -> A:
    return value


def starid(*value: Any) -> Tuple:
    return value


__all__ = ["identity", "starid"]
