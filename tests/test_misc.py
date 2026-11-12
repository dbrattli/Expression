from typing import assert_type

from expression.core.misc import flip, fst, snd


def test_flip_preserves_argument_and_result_types():
    def repeat(text: str, count: int) -> str:
        return text * count

    flipped = flip(repeat)
    assert assert_type(flipped(3, "ab"), str) == "ababab"


def test_fst_preserves_selected_type():
    pair: tuple[int, str] = (42, "answer")
    assert assert_type(fst(pair), int) == 42


def test_snd_preserves_selected_type():
    pair: tuple[int, str] = (42, "answer")
    assert assert_type(snd(pair), str) == "answer"
