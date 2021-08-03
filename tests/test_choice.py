from expression import Choice, Choice1of2, Choice2, Choice2of2, match


def test_choice_choice1of2():
    xs: Choice2[int, str] = Choice1of2(42)

    assert isinstance(xs, Choice)
    assert isinstance(xs, Choice2)

    with match(xs) as case:
        for x in Choice1of2.match(case):
            assert x == 42
            break
        else:
            assert False


def test_choice_choice2of2():
    xs: Choice2[int, str] = Choice2of2("test")

    assert isinstance(xs, Choice)
    assert isinstance(xs, Choice2)

    with match(xs) as case:
        for x in Choice2of2.match(case):
            assert x == "test"
            break
        else:
            assert False
