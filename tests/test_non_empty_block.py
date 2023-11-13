import pytest
from pydantic.error_wrappers import ValidationError
from pydantic.main import BaseModel

from expression import Nothing, Some
from expression.collections import NonEmptyBlock, Block, non_empty_block

_test_value: NonEmptyBlock[int] = NonEmptyBlock(1, (2, 3, 4))


def test_non_empty_block_append():
    other = [9, 10, 11]
    expected = NonEmptyBlock(1, [2, 3, 4, 9, 10, 11])
    assert _test_value.append(other) == expected
    assert _test_value.pipe(non_empty_block.append(other)) == expected


def test_non_empty_block_choose():
    expected = Block([3, 4])
    assert _test_value.choose(lambda i: Some(i) if i >= 3 else Nothing) == expected
    assert _test_value.pipe(non_empty_block.choose(lambda i: Some(i) if i >= 3 else Nothing)) == expected


def test_non_empty_block_choose_no_matches():
    assert _test_value.choose(lambda i: Nothing) == Block()
    assert _test_value.pipe(non_empty_block.choose(lambda i: Nothing)) == Block()


def test_non_empty_block_collect():
    expected = NonEmptyBlock(1, (1, 10, 2, 2, 20, 3, 3, 30, 4, 4, 40))
    assert _test_value.collect(lambda i: NonEmptyBlock(i, (i, i * 10))) == expected
    assert _test_value.pipe(non_empty_block.collect(lambda i: NonEmptyBlock(i, (i, i * 10)))) == expected


def test_non_empty_block_cons():
    expected = NonEmptyBlock(-99, [1, 2, 3, 4])
    assert _test_value.cons(-99) == expected
    assert _test_value.pipe(non_empty_block.cons(-99)) == expected


def test_non_empty_block_filter():
    expected = Block([1, 2])
    assert _test_value.filter(lambda i: i < 3) == expected
    assert _test_value.pipe(non_empty_block.filter(lambda i: i < 3)) == expected


def test_non_empty_block_fold():
    initial_state = ''
    expected = '1234'
    assert _test_value.fold(lambda state, source: state + str(source), state=initial_state) == expected
    assert _test_value.pipe(non_empty_block.fold(lambda state, source: state + str(source), state=initial_state)) == expected


def test_non_empty_block_forall_true():
    assert _test_value.forall(lambda i: i < 100)
    assert _test_value.pipe(non_empty_block.forall(lambda i: i < 100))


def test_non_empty_block_forall_false():
    assert not _test_value.forall(lambda i: i < 4)
    assert not _test_value.pipe(non_empty_block.forall(lambda i: i < 4))


def test_non_empty_block_head():
    assert _test_value.head() == 1
    assert _test_value.pipe(non_empty_block.head) == 1


def test_non_empty_block_indexed():
    expected = NonEmptyBlock((0, 1), ((1, 2), (2, 3), (3, 4)))
    assert _test_value.indexed() == expected
    assert _test_value.pipe(non_empty_block.indexed) == expected


def test_non_empty_block_item_first_item():
    expected = Some(1)
    assert _test_value.item(0) == expected
    assert _test_value.pipe(non_empty_block.item(0)) == expected


def test_non_empty_block_item_last_item():
    expected = Some(4)
    assert _test_value.item(3) == expected
    assert _test_value.pipe(non_empty_block.item(3)) == expected


def test_non_empty_block_item_out_of_range():
    assert _test_value.item(99) is Nothing
    assert _test_value.pipe(non_empty_block.item(99)) is Nothing


def test_non_empty_block_map():
    expected = NonEmptyBlock('X 1 X', ('X 2 X', 'X 3 X', 'X 4 X'))
    assert _test_value.map(lambda i: f'X {i} X') == expected
    assert _test_value.pipe(non_empty_block.map(lambda i: f'X {i} X')) == expected


def test_non_empty_block_starmap():
    mapped_value = _test_value.map(lambda i: (i, i * 10, i * 100))
    expected = NonEmptyBlock('1 10 100', ('2 20 200', '3 30 300', '4 40 400'))
    assert mapped_value.starmap(lambda a, b, c: f'{a} {b} {c}') == expected
    assert mapped_value.pipe(non_empty_block.starmap(lambda a, b, c: f'{a} {b} {c}')) == expected


# TODO: Not sure how to make this pass pyright
#       Gives the following type of error:
#         Type parameter "_TSource@NonEmptyBlock" is invariant, but "int" is not the same as
#         "_TSourceSum@sum | Literal[0]"
#def test_non_empty_block_sum():
#    assert _test_value.sum() == 10
#    assert _test_value.pipe(non_empty_block.sum) == 10
#
#
#def test_non_empty_block_sum_by():
#    assert _test_value.sum_by(lambda i: i * 10) == 100
#    assert _test_value.pipe(non_empty_block.sum_by(lambda i: i * 10)) == 100


def test_non_empty_block_mapi():
    expected = NonEmptyBlock('0: 1', ('1: 2', '2: 3', '3: 4'))
    assert _test_value.mapi(lambda index, value: f'{index}: {value}') == expected
    assert _test_value.pipe(non_empty_block.mapi(lambda index, value: f'{index}: {value}')) == expected


def test_non_empty_block_of():
    assert non_empty_block.of(1, 2, 3, 4) == _test_value
    assert NonEmptyBlock.of(1, 2, 3, 4) == _test_value
    assert non_empty_block.of(1, 2, 3, 4) == _test_value


def test_non_empty_block_of_seq():
    test_block = Block([1, 2, 3, 4])
    assert NonEmptyBlock.of_seq(test_block) == Some(_test_value)
    assert test_block.pipe(non_empty_block.of_seq) == Some(_test_value)


def test_non_empty_block_of_seq_empty():
    test_block = Block()
    assert NonEmptyBlock.of_seq(test_block) is Nothing
    assert test_block.pipe(non_empty_block.of_seq) is Nothing


def test_non_empty_block_of_init_last():
    assert NonEmptyBlock.of_init_last([1, 2, 3], 4) == NonEmptyBlock(1, (2, 3, 4))


def test_non_empty_block_of_init_last_empty_iterable():
    assert NonEmptyBlock.of_init_last([], 4) == NonEmptyBlock(4)


def test_non_empty_block_partition():
    expected = (Block([2, 4]), Block([1, 3]))
    assert _test_value.partition(lambda i: i % 2 == 0) == expected
    assert _test_value.pipe(non_empty_block.partition(lambda i: i % 2 == 0)) == expected


def test_non_empty_block_range_stop():
    expected = Some(NonEmptyBlock(0, (1, 2)))
    assert NonEmptyBlock.range(3) == expected
    assert non_empty_block.range(3) == expected


def test_non_empty_block_range_start_stop_step():
    expected = Some(NonEmptyBlock(1, (3, 5)))
    assert NonEmptyBlock.range(1, 6, 2) == expected
    assert non_empty_block.range(1, 6, 2) == expected


def test_non_empty_block_range_start_and_stop_the_same():
    assert NonEmptyBlock.range(1, 1) is Nothing
    assert non_empty_block.range(1, 1) is Nothing


def test_non_empty_block_reduce():
    assert _test_value.reduce(lambda a, b: a + b) == 10
    assert _test_value.pipe(non_empty_block.reduce(lambda a, b: a + b)) == 10


def test_non_empty_block_singleton():
    assert NonEmptyBlock.singleton(1) == NonEmptyBlock(1)
    assert non_empty_block.singleton(1) == NonEmptyBlock(1)


def test_non_empty_block_skip_head():
    expected = Some(NonEmptyBlock(2, (3, 4)))
    assert _test_value.skip(1) == expected
    assert _test_value.pipe(non_empty_block.skip(1)) == expected


def test_non_empty_block_skip_all_but_last():
    expected = Some(NonEmptyBlock(4))
    assert _test_value.skip(3) == expected
    assert _test_value.pipe(non_empty_block.skip(3)) == expected


def test_non_empty_block_skip_all():
    assert _test_value.skip(4) is Nothing
    assert _test_value.pipe(non_empty_block.skip(4)) is Nothing


def test_non_empty_block_skip_last_element():
    expected = Some(NonEmptyBlock(1, (2, 3)))
    assert _test_value.skip_last(1) == expected
    assert _test_value.pipe(non_empty_block.skip_last(1)) == expected


def test_non_empty_block_skip_last_all_but_head():
    expected = Some(NonEmptyBlock(1))
    assert _test_value.skip_last(3) == expected
    assert _test_value.pipe(non_empty_block.skip_last(3)) == expected


def test_non_empty_block_skip_last_all():
    assert _test_value.skip_last(4) is Nothing
    assert _test_value.pipe(non_empty_block.skip_last(4)) is Nothing


def test_non_empty_block_tail():
    expected = Block((2, 3, 4))
    assert _test_value.tail() == expected
    assert _test_value.pipe(non_empty_block.tail) == expected


def test_non_empty_block_sort():
    block = NonEmptyBlock(2, (4, 3, 1))
    assert block.sort() == _test_value
    assert block.pipe(non_empty_block.sort()) == _test_value


def test_non_empty_block_sort_reverse():
    block = NonEmptyBlock(2, (4, 3, 1))
    expected = NonEmptyBlock(4, (3, 2, 1))
    assert block.sort(reverse=True) == expected
    assert block.pipe(non_empty_block.sort(reverse=True)) == expected


def test_non_empty_block_sort_with():
    expected = NonEmptyBlock(3, (1, 4, 2))
    assert _test_value.sort_with(lambda i: i % 3) == expected
    assert _test_value.pipe(non_empty_block.sort_with(lambda i: i % 3)) == expected


def test_non_empty_block_sort_with_reverse():
    expected = NonEmptyBlock(2, (1, 4, 3))
    assert _test_value.sort_with(lambda i: i % 3, reverse=True) == expected
    assert _test_value.pipe(non_empty_block.sort_with(lambda i: i % 3, reverse=True)) == expected


def test_non_empty_block_take():
    expected = NonEmptyBlock(1, (2,))
    assert _test_value.take(2) == expected
    assert _test_value.pipe(non_empty_block.take(2)) == expected


def test_non_empty_block_take_more_than_block_size():
    assert _test_value.take(10) == _test_value
    assert _test_value.pipe(non_empty_block.take(10)) == _test_value


def test_non_empty_block_take_last():
    expected = NonEmptyBlock(3, (4,))
    assert _test_value.pipe(non_empty_block.take_last(2)) == expected


def test_non_empty_block_take_last_more_than_block_size():
    assert _test_value.take_last(10) == _test_value
    assert _test_value.pipe(non_empty_block.take_last(10)) == _test_value


def test_non_empty_block_dict():
    expected = [1, 2, 3, 4]
    assert _test_value.dict() == expected
    assert _test_value.pipe(non_empty_block.dict) == expected


def test_non_empty_block_zip():
    expected = NonEmptyBlock((1, 10), ((2, 11), (3, 12), (4, 13)))
    other = NonEmptyBlock(10, (11, 12, 13))
    assert _test_value.zip(other) == expected
    assert _test_value.pipe(non_empty_block.zip(other)) == expected


def test_non_empty_block_add():
    assert _test_value + _test_value == NonEmptyBlock(1, (2, 3, 4, 1, 2, 3, 4))


def test_non_empty_block_contains():
    assert 4 in _test_value


def test_non_empty_block_contains_not():
    assert 5 not in _test_value


def test_non_empty_block_concat():
    assert non_empty_block.concat(
        NonEmptyBlock.of(_test_value, _test_value, _test_value)
    ) == NonEmptyBlock(1, (2, 3, 4, 1, 2, 3, 4, 1, 2, 3, 4))


class _Wrapper(BaseModel):
    non_empty_block: NonEmptyBlock[int]


def test_non_empty_block_validate_non_empty_block_value():
    wrapper = _Wrapper(non_empty_block=_test_value)
    assert wrapper.non_empty_block == _test_value


def test_non_empty_block_validate_not_a_list_value():
    with pytest.raises(ValidationError):
        _Wrapper.parse_obj({'non_empty_block': 'not-a-list'})


def test_non_empty_block_validate_list_value():
    wrapper = _Wrapper.parse_obj({'non_empty_block':[1, 2, 3, 4]})
    assert wrapper.non_empty_block == _test_value


def test_non_empty_block_validate_empty_list_value():
    with pytest.raises(ValidationError):
        _Wrapper.parse_obj({'non_empty_block':[]})
