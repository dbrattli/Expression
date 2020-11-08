from typing import Any, Callable, Generic, Optional, Tuple, TypeVar, Union, cast, get_origin

A = TypeVar("A")
B = TypeVar("B")
TSource = TypeVar("TSource")
TResult = TypeVar("TResult")
Base = TypeVar("Base")
Derived = TypeVar("Derived")


def downcast(type: Base, expr: Derived) -> Base:
    """Downcast expression `Derived` to `Base`

    Checks at compile time that the type of expression E is a supertype
    of T, and checks at runtime that E is in fact an instance of T.

    Note: F# `:?>` or `downcast`.
    """
    assert isinstance(expr, type), f"The type of expression {expr} is not a supertype of {type}"
    return expr


def upcast(type: Derived, expr: Base) -> Derived:
    """Upcast expression `Base` to `Derived`.

    Check that the `Derived` type is a supertype of Base.

    Note: F# `:>` or `upcast`.
    """

    assert isinstance(expr, type), f"The expression {expr} is not derived from type {type}"
    return expr


def try_upcast(type_: Derived, expr: Base) -> Optional[Derived]:
    """Upcast expression `Base` to `Derived`.

    Check that the `Derived` type is a supertype of `Base`.

    NOTE: Supports generic types.

    Returns:
        None if `Derived` is not a supertype of `Base`.
    """
    origin: Optional[Derived] = get_origin(type_) or type_
    if origin is not None and isinstance(expr, origin):
        derived = cast(type(type_), expr)
        return derived
    else:
        return None


def identity(value: A) -> A:
    """Identity function.

    Returns value given as argument.
    """
    return value


def starid(*value: Any) -> Tuple[Any, ...]:
    return value


def flip(fn: Callable[[A, B], Any]) -> Callable[[B, A], Any]:
    """Flips the arguments for a function taking two arguments.

    Example:
        >>> fn(a, b) == flip(fn)(b, a)
    """

    def _(b: B, a: A) -> Any:
        return fn(a, b)

    return _


class Thunk(Generic[TResult]):
    """Suspended computaton."""

    def __init__(self, name: Callable[..., TResult], *args: Any, **kw: Any):
        self.run = lambda: name(*args, **kw)

    def __call__(self) -> TResult:
        return self.run()


def trampoline(fn: Callable[..., TResult]) -> Callable[..., TResult]:
    """Thunk bouncing decorator."""

    def _trampoline(bouncer: Union[Thunk[TResult], Callable[..., TResult]]) -> TResult:
        while isinstance(bouncer, Thunk):
            bouncer = bouncer()
        return bouncer

    def _(*args: Any) -> TResult:
        return _trampoline(fn(*args))

    return _


__all__ = ["identity", "starid", "flip", "Thunk", "trampoline"]
