from lexer import Lexer, TK, Token
from utils import Peekable, Spanned
from expr import (
    App,
    BinOp,
    Expr,
    Fun,
    Ident,
    IntLit,
    LetIn,
    Negate,
    Op,
    Print,
    RawLetBind,
)

from dataclasses import dataclass


class SyntaxError(Exception):
    pass


@dataclass
class UnexpectedToken(SyntaxError):
    expected: list[TK]
    got: Token


class UnexpectedEOI(SyntaxError):
    pass


BINOP_TKS = [TK.TK_ADD, TK.TK_SUB, TK.TK_MUL, TK.TK_DIV, TK.TK_MOD]

EXPR_TKS = [TK.TK_LET, TK.TK_FUN, TK.TK_PRINT, TK.TK_IDENT, TK.TK_INT, TK.TK_LPAREN]

EXPR_TERMINATORS = [TK.TK_RPAREN, TK.TK_COMMA, TK.TK_IN, TK.TK_EOF]


class Parser:
    source: str
    lexer: Peekable[Token]

    def __init__(self, source):
        self.source = source
        self.lexer = Peekable(Lexer(source))

    def parse_expr(self) -> Expr:
        lhs: Expr = self.parse_base_expr()

        while True:
            peeked = self.peek()
            if peeked in BINOP_TKS:
                op = self.next().map_data(Op.from_tk)
                rhs = self.parse_base_expr_or_unary_op()
                lhs = Spanned(span=lhs.span + rhs.span, data=BinOp(op, lhs, rhs))
            elif peeked in EXPR_TKS:
                arg = self.parse_base_expr()
                lhs = Spanned(span=lhs.span + arg.span, data=App(f=lhs, arg=arg))
            elif peeked in EXPR_TERMINATORS:
                break
            else:
                raise UnexpectedToken(
                    expected=BINOP_TKS + EXPR_TKS + EXPR_TERMINATORS, got=self.next()
                )

        return lhs

    def parse_base_expr_or_unary_op(self):
        # Could generalise this to other prefix unary operators like boolean negation
        if self.peek() == TK.TK_SUB:
            return self.parse_negation()
        else:
            return self.parse_base_expr()

    def parse_base_expr(self) -> Expr:
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
            case TK.TK_LPAREN:
                lparen = self.next()
                expr = self.parse_expr()
                rparen = self.expect(TK.TK_RPAREN)
                return Spanned(span=lparen.span + rparen.span, data=expr.data)
            case _:
                raise UnexpectedToken(
                    expected=EXPR_TKS,
                    got=self.next(),
                )

    def parse_negation(self) -> Expr:
        minus = self.next()
        operand = self.parse_base_expr()
        return Spanned(span=minus.span + operand.span, data=Negate(operand))

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

    def peek(self) -> TK:
        match self.lexer.peek():
            case Token(_, kind):
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

    def expect(self, expected: TK) -> Token:
        match self.peek():
            case kind if kind == expected:
                return self.next()
            case TK.TK_EOF:
                raise UnexpectedEOI()
            case _:
                raise UnexpectedToken(expected=[expected], got=self.next())

        # Mypy doesn't seem to have implemented match exhaustivity checking
        assert False, "unreachable"

    def token_source(self, tok: Token) -> Spanned[str]:
        return tok.get_source(self.source)
