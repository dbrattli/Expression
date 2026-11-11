from __future__ import annotations

import string
from enum import Enum
from typing import Literal, TypeAlias, final

from expression import Error, Ok, Option, Some, TaggedUnion, case, pipe, tag
from expression.collections import Block
from expression.extra.parser import (
    Parser,
    and_then,
    any_of,
    choice,
    many,
    opt,
    pchar,
    pfloat,
    pint,
    pstring,
)


def test_parse_pchar():
    input = "ABC"
    parseA: Parser[str] = pchar("A")

    result = parseA(input)

    assert result.is_ok()
    match result:
        case Ok(a):
            assert a == "A"
        case _:
            assert False


def test_parse_pchar_fluent():
    input = "ABC"
    parseA: Parser[str] = Parser.pchar("A")

    result = parseA(input)

    assert result.is_ok()
    match result:
        case Ok(a):
            assert a == "A"
        case _:
            assert False


def test_parse_a_then_b():
    input = "ABC"
    parse_a: Parser[str] = pchar("A")
    parse_b: Parser[str] = pchar("B")

    parseAB = pipe(
        parse_a,
        and_then(parse_b),
    )

    result = parseAB(input)
    assert result.is_ok()
    match result:
        case Ok((a, b)):
            assert (a, b) == ("A", "B")
        case _:
            assert False


def test_parse_a_then_b_fluent():
    input = "ABC"
    parseAB = pchar("A").and_then(pchar("B"))

    result = parseAB(input)
    assert result.is_ok()
    match result:
        case Ok((a, b)):
            assert (a, b) == ("A", "B")
        case _:
            assert False


def test_pstring():
    parse_abc = pstring("ABC")

    ret = parse_abc("ABCDE")  # Success ("ABC", "DE")
    assert ret.is_ok()
    match ret:
        case Ok(success):
            assert success == "ABC"
        case _:
            assert False

    ret = parse_abc("A|CDE")  # Failure "Expecting 'B'. Got '|'"
    assert ret.is_error()
    match ret:
        case Error(error):
            assert error == "Expecting 'B'. Got '|'"
        case _:
            assert False

    ret = parse_abc("AB|DE")  # Failure "Expecting 'C'. Got '|'"
    assert ret.is_error()
    match ret:
        case Error(error):
            assert error == "Expecting 'C'. Got '|'"
        case _:
            assert False


def test_int():
    ret = pint("123C")

    match ret:
        case Ok(success):
            assert success == 123
        case _:
            assert False


def test_int_negative():
    ret = pint("-123C")

    match ret:
        case Ok(success):
            assert success == -123
        case _:
            assert False


def test_float():
    ret = pfloat("123C")

    match ret:
        case Ok(success):
            assert success == 123
        case _:
            assert False


def test_float_with_decimal():
    ret = pfloat("123.45C")

    match ret:
        case Ok(success):
            assert success == 123.45
        case _:
            assert False


def test_negative_float_with_decimal():
    ret = pfloat("-123.45C")

    match ret:
        case Ok(success):
            assert success == -123.45
        case _:
            assert False


class ComparisonOperator(Enum):
    EQ = "=="
    NOT_EQ = "!="
    LT = "<"
    LT_E = "<="
    GT = ">"
    GT_E = ">="
    IS = "is"
    IS_NOT = "is not"
    IN = "in"
    NOT_IN = "not in"


class BoolOp(Enum):
    AND = "and"
    OR = "or"


@final
@case
class Compare:
    left: Expression
    comparators: Block[Expression]
    ops: Block[ComparisonOperator]
    tag: Literal["compare"] = tag("compare")


@final
@case
class Name:
    name: str
    tag: Literal["name"] = tag("name")


@final
@case
class Constant:
    value: object
    tag: Literal["constant"] = tag("constant")


@final
@case
class Boolean:
    operator: BoolOp
    tag: Literal["boolean"] = tag("boolean")


Expression: TypeAlias = TaggedUnion[Name | Constant | Boolean | Compare]


def pname() -> Parser[Expression]:
    first = any_of(string.ascii_letters + "_")
    rest = pipe(
        any_of(string.ascii_letters + string.digits + "_"),
        many,
        opt,
    )

    def mapper(first: str, rest: Option[Block[str]]) -> Expression:
        match rest:
            case Some(letters):
                return Name(first + "".join(letters))
            case _:
                return Name(first)

    return first.and_then(rest).starmap(mapper)


def pexpr() -> Parser[Expression]:
    parsers = [
        pname(),
    ]
    return pipe(
        parsers,
        Block[Parser[Expression]].of_seq,
        choice,
    )


def test_parse_name_expr():
    result = pipe(
        "test",
        pexpr(),
    )

    assert result.is_ok()
    match result:
        case Ok(Name(name)):
            assert name == "test"

        case _:
            assert False


def test_many_long_input_preserves_order_and_remaining():
    from expression.extra.parser import many1, sep_by1

    text = "ab" * 1500 + "!"
    expected = Ok((Block(text[:-1]), (text, len(text) - 1)))
    assert many(any_of("ab")).run((text, 0)) == expected
    assert many1(any_of("ab")).run((text, 0)) == expected

    separated = ",".join("ab" * 750) + "!"
    assert sep_by1(any_of("ab"), pchar(",")).run((separated, 0)) == Ok(
        (Block("ab" * 750), (separated, len(separated) - 1))
    )


def test_many_rejects_non_consuming_parser():
    import pytest

    from expression.extra.parser import many1, preturn

    for repeated in [many(preturn(1)), many1(preturn(1)), many(opt(pchar("a")))]:
        with pytest.raises(ValueError, match="must consume input"):
            repeated("")


def test_many_preserves_input_on_failure():
    from expression.extra.parser import many1

    assert many(pchar("a")).run(("b", 0)) == Ok((Block(), ("b", 0)))
    assert many1(pchar("a"))("b").is_error()
