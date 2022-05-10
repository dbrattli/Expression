import string
from typing import Any, Callable, Tuple, TypeVar, cast, overload

from expression.collections import Block, block
from expression.core import (
    Error,
    Nothing,
    Ok,
    Option,
    Result,
    Some,
    curry,
    curry_flipped,
    match,
    pipe,
)

_A = TypeVar("_A")
_B = TypeVar("_B")
_C = TypeVar("_C")
_D = TypeVar("_D")


ParseResult = Result[Tuple[_A, str], str]
Parser = Callable[[str], ParseResult[_A]]


@curry(1)
def pchar(char: str, input: str) -> ParseResult[str]:
    if not input:
        return Error("no more input")

    first = input[0]
    if first == char:
        remaining = input[1:]
        return Ok((char, remaining))
    else:
        msg = f"Expecting '{char}'. Got '{first}'"
        return Error(msg)


@curry(2)
def and_then(
    parser2: Parser[_B], parser1: Parser[_A], input: str
) -> ParseResult[Tuple[_A, _B]]:
    result1 = parser1(input)
    with match(result1) as case:
        for error in case(Error[Any, str]):
            return Error[Tuple[Tuple[_A, _B], str], str](error)
        for value1, remaining1 in case(Ok[Tuple[_A, str], str]):
            result2 = parser2(remaining1)

            with match(result2) as case:
                for error in case(Error[Any, str]):
                    return Error[Any, str](error)
                for (value2, remaining2) in case(Ok[Tuple[_B, str], str]):
                    return Ok(((value1, value2), remaining2))

        return case.default(Error[Tuple[Tuple[_A, _B], str], str]("parser error"))


@curry_flipped(1)
def or_else(input: str, parser1: Parser[_A], parser2: Parser[_A]) -> ParseResult[_A]:
    result1 = parser1(input)
    with match(result1) as case:
        if case(Ok[Tuple[str, str], str]):
            return result1
        if case(Error[Any, str]):
            result2 = parser2(input)
            return result2

    return case.default(Error[Tuple[_A, str], str]("parser error"))


def choice(list_of_parsers: Block[Parser[_A]]) -> Parser[_A]:
    return list_of_parsers.reduce(or_else)


def any_of(list_of_chars: str) -> Parser[str]:
    return pipe(
        block.of_seq(list_of_chars),
        block.map(pchar),  # convert into parsers
        choice,  # combine them
    )


parse_lowercase = any_of(string.ascii_lowercase)
parse_digit = any_of(string.digits)


@curry(2)
def map(f: Callable[[_A], _B], parser: Parser[_A], input: str) -> ParseResult[_B]:
    # run parser with the input
    result = parser(input)

    # test the result for Failure/Success
    with match(result) as case:
        for value, remaining in case(Ok[Tuple[_A, str], str]):
            # if success, return the value transformed by f
            new_value = f(value)
            return Ok[Tuple[_B, str], str]((new_value, remaining))

        for error in case(Error[Tuple[_A, str], str]):
            # if failed, return the error
            return Error[Tuple[_B, str], str](error)

    return case.default(Error[Tuple[_B, str], str]("parser error"))


@curry(1)
@overload
def starmap(f: Callable[[_A, _B], _C], parser: Parser[Tuple[_A, _B]]) -> Parser[_C]:
    ...


@curry(1)
@overload
def starmap(
    f: Callable[[_A, _B, _C], _D], parser: Parser[Tuple[_A, _B, _C]]
) -> Parser[_D]:
    ...


@curry(1)
def starmap(f: Callable[..., Any], parser: Parser[Tuple[Any, ...]]) -> Parser[Any]:
    def mapper(values: Tuple[Any, ...]) -> Any:
        return f(*values)

    return pipe(parser, map(mapper))


@curry_flipped(1)
def rtn(input: str, x: _A) -> ParseResult[_A]:
    return Ok((x, input))


@curry_flipped(1)
def fail(input: str, error: str) -> ParseResult[Any]:
    return Error[Tuple[Any, str], str](error)


def apply(f_p: Parser[Callable[[_A], _B]], x_p: Parser[_A]) -> Parser[_B]:
    def mapper(fx: Tuple[Callable[[_A], _B], _A]) -> _B:
        return fx[0](fx[1])

    # create a Parser containing a pair (f,x)
    ret = pipe(
        f_p,
        and_then(x_p),
        # map the pair by applying f to x
        map(mapper),
    )
    return ret


@curry(2)
def lift2(
    f: Callable[[_A], Callable[[_B], _C]], xP: Parser[_A], yP: Parser[_B]
) -> Parser[_C]:
    return apply(apply(rtn(f), xP), yP)


def sequence(parser_list: Block[Parser[_A]]) -> Parser[Block[_A]]:
    # define the "cons" function, which is a two parameter function
    @curry(1)
    def cons(head: _A, tail: Block[_A]) -> Block[_A]:
        return tail.cons(head)

    # lift it to Parser World
    cons_p = lift2(cons)

    # process the list of parsers recursively
    with match(parser_list) as case:
        if case(block.empty):
            return rtn(block.empty)
        for head, *tail in case(Block[Parser[_A]]):
            tail_ = sequence(Block(tail))
            return cons_p(head)(tail_)

        return fail("parser error")


def pstring(string_input: str) -> Parser[str]:
    return pipe(
        string_input,
        block.of_seq,
        block.map(pchar),
        sequence,
        map(lambda x: "".join(x)),
    )


def parse_zero_or_more(parser: Parser[_A], input: str) -> Tuple[Block[_A], str]:
    # run parser with the input
    first_result = parser(input)

    # test the result for Failure/Success
    with match(first_result) as case:
        for first_value, input_after_first_parse in case(Ok[Tuple[_A, str], str]):
            # if parse succeeds, call recursively
            # to get the subsequent values
            subsequent_values, remaining_input = parse_zero_or_more(
                parser, input_after_first_parse
            )
            values = subsequent_values.cons(first_value)
            return values, remaining_input

        ret = case.default((block.empty, input))
        return ret


@curry_flipped(1)
def many(input: str, parser: Parser[_A]) -> ParseResult[Block[_A]]:
    # parse the input -- wrap in Success as it always succeeds
    ok = parse_zero_or_more(parser, input)
    return Ok[Tuple[Block[_A], str], str](ok)


@curry_flipped(1)
def many1(input: str, parser: Parser[_A]) -> ParseResult[Block[_A]]:
    # run parser with the input
    firstResult = parser(input)
    # test the result for Failure/Success
    with match(firstResult) as case:
        for first_value, input_after_first_parse in case(Ok[Tuple[_A, str], str]):
            # if first found, look for zeroOrMore now
            subsequent_values, remaining_input = parse_zero_or_more(
                parser, input_after_first_parse
            )
            values = subsequent_values.cons(first_value)
            return Ok[Tuple[Block[_A], str], str]((values, remaining_input))

        for err in case(Error[Tuple[_A, str], str]):
            return Error(err)  # failed

        return Error("parser error")


def opt(p: Parser[_A]) -> Parser[Option[_A]]:
    nothing = cast(Option[_A], Nothing)

    def mapper(a: _A) -> Option[_A]:
        return Some(a)

    some: Parser[Option[_A]] = pipe(p, map(mapper))
    none: Parser[Option[_A]] = rtn(nothing)
    return or_else(some, none)


@curry(1)
def then_ignore(
    parser2: Parser[_B],
    parser1: Parser[_A],
) -> Parser[_A]:
    def mapper(value: Tuple[_A, _B]) -> _A:
        return value[0]

    return pipe(
        parser1,
        and_then(parser2),
        map(mapper),
    )


@curry(1)
def ignore_then(parser2: Parser[_B], parser1: Parser[_A]) -> Parser[_B]:
    def mapper(value: Tuple[_A, _B]) -> _B:
        return value[1]

    return pipe(
        parser1,
        and_then(parser2),
        map(mapper),
    )


def _pint() -> Parser[int]:
    # helper
    def result_to_int(sign: Option[str], digitList: Block[str]) -> int:
        # ignore int overflow for now
        return pipe(digitList, str, int) * -1 if sign.is_some() else 1

    # define parser for one or more digits
    digits = many1(parse_digit)

    # map the digits to an int
    ret = pipe(
        opt(pchar("-")),
        and_then(digits),
        starmap(result_to_int),
    )
    return ret


pint = _pint()


def _pfloat() -> Parser[float]:
    # helper
    def result_to_float(
        sd: Tuple[Option[str], Block[str]], digits2: Option[Block[str]]
    ) -> float:
        # ignore int overflow for now
        sign, digits1 = sd
        if digits2.is_some():
            digits1 = digits1 + digits2.value.cons(".")
        return pipe(digits1, str, int) * -1 if sign.is_some() else 1

    # define parser for one or more digits
    digits = many1(parse_digit)

    # map the digits to an int
    ret = pipe(
        opt(pchar("-")),
        and_then(digits),
        then_ignore(opt(pchar("."))),
        and_then(opt(digits)),
        starmap(result_to_float),
    )
    return ret


pfloat = _pfloat()


whitespace_char = any_of(" \t\n")
whitespace = many1(whitespace_char)


def between(p1: Parser[Any], p2: Parser[_A], p3: Parser[Any]) -> Parser[_A]:
    return pipe(
        p1,
        ignore_then(p2),
        then_ignore(p3),
    )


@curry(1)
def _starts_with(string: str, prefix: str) -> bool:
    return string.startswith(prefix)


starts_with = lift2(_starts_with)


def bind(input: str, f: Callable[[_A], Parser[_B]], p: Parser[_A]) -> ParseResult[_B]:
    result1 = p(input)
    with match(result1) as case:
        for value1, remaning_input in case(Ok[Tuple[_A, str], str]):
            p2 = f(value1)
            return p2(remaning_input)

        for err in case(Error[Tuple[_A, str], str]):
            return Error(err)  # failed

        return Error("parser error")


__all__ = [
    "bind",
    "ParseResult",
    "Parser",
    "pchar",
    "and_then",
    "or_else",
    "choice",
    "any_of",
    "parse_lowercase",
    "parse_digit",
    "map",
    "rtn",
    "fail",
    "apply",
    "lift2",
    "sequence",
    "pstring",
    "many1",
    "many",
    "pint",
    "starts_with",
    "then_ignore",
    "ignore_then",
    "whitespace",
    "opt",
]
