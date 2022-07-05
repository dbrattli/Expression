from __future__ import annotations

import string
from dataclasses import dataclass
from typing import Any, Tuple

from expression import (
    Error,
    Nothing,
    Nothing_,
    Ok,
    Option,
    Some,
    TaggedUnion,
    Tag,
    pipe,
    tag,
)
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


class ComparisonOperator(TaggedUnion):
    EQ = tag()
    NOT_EQ = tag()
    LT = tag()
    LT_E = tag()
    GT = tag()
    GT_E = tag()
    IS = tag()
    IS_NOT = tag()
    IN = tag()
    NOT_IN = tag()

    @staticmethod
    def eq() -> ComparisonOperator:
        return ComparisonOperator(ComparisonOperator.EQ)

    @staticmethod
    def not_eq() -> ComparisonOperator:
        return ComparisonOperator(ComparisonOperator.NOT_EQ)


@dataclass
class Compare:
    left: Expression
    comparators: Block[Expression]
    ops: Block[ComparisonOperator]


class BoolOp(TaggedUnion):
    AND = tag()
    OR = tag()

    @staticmethod
    def and_() -> BoolOp:
        return BoolOp(BoolOp.AND)

    @staticmethod
    def or_() -> BoolOp:
        return BoolOp(BoolOp.OR)


class Expression(TaggedUnion):
    CONSTANT = tag()
    NAME = Tag[str]()
    BOOL_OP = tag(BoolOp)
    COMPARE = tag(Compare)

    @staticmethod
    def name(name: str) -> Expression:
        return Expression(Expression.NAME, name)

    @staticmethod
    def compare(compare: Compare) -> Expression:
        return Expression(Expression.COMPARE, compare)

    @staticmethod
    def constant(value: Any) -> Expression:
        return Expression(Expression.CONSTANT, value)


def pname() -> Parser[Expression]:
    first = any_of(string.ascii_letters + "_")
    rest = pipe(
        any_of(string.ascii_letters + string.digits + "_"),
        many,
        opt,
    )

    def mapper(first: str, rest: Option[Block[str]]) -> str:
        match rest:
            case Some(letters):
                return first + "".join(letters)
            case _:
                return first

    return first.and_then(rest).starmap(mapper).map(Expression.name)


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
        case Ok(Expression(Expression.NAME, name)):
            assert name == "test"

        case _:
            assert False
