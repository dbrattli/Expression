from typing import Tuple

from expression import Error, Ok, match, pipe
from expression.extra.parser import Parser, and_then, pchar, pfloat, pint, pstring


def test_parse_pchar():
    input = "ABC"
    parseA: Parser[str] = pchar("A")

    result = parseA(input)

    assert result.is_ok()
    with match(result) as case:
        for (a, b) in case(Ok[Tuple[str, str], str]):
            assert (a, b) == ("A", "BC")
        if case._:
            assert False


def test_parse_pchar_fluent():
    input = "ABC"
    parseA: Parser[str] = Parser.pchar("A")

    result = parseA(input)

    assert result.is_ok()
    with match(result) as case:
        for (a, b) in case(Ok[Tuple[str, str], str]):
            assert (a, b) == ("A", "BC")
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
        for (a, b), c in case(Ok[Tuple[Tuple[str, str], str], str]):
            assert (a, b) == ("A", "B")
            assert c == "C"
        if case._:
            assert False


def test_parse_a_then_b_fluent():
    input = "ABC"
    parseAB = pchar("A").and_then(pchar("B"))

    result = parseAB(input)
    assert result.is_ok()
    with match(result) as case:
        for (a, b), c in case(Ok[Tuple[Tuple[str, str], str], str]):
            assert (a, b) == ("A", "B")
            assert c == "C"
        if case._:
            assert False


def test_pstring():
    parse_abc = pstring("ABC")

    ret = parse_abc("ABCDE")  # Success ("ABC", "DE")
    assert ret.is_ok()
    with match(ret) as case:
        for success, remaining in case(Ok[Tuple[str, str], str]):
            assert success == "ABC"
            assert remaining == "DE"
        if case._:
            assert False

    ret = parse_abc("A|CDE")  # Failure "Expecting 'B'. Got '|'"
    assert ret.is_error()
    with match(ret) as case:
        for error in case(Error[Tuple[str, str], str]):
            assert error == "Expecting 'B'. Got '|'"
        if case._:
            assert False

    ret = parse_abc("AB|DE")  # Failure "Expecting 'C'. Got '|'"
    assert ret.is_error()
    with match(ret) as case:
        for error in case(Error[Tuple[str, str], str]):
            assert error == "Expecting 'C'. Got '|'"
        if case._:
            assert False


def test_int():
    ret = pint("123C")
    print(ret)

    with match(ret) as case:
        for success, remaining in case(Ok[Tuple[int, str], str]):
            assert success == 123
            assert remaining == "C"
        if case._:
            assert False


def test_int_negative():
    ret = pint("-123C")
    print(ret)

    with match(ret) as case:
        for success, remaining in case(Ok[Tuple[int, str], str]):
            assert success == -123
            assert remaining == "C"
        if case._:
            assert False


def test_float():
    ret = pfloat("123C")
    print(ret)

    with match(ret) as case:
        for success, remaining in case(Ok[Tuple[float, str], str]):
            assert success == 123
            assert remaining == "C"
        if case._:
            assert False


def test_float_with_decimal():
    ret = pfloat("123.45C")
    print(ret)

    with match(ret) as case:
        for success, remaining in case(Ok[Tuple[float, str], str]):
            assert success == 123.45
            assert remaining == "C"
        if case._:
            assert False


def test_negative_float_with_decimal():
    ret = pfloat("-123.45C")

    with match(ret) as case:
        for success, remaining in case(Ok[Tuple[float, str], str]):
            assert success == -123.45
            assert remaining == "C"
        if case._:
            assert False
