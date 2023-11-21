from typing import Optional, assert_never
from lexer import Lexer, TK, Token
from utils import Peekable
from expr import Expr

from dataclasses import dataclass


@dataclass
class UnexpectedToken:
    expected: list[TK]
    got: Token


class UnexpectedEOI:
    pass


SyntaxError = UnexpectedEOI | UnexpectedToken


class Parser:
    source: str
    lexer: Peekable[Optional[Token]]

    def __init__(self, source):
        self.source = source
        self.lexer = Peekable(Lexer(source))

    def expect(self, expected: TK) -> Token | SyntaxError:
        match self.lexer.peek():
            case Token(kind, _) as tok if kind == expected:
                return tok
            case Token(TK.TK_EOF, _) | None:
                return UnexpectedEOI()
            case tok:
                return UnexpectedToken(expected=[expected], got=tok)

        # Mypy doesn't seem to have implemented match exhaustivity checking
        assert False, "unreachable"

    def peek(self) -> TK:
        match self.lexer.peek():
            case Token(kind, _):
                return kind
            case None:
                return TK.TK_EOF

        assert False, "unreachable"

    def parse_expr(self) -> Expr | SyntaxError:
        return UnexpectedEOI()
