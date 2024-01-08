from __future__ import annotations

import string
from dataclasses import dataclass
from typing import Any, Literal

from expression import Option, Result, case, pipe, tag, tagged_union
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
        case Result(tag="ok", ok=a):
            assert a == "A"
        case _:
            assert False


def test_parse_pchar_fluent():
    input = "ABC"
    parseA: Parser[str] = Parser.pchar("A")

    result = parseA(input)

    assert result.is_ok()
    match result:
        case Result(tag="ok", ok=a):
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
        case Result(tag="ok", ok=(a, b)):
            assert (a, b) == ("A", "B")
        case _:
            assert False


def test_parse_a_then_b_fluent():
    input = "ABC"
    parseAB = pchar("A").and_then(pchar("B"))

    result = parseAB(input)
    assert result.is_ok()
    match result:
        case Result(tag="ok", ok=(a, b)):
            assert (a, b) == ("A", "B")
        case _:
            assert False


def test_pstring():
    parse_abc = pstring("ABC")

    ret = parse_abc("ABCDE")  # Success ("ABC", "DE")
    assert ret.is_ok()
    match ret:
        case Result(tag="ok", ok=success):
            assert success == "ABC"
        case _:
            assert False

    ret = parse_abc("A|CDE")  # Failure "Expecting 'B'. Got '|'"
    assert ret.is_error()
    match ret:
        case Result(tag="error", error=error):
            assert error == "Expecting 'B'. Got '|'"
        case _:
            assert False

    ret = parse_abc("AB|DE")  # Failure "Expecting 'C'. Got '|'"
    assert ret.is_error()
    match ret:
        case Result(tag="error", error=error):
            assert error == "Expecting 'C'. Got '|'"
        case _:
            assert False


def test_int():
    ret = pint("123C")

    match ret:
        case Result(tag="ok", ok=success):
            assert success == 123
        case _:
            assert False


def test_int_negative():
    ret = pint("-123C")

    match ret:
        case Result(tag="ok", ok=success):
            assert success == -123
        case _:
            assert False


def test_float():
    ret = pfloat("123C")

    match ret:
        case Result(tag="ok", ok=success):
            assert success == 123
        case _:
            assert False


def test_float_with_decimal():
    ret = pfloat("123.45C")

    match ret:
        case Result(tag="ok", ok=success):
            assert success == 123.45
        case _:
            assert False


def test_negative_float_with_decimal():
    ret = pfloat("-123.45C")

    match ret:
        case Result(tag="ok", ok=success):
            assert success == -123.45
        case _:
            assert False


@tagged_union
class ComparisonOperator:
    tag: Literal["EQ", "NOT_EQ", "LT", "LT_E", "GT", "GT_E", "IS", "IS_NOT", "IN", "NOT_IN"] = tag()

    EQ: bool = case()
    NOT_EQ: bool = case()
    LT: bool = case()
    LT_E: bool = case()
    GT: bool = case()
    GT_E: bool = case()
    IS: bool = case()
    IS_NOT: bool = case()
    IN: bool = case()
    NOT_IN: None = case()

    @staticmethod
    def eq() -> ComparisonOperator:
        return ComparisonOperator(EQ=True)

    @staticmethod
    def not_eq() -> ComparisonOperator:
        return ComparisonOperator(NOT_EQ=True)


@dataclass
class Compare:
    left: Expression
    comparators: Block[Expression]
    ops: Block[ComparisonOperator]


@tagged_union
class BoolOp:
    AND: None = case()
    OR: None = case()

    @staticmethod
    def and_() -> BoolOp:
        return BoolOp(AND=None)

    @staticmethod
    def or_() -> BoolOp:
        return BoolOp(OR=None)


@tagged_union
class Expression:
    tag: Literal["NAME", "CONSTANT", "BOOL_OP", "COMPARE"] = tag()

    CONSTANT: bool = case()
    NAME: str = case()
    BOOL_OP: BoolOp = case()
    COMPARE: Compare = case()

    @staticmethod
    def name(name: str) -> Expression:
        return Expression(NAME=name)

    @staticmethod
    def compare(compare: Compare) -> Expression:
        return Expression(COMPARE=compare)

    @staticmethod
    def constant(value: Any) -> Expression:
        return Expression(CONSTANT=value)


def pname() -> Parser[Expression]:
    first = any_of(string.ascii_letters + "_")
    rest = pipe(
        any_of(string.ascii_letters + string.digits + "_"),
        many,
        opt,
    )

    def mapper(first: str, rest: Option[Block[str]]) -> str:
        match rest:
            case Option(tag="some", some=letters):
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
        case Result(tag="ok", ok=Expression(NAME=name)):
            assert name == "test"

        case _:
            assert False
