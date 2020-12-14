from typing import Any, NoReturn


class EffectError(Exception):
    """An error that will exit any computational expression.

    We use this to detect if sub-generators causes an exit, since
    yielding nothing will be silently ignored.
    """


class MatchFailureError(Exception):
    """Pattern match failure error."""

    def __init__(self, expr: Any):
        msg = f"Incomplete pattern matches on this expression. {expr} did not match any cases."
        super().__init__(msg)


def failwith(message: str) -> NoReturn:
    """Raise exception with the given message string."""
    raise Exception(message)


__all__ = ["EffectError", "failwith", "MatchFailureError"]
