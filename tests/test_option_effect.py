from typing import TypeVar

from expression import Nothing, Some, effect

T = TypeVar("T", float, int)


def test_option_builder_projection_int_str():
    @effect.option
    def fn():
        z: str = "Not found"
        for x in Some(42.0):
            for y in Some(int(x)):
                z = yield from Some(str(y))

        return z

    for x in fn():
        assert x == "42"
        break
    else:
        assert False


def test_option_builder_yield_from_nothing():
    @effect.option
    def fn():
        x = yield from Nothing  # or a function returning Nothing

        # -- The rest of the function will never be executed --
        y = yield from Some(43)

        return x + y

    xs = fn()
    assert xs is Nothing
