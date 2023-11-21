from types import NoneType
from typing import Optional, assert_never
from lexer import Lexer, TK, Token
from utils import Peekable, Spanned
from expr import Expr, Fun, Ident, IntLit, LetIn, Print, RawExpr, RawLetBind

from dataclasses import dataclass


class SyntaxError(Exception):
    pass


@dataclass
class UnexpectedToken(SyntaxError):
    expected: list[TK]
    got: Token


class UnexpectedEOI(SyntaxError):
    pass


class Parser:
    source: str
    lexer: Peekable[Token]

    def __init__(self, source):
        self.source = source
        self.lexer = Peekable(Lexer(source))

    def expect(self, expected: TK) -> Token:
        match self.lexer.peek():
            case Token(kind, _) as tok if kind == expected:
                return tok
            case Token(TK.TK_EOF, _) | None:
                raise UnexpectedEOI()
            case Token(_, _) as tok:
                raise UnexpectedToken(expected=[expected], got=tok)

        # Mypy doesn't seem to have implemented match exhaustivity checking
        assert False, "unreachable"

    def peek(self) -> TK:
        match self.lexer.peek():
            case Token(kind, _):
                return kind
            case None:
                return TK.TK_EOF

        assert False, "unreachable"

    def next(self) -> Token:
        match next(self.lexer):
            case None:
                raise UnexpectedEOI()
            case Token(_, _) as tok:
                return tok

        assert False, "unreachable"

    def token_source(self, tok: Token) -> Spanned[str]:
        return tok.get_source(self.source)

    def parse_let(self) -> Expr:
        let = self.next()
        bindings = []
        while self.peek() != TK.TK_IN:
            name = self.token_source(self.expect(TK.TK_IDENT))
            self.expect(TK.TK_ASSIGN)
            value = self.parse_expr()
            bind = RawLetBind(name, value)
            bindings.append(Spanned(span=name.span + value.span, data=bind))

            if self.peek() == TK.TK_COMMA:
                self.next()
            else:
                break

        self.expect(TK.TK_IN)
        body = self.parse_expr()

        return Spanned(span=let.span + body.span, data=LetIn(bindings, body))

    def parse_fun(self) -> Expr:
        fun = self.next()

        params: list[Spanned[str]] = []
        while self.peek() != TK.TK_ARROW:
            name = self.token_source(self.expect(TK.TK_IDENT))
            params.append(name)

        self.expect(TK.TK_ARROW)
        # We do a little bit of auto-currying
        body: Expr = self.parse_expr()
        first_param, *rest_params = params
        for param in reversed(rest_params):
            body = Spanned(span=param.span + body.span, data=Fun(param, body))

        return Spanned(
            span=fun.span + body.span, data=Fun(param=first_param, body=body)
        )

    def parse_print(self) -> Expr:
        print_kw = self.next()
        value = self.parse_expr()

        return Spanned(span=print_kw.span + value.span, data=Print(value))

    def parse_ident(self) -> Expr:
        ident = self.next()
        return Spanned(span=ident.span, data=Ident(self.token_source(ident)))

    def parse_int(self) -> Expr:
        num = self.token_source(self.next())
        return Spanned(span=num.span, data=IntLit(int(num.data)))

    def parse_expr(self) -> Expr:
        match self.peek():
            case TK.TK_LET:
                return self.parse_let()
            case TK.TK_FUN:
                return self.parse_fun()
            case TK.TK_PRINT:
                return self.parse_print()
            case TK.TK_IDENT:
                return self.parse_ident()
            case TK.TK_INT:
                return self.parse_int()
            case _:
                raise UnexpectedToken(
                    expected=[
                        TK.TK_LET,
                        TK.TK_FUN,
                        TK.TK_PRINT,
                        TK.TK_IDENT,
                        TK.TK_INT,
                    ],
                    got=self.next(),
                )

        assert False, "unreachable"
