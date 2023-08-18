from expression import Choice, Choice1of2, Choice2, Choice2of2


def test_choice_choice1of2():
    xs: Choice2[int, str] = Choice1of2(42)

    assert isinstance(xs, Choice)
    assert isinstance(xs, Choice2)

    match xs:
        case Choice1of2(x):
            assert x == 42
        case _:  # type: ignore
            assert False


def test_choice_choice2of2():
    xs: Choice2[int, str] = Choice2of2("test")

    assert isinstance(xs, Choice)
    assert isinstance(xs, Choice2)

    match xs:
        case Choice2of2(x):
            assert x == "test"
        case _:  # type: ignore
            assert False
