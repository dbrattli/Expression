from typing import Generator, TypeVar

from expression import Some, effect

T = TypeVar("T", float, int)


def test_option_builder_projection_int_str():
    @effect.option
    def fn() -> Generator[str, str, str]:
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
