from typing import NoReturn


class EffectError(Exception):
    """An error that will exit any computational expression.

    We use this to detect if sub-generators causes an exit, since
    yielding nothing will be silently ignored.
    """


def failwith(message: str) -> NoReturn:
    raise Exception(message)


__all__ = ["EffectError", "failwith"]
