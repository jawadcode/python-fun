from dataclasses import dataclass
from enum import Enum
from typing import Callable, Optional, TypeVar
from typing_extensions import override

from utils import Span, Spanned, map_pred


class TK(Enum):
    TK_LET = "'let'"
    TK_IN = "'in'"
    TK_FUN = "'fun'"
    TK_PRINT = "'print'"
    TK_INT = "integer literal"
    TK_IDENT = "identifier"
    TK_ASSIGN = "'='"
    TK_ARROW = "'=>'"
    TK_LPAREN = "'('"
    TK_RPAREN = "')'"
    TK_COMMA = "','"
    TK_ADD = "'+'"
    TK_SUB = "'-'"
    TK_MUL = "'*'"
    TK_DIV = "'/'"
    TK_MOD = "'%'"
    TK_INVALID = "<invalid token>"
    TK_EOF = "EOF"


@dataclass
class Token:
    kind: TK
    span: Span

    def __str__(self) -> str:
        return f"{self.kind.value: <15} @ {str(self.span)}"

    def get_source(self, source: str) -> Spanned[str]:
        return Spanned(span=self.span, data=source[self.span.start : self.span.end])


class Lexer:
    source: str
    start: int
    current: int
    eof: bool

    def __init__(self, source: str):
        self.source = source
        self.start = 0
        self.current = 0
        self.eof = False

    def __iter__(self) -> "Lexer":
        return self

    def skip(self):
        self.current += 1

    def at_end(self) -> bool:
        return self.current == len(self.source)

    def peek(self) -> Optional[str]:
        if self.at_end():
            return None
        else:
            return self.source[self.current]

    # Need to use 'self.at_end()' check before this
    def next(self) -> str:
        temp = self.source[self.current]
        self.current += 1
        return temp

    def skip_whitespace(self):
        while token := self.peek():
            match token:
                case "\n" | "\r" | "\t" | " ":
                    self.skip()
                case "#":
                    self.skip()
                    while t := self.peek():
                        if t != "\n":
                            self.skip()
                        else:
                            break
                case _:
                    return

    def check_keyword(self, start: int, rest: str, kind: TK) -> TK:
        source_start = self.start + start
        if (
            self.current - self.start == start + len(rest)
            and self.source[source_start : source_start + len(rest)] == rest
        ):
            return kind
        else:
            return TK.TK_IDENT

    def ident_type(self) -> TK:
        # This trie may be a little overkill for our purposes but it's easier to expand on if I want to
        match self.source[self.start]:
            case "l":
                return self.check_keyword(1, "et", TK.TK_LET)
            case "i":
                return self.check_keyword(1, "n", TK.TK_IN)
            case "f":
                return self.check_keyword(1, "un", TK.TK_FUN)
            case "p":
                return self.check_keyword(1, "rint", TK.TK_PRINT)
            case _:
                return TK.TK_IDENT

    def ident(self) -> TK:
        while map_pred(self.peek(), str.isidentifier) or map_pred(
            self.peek(), str.isdigit
        ):
            self.skip()

        return self.ident_type()

    def number(self) -> TK:
        while map_pred(self.peek(), str.isdigit):
            self.skip()

        return TK.TK_INT

    def match(self, expected: str) -> bool:
        if self.at_end() or self.peek() != expected:
            return False
        else:
            self.skip()
            return True

    def next_kind(self):
        self.skip_whitespace()

        if self.at_end():
            return TK.TK_EOF

        c = self.next()
        if c.isidentifier():
            return self.ident()
        elif c.isdigit():
            return self.number()
        else:
            match c:
                case "=":
                    return TK.TK_ARROW if self.match(">") else TK.TK_ASSIGN
                case "(":
                    return TK.TK_LPAREN
                case ")":
                    return TK.TK_RPAREN
                case ",":
                    return TK.TK_COMMA
                case "+":
                    return TK.TK_ADD
                case "-":
                    return TK.TK_SUB
                case "*":
                    return TK.TK_MUL
                case "/":
                    return TK.TK_DIV
                case "%":
                    return TK.TK_MOD
                case _:
                    return TK.TK_INVALID

    def next_token(self) -> tuple[TK, Span]:
        self.skip_whitespace()
        self.start = self.current
        return (self.next_kind(), Span(start=self.start, end=self.current))

    def __next__(self) -> Token:
        match self.next_token():
            case (TK.TK_EOF, _) if self.eof:
                raise StopIteration
            case (TK.TK_EOF, span):
                self.eof = True
                return Token(kind=TK.TK_EOF, span=span)
            case (kind, span):
                return Token(kind, span)

        assert False, "unreachable"
