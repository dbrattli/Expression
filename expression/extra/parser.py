from __future__ import annotations

import string
from collections.abc import Callable
from typing import Any, Generic, TypeVar, overload

from expression.collections import Block, block
from expression.core import Error, Nothing, Ok, Option, Result, Some, curry, fst, pipe


_A = TypeVar("_A")
_B = TypeVar("_B")
_C = TypeVar("_C")
_D = TypeVar("_D")
_E = TypeVar("_E")

Remaining = tuple[str, int]
ParseResult = Result[tuple[_A, Remaining], str]


class Parser(Generic[_A]):
    """The Parser class."""

    __slots__ = ["_name", "_run"]

    def __init__(self, run: Callable[[Remaining], ParseResult[_A]], name: str | None = None) -> None:
        self._run = run
        self._name = name or "parser"

    def __call__(self, input: str) -> Result[_A, str]:
        """Returns result without the remaining string."""
        return self._run((input, 0)).map(fst)

    def run(self, input: Remaining) -> ParseResult[_A]:
        """Returns parser result and the remaining string."""
        return self._run(input)

    @staticmethod
    def fail(error: str) -> Parser[Any]:
        return fail(error)

    @staticmethod
    def pchar(char: str) -> Parser[str]:
        return pchar(char)

    @staticmethod
    def any_of(list_of_chars: str) -> Parser[str]:
        return any_of(list_of_chars)

    def and_then(self, p2: Parser[_B]) -> Parser[tuple[_A, _B]]:
        return pipe(self, and_then(p2))

    def ignore_then(self, p2: Parser[_B]) -> Parser[_B]:
        return pipe(self, ignore_then(p2))

    def then_ignore(self, p2: Parser[Any]) -> Parser[_A]:
        return pipe(self, then_ignore(p2))

    def or_else(self, parser2: Parser[_A]) -> Parser[_A]:
        return or_else(self)(parser2)

    def map(self, mapper: Callable[[_A], _B]) -> Parser[_B]:
        mapped = map(mapper)
        return pipe(self, mapped)

    @overload
    def starmap(self: Parser[tuple[_B, _C]], mapper: Callable[[_B, _C], _D]) -> Parser[_D]: ...

    @overload
    def starmap(self: Parser[tuple[_B, _C, _D]], mapper: Callable[[_B, _C, _D], _E]) -> Parser[_E]: ...

    def starmap(self: Parser[Any], mapper: Callable[..., Any]) -> Parser[Any]:
        return pipe(self, starmap(mapper))

    def opt(self) -> Parser[Option[_A]]:
        return opt(self)

    def ignore(self) -> Parser[None]:
        return ignore(self)

    def bind(self, binder: Callable[[_A], Parser[_B]]) -> Parser[_B]:
        bound = bind(binder)
        return pipe(self, bound)

    def between(self, p2: Parser[_A], p3: Parser[Any]) -> Parser[_A]:
        return between(p2)(p3)(self)

    def __repr__(self) -> str:
        return self._name

    def __str__(self) -> str:
        return repr(self)


def pchar(char: str) -> Parser[str]:
    """Parse the given character."""

    def run(input: Remaining) -> ParseResult[str]:
        remaining, pos = input
        if pos >= len(remaining):
            return Error("no more input")

        first = remaining[pos]  # input[0], remaining = input[1:]
        if first == char:
            return Ok((char, (remaining, pos + 1)))
        else:
            msg = f"Expecting '{char}'. Got '{first}'"
            return Error(msg)

    return Parser(run, f"pchar('{char}')")


@curry(1)
def and_then(p2: Parser[_B], p1: Parser[_A]) -> Parser[tuple[_A, _B]]:
    """And then.

    The parser p1 .>>. p2 applies the parsers p1 and p2 in sequence and
    returns the results in a tuple.

    Args:
        p2 (Parser[_B]): Second parser.
        p1 (Parser[_A]): First parser.

    Returns:
        Parser[Tuple[_A, _B]]: Result parser.
    """

    def run(input: Remaining) -> ParseResult[tuple[_A, _B]]:
        result1 = p1.run(input)
        match result1:
            case Result(tag="error", error=error):
                return Error(error)
            case Result(ok=(value1, remaining1)):
                result2 = p2.run(remaining1)

                match result2:
                    case Result(tag="error", error=error):
                        return Error(error)
                    case Result(ok=(value2, remaining2)):
                        return Ok(((value1, value2), remaining2))

    return Parser(run, f"and_then({p2}, {p1}")


@curry(1)
def or_else(p1: Parser[_A], p2: Parser[_A]) -> Parser[_A]:
    def run(input: Remaining) -> ParseResult[_A]:
        result1 = p1.run(input)
        match result1:
            case Result(tag="ok"):
                return result1
            case _:
                result2 = p2.run(input)
                return result2

    return Parser(run, f"or_else({p2}, {p1}")


def choice(list_of_parsers: Block[Parser[_A]]) -> Parser[_A]:
    return list_of_parsers.reduce(lambda a, b: or_else(a)(b))


def any_of(list_of_chars: str) -> Parser[str]:
    return pipe(
        list_of_chars,
        block.of_seq,
        block.map(pchar),  # convert into parsers
        choice,  # combine them
    )


parse_lowercase = any_of(string.ascii_lowercase)
parse_letters = any_of(string.ascii_letters)
parse_digit = any_of(string.digits)


@curry(1)
def map(mapper: Callable[[_A], _B], parser: Parser[_A]) -> Parser[_B]:
    def run(input: Remaining) -> ParseResult[_B]:
        # run parser with the input
        result = parser.run(input)

        # test the result for Failure/Success
        match result:
            case Result(tag="ok", ok=(value, remaining)):
                # if success, return the value transformed by f
                new_value = mapper(value)
                return Ok((new_value, remaining))

            case Result(error=error):
                # if failed, return the error
                return Error(error)

    return Parser(run, f"map(A => B, {parser})")


@curry(1)
@overload
def starmap(mapper: Callable[[_A, _B], _C], parser: Parser[tuple[_A, _B]]) -> Parser[_C]: ...


@curry(1)
@overload
def starmap(mapper: Callable[[_A, _B, _C], _D], parser: Parser[tuple[_A, _B, _C]]) -> Parser[_D]: ...


@curry(1)
def starmap(mapper: Callable[..., Any], parser: Parser[Any]) -> Parser[Any]:
    def mapper_(values: tuple[Any, ...]) -> Any:
        return mapper(*values)

    return pipe(
        parser,
        map(mapper_),
    )


def preturn(x: _A) -> Parser[_A]:
    def run(input: Remaining) -> ParseResult[_A]:
        return Ok((x, input))

    return Parser(run, f"preturn({x})")


def fail(error: str) -> Parser[Any]:
    def run(input: Remaining) -> ParseResult[Any]:
        return Error(error)

    return Parser(run, f'fail("{error}")')


def apply(f_p: Parser[Callable[[_A], _B]], x_p: Parser[_A]) -> Parser[_B]:
    def mapper(fx: tuple[Callable[[_A], _B], _A]) -> _B:
        return fx[0](fx[1])

    # create a Parser containing a pair (f,x)
    return pipe(
        f_p,
        and_then(x_p),
        # map the pair by applying f to x
        map(mapper),
    )


@curry(2)
def lift2(fn: Callable[[_A], Callable[[_B], _C]], xP: Parser[_A], yP: Parser[_B]) -> Parser[_C]:
    return apply(apply(preturn(fn), xP), yP)


def sequence(parser_list: Block[Parser[_A]]) -> Parser[Block[_A]]:
    # define the "cons" function, which is a two parameter function
    @curry(1)
    def cons(head: _A, tail: Block[_A]) -> Block[_A]:
        return tail.cons(head)

    # lift it to Parser World
    cons_p = lift2(cons)

    # process the list of parsers recursively
    match parser_list:
        case block.empty:
            return preturn(block.empty)
        case Block([head, *tail]):
            tail_ = sequence(Block(tail))
            return cons_p(head)(tail_)
        case _:
            raise ValueError("invalid parser list")


def pstring(string_input: str) -> Parser[str]:
    return pipe(
        string_input,
        block.of_seq,
        block.map(pchar),
        sequence,
        map(lambda x: "".join(x)),
    )


def parse_zero_or_more(parser: Parser[_A], input: Remaining) -> tuple[Block[_A], Remaining]:
    # run parser with the input
    first_result = parser.run(input)

    # test the result for Failure/Success
    match first_result:
        case Result(tag="ok", ok=(first_value, input_after_first_parse)):
            # if parse succeeds, call recursively
            # to get the subsequent values
            subsequent_values, remaining_input = parse_zero_or_more(parser, input_after_first_parse)
            values = subsequent_values.cons(first_value)
            return values, remaining_input
        case _:
            return (block.empty, input)


def many(parser: Parser[_A]) -> Parser[Block[_A]]:
    def run(input: Remaining) -> ParseResult[Block[_A]]:
        # parse the input -- wrap in Success as it always succeeds
        ok = parse_zero_or_more(parser, input)
        return Ok(ok)

    return Parser(run, f"many({parser})")


def many1(parser: Parser[_A]) -> Parser[Block[_A]]:
    def run(input: Remaining) -> ParseResult[Block[_A]]:
        # run parser with the input
        firstResult = parser.run(input)
        # test the result for Failure/Success
        match firstResult:
            case Result(tag="ok", ok=(first_value, input_after_first_parse)):
                # if first found, look for zeroOrMore now
                subsequent_values, remaining_input = parse_zero_or_more(parser, input_after_first_parse)
                values = subsequent_values.cons(first_value)
                return Ok((values, remaining_input))

            case Result(error=err):
                return Error(err)  # failed

    return Parser(run, f"many({parser})")


def sep_by1(p: Parser[_A], sep: Parser[Any]) -> Parser[Block[_A]]:
    """Parses one or more occurrences of p separated by sep."""
    sep_then_p = sep.ignore_then(p)

    def mapper(p: _A, plist: Block[_A]) -> Block[_A]:
        return plist.cons(p)

    return p.and_then(many(sep_then_p)).starmap(mapper)


def sep_by(p: Parser[_A], sep: Parser[Any]) -> Parser[Block[_A]]:
    """Parses zero or more occurrences of p separated by sep."""
    return sep_by1(p, sep).or_else(preturn(block.empty))


# define parser for one or more digits
digits = many1(parse_digit)


def opt(p: Parser[_A]) -> Parser[Option[_A]]:
    nothing: Option[_A] = Nothing

    def mapper(a: _A) -> Option[_A]:
        return Some(a)

    some: Parser[Option[_A]] = pipe(p, map(mapper))
    none: Parser[Option[_A]] = preturn(nothing)
    return or_else(some)(none)


@curry(1)
def then_ignore(
    p2: Parser[Any],
    p1: Parser[_A],
) -> Parser[_A]:
    """Then ignore.

    The parser p1 .>> p2 applies the parsers p1 and p2 in sequence and
    returns the result of p1.

    Args:
        p2 (Parser[_B]): Second parser.
        p1 (Parser[_A]): First parser.

    Returns:
        Parser[_A]: Result parser.
    """

    def mapper(value: tuple[_A, Any]) -> _A:
        return value[0]

    return pipe(
        p1,
        and_then(p2),
        map(mapper),
    )


@curry(1)
def ignore_then(p2: Parser[_B], p1: Parser[Any]) -> Parser[_B]:
    """Ignore then.

    The parser p1 >>. p2 applies the parsers p1 and p2 in sequence and
    returns the result of p2.

    Args:
        p2 (Parser[_B]): Second parser
        p1 (Parser[_A]): First parser.

    Returns:
        Parser[_B]: Result parser.
    """

    def mapper(value: tuple[Any, _B]) -> _B:
        return value[1]

    return pipe(
        p1,
        and_then(p2),
        map(mapper),
    )


def _pint() -> Parser[int]:
    # helper
    def result_to_int(sign: Option[str], digit_list: Block[str]) -> int:
        # ignore int overflow for now
        ret = pipe(
            digit_list,
            lambda digit_list: "".join(digit_list),
            int,
        )
        return ret * -1 if sign.is_some() else ret

    # map the digits to an int
    return pipe(
        "-",
        pchar,
        opt,
        and_then(digits),
        starmap(result_to_int),
    )


pint = _pint()


def _pfloat() -> Parser[float]:
    # helper
    def result_to_float(sd: tuple[Option[str], Block[str]], digits2: Option[Block[str]]) -> float:
        # ignore int overflow for now
        sign, digits1 = sd
        if digits2.is_some():
            digits1 = digits1 + digits2.value.cons(".")

        ret = pipe(
            digits1,
            lambda digits: "".join(digits),
            float,
        )

        return ret * -1 if sign.is_some() else ret

    # define parser for one or more digits
    digits = many1(parse_digit)

    # map the digits to an int
    ret = pipe(
        opt(pchar("-")),
        and_then(digits),
        and_then(
            opt(
                pipe(
                    pchar("."),
                    ignore_then(digits),
                )
            ),
        ),
        starmap(result_to_float),
    )
    return ret


pfloat = _pfloat()


whitespace_char = any_of(string.whitespace)
whitespace = many1(whitespace_char)


@curry(2)
def between(popen: Parser[Any], pclose: Parser[Any], p: Parser[_A]) -> Parser[_A]:
    """Parse between.

    The parser between popen pclose p applies the parsers popen, p and
    pclose in sequence. It returns the result of p.

    Args:
        popen (Parser[Any]): First parser
        pclose (Parser[Any]): Last parser
        p (Parser[_A]): Parser in between.

    Returns:
        Parser[_A]: Result of the middle (p) parser.
    """
    return pipe(
        popen,
        ignore_then(p),
        then_ignore(pclose),
    )


@curry(1)
def _starts_with(string: str, prefix: str) -> bool:
    return string.startswith(prefix)


starts_with = lift2(_starts_with)


@curry(1)
def bind(f: Callable[[_A], Parser[_B]], p: Parser[_A]) -> Parser[_B]:
    def run(input: Remaining) -> ParseResult[_B]:
        result1 = p.run(input)
        match result1:
            case Result(tag="ok", ok=(value1, remaning_input)):
                p2 = f(value1)
                return p2.run(remaning_input)
            case Result(error=err):
                return Error(err)  # failed
            case _:  # type: ignore
                return Error("parser error")

    return Parser(run, f"bind(A => Parser[B], {p}")


def ignore(p: Parser[Any]) -> Parser[None]:
    def mapper(_: Any) -> None:
        return None

    return pipe(
        p,
        map(mapper),
    )


__all__ = [
    "and_then",
    "any_of",
    "apply",
    "between",
    "bind",
    "choice",
    "fail",
    "digits",
    "map",
    "ignore",
    "ignore_then",
    "lift2",
    "many1",
    "many",
    "opt",
    "or_else",
    "parse_digit",
    "parse_letters",
    "parse_lowercase",
    "pint",
    "ParseResult",
    "Parser",
    "pchar",
    "pstring",
    "preturn",
    "sequence",
    "sep_by",
    "sep_by1",
    "starts_with",
    "then_ignore",
    "whitespace",
]
