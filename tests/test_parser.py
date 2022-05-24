from __future__ import annotations

import string
from dataclasses import dataclass
from typing import Any, Tuple

from expression import Error, Nothing, Ok, Option, Some, TaggedUnion, match, pipe, tag
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
    with match(result) as case:
        for a in case(Ok[str, str]):
            assert a == "A"
        if case._:
            assert False


def test_parse_pchar_fluent():
    input = "ABC"
    parseA: Parser[str] = Parser.pchar("A")

    result = parseA(input)

    assert result.is_ok()
    with match(result) as case:
        for a in case(Ok[str, str]):
            assert a == "A"
        if case._:
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
    with match(result) as case:
        for (a, b) in case(Ok[Tuple[str, str], str]):
            assert (a, b) == ("A", "B")
        if case._:
            assert False


def test_parse_a_then_b_fluent():
    input = "ABC"
    parseAB = pchar("A").and_then(pchar("B"))

    result = parseAB(input)
    assert result.is_ok()
    with match(result) as case:
        for (a, b) in case(Ok[Tuple[str, str], str]):
            assert (a, b) == ("A", "B")
        if case._:
            assert False


def test_pstring():
    parse_abc = pstring("ABC")

    ret = parse_abc("ABCDE")  # Success ("ABC", "DE")
    assert ret.is_ok()
    with match(ret) as case:
        for success in case(Ok[str, str]):
            assert success == "ABC"
        if case._:
            assert False

    ret = parse_abc("A|CDE")  # Failure "Expecting 'B'. Got '|'"
    assert ret.is_error()
    with match(ret) as case:
        for error in case(Error[str, str]):
            assert error == "Expecting 'B'. Got '|'"
        if case._:
            assert False

    ret = parse_abc("AB|DE")  # Failure "Expecting 'C'. Got '|'"
    assert ret.is_error()
    with match(ret) as case:
        for error in case(Error[str, str]):
            assert error == "Expecting 'C'. Got '|'"
        if case._:
            assert False


def test_int():
    ret = pint("123C")

    with match(ret) as case:
        for success in case(Ok[int, str]):
            assert success == 123
        if case._:
            assert False


def test_int_negative():
    ret = pint("-123C")

    with match(ret) as case:
        for success in case(Ok[int, str]):
            assert success == -123
        if case._:
            assert False


def test_float():
    ret = pfloat("123C")

    with match(ret) as case:
        for success in case(Ok[float, str]):
            assert success == 123
        if case._:
            assert False


def test_float_with_decimal():
    ret = pfloat("123.45C")

    with match(ret) as case:
        for success in case(Ok[float, str]):
            assert success == 123.45
        if case._:
            assert False


def test_negative_float_with_decimal():
    ret = pfloat("-123.45C")

    with match(ret) as case:
        for success in case(Ok[float, str]):
            assert success == -123.45
        if case._:
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
    CONSTANT = tag(Any)
    NAME = tag(str)
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
        with match(rest) as case:
            if case(Nothing):
                return first
            for letters in case(Some[Block[str]]):
                return first + "".join(letters)

            return case.default(first)

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
    name = pipe(
        "test",
        pexpr(),
    )

    assert name.is_ok()
    with match(name) as case:
        if case(Nothing):
            assert False
        for expr in case(Ok[Expression, str]):
            with match(expr) as case:
                for name in case(Expression.NAME):
                    assert name == "test"
                    break
                else:
                    assert False
                break
        else:
            assert False
