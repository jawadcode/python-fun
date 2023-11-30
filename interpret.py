from dataclasses import dataclass
from enum import Enum
from typing import Optional
from pprint import pprint
from expr import (
    App,
    Expr,
    Fun,
    LetIn,
    Negate,
    BinOp,
    Op,
    Print,
    Ident,
    IntLit,
    RawLetBind,
)
from utils import Span, Spanned


class RuntimeError(Exception):
    pass


@dataclass
class NotBound(RuntimeError):
    span: Span


class Ty(Enum):
    TY_FUN = "function"
    TY_INT = "integer"


@dataclass
class TypeMismatch(RuntimeError):
    span: Span
    expected: Ty
    got: Ty


@dataclass
class Env:
    # This feels like a bad decision
    enclosing: "Optional[Env]"
    bindings: dict[str, "Spanned[Value]"]

    def __init__(self, enclosing: "Optional[Env]"):
        self.enclosing = enclosing
        self.bindings = {}

    def __getitem__(self, ident: str) -> "Optional[Spanned[Value]]":
        match (self.bindings.get(ident, None), self.enclosing):
            case (Spanned(_, _) as value, _):
                return value
            case (None, Env(_, _) as enclosing):
                return enclosing[ident]
            case _:
                return None

    def __setitem__(self, ident: Spanned[str], value: "Value") -> None:
        self.bindings[ident.data] = ident.map_data(lambda _: value)

    def __delitem__(self, ident: Spanned[str]) -> None:
        del self.bindings[ident.data]


@dataclass
class FunValue:
    param: Spanned[str]
    captures: Env
    body: Expr


Value = int | FunValue


class Interpret:
    env: Env

    def __init__(self, env: Optional[Env]) -> None:
        self.env = Env(env)

    def interpret(self, expr: Expr) -> Value:
        match expr.data:
            case LetIn(bindings, body):
                return self.let_in(bindings, body)
            case Fun(param, body):
                return self.fun(expr.span, param, body)
            case App(f, arg):
                return self.app(f, arg)
            case Negate(expr):
                return self.negate(expr.span, expr)
            case BinOp(op, lhs, rhs):
                return self.bin_op(expr.span, op, lhs, rhs)
            case Print(expr):
                return self.printt(expr)
            case Ident(ident):
                return self.ident(expr.span, ident)
            case IntLit(num):
                return num
            case _:
                assert False, "unreachable"

    def let_in(self, bindings: list[Spanned[RawLetBind]], body: Expr) -> Value:
        for bind in bindings:
            value = self.interpret(bind.data.value)
            self.env[bind.data.name] = value
        body_value = self.interpret(body)

        for bind in bindings:
            del self.env[bind.data.name]

        return body_value

    def fun(self, span: Span, param: Spanned[str], body: Expr) -> Value:
        # A little bit of debubbing
        print(f"\n{str(Fun(param, body))}")
        pprint([binding[0] for binding in self.env.bindings.items()])
        return FunValue(param=param, captures=Env(self.env), body=body)

    def app(self, f: Expr, arg: Expr) -> Value:
        f_value = self.interpret(f)
        arg_value = self.interpret(arg)

        match f_value:
            case FunValue(param, env, body):
                previous = self.env
                self.env = env
                self.env[param] = arg_value
                result = self.interpret(body)
                del self.env[param]
                self.env = previous
                return result
            case int(_):
                raise TypeMismatch(span=f.span, expected=Ty.TY_FUN, got=Ty.TY_INT)

    def negate(self, span: Span, expr: Expr) -> Value:
        value = self.interpret(expr)
        match value:
            case FunValue(_, _):
                raise TypeMismatch(span=span, expected=Ty.TY_INT, got=Ty.TY_FUN)
            case int(num):
                return -num

    def bin_op(self, span: Span, op: Spanned[Op], lhs: Expr, rhs: Expr) -> Value:
        lhs_value = self.interpret(lhs)
        rhs_value = self.interpret(rhs)

        match (lhs_value, rhs_value):
            case (int(x), int(y)):
                match op:
                    case Op.OP_ADD:
                        return x + y
                    case Op.OP_SUB:
                        return x - y
                    case Op.OP_MUL:
                        return x * y
                    case Op.OP_DIV:
                        return x // y
                    case Op.OP_MOD:
                        return x % y
            case (int(x), FunValue(_, _)):
                raise TypeMismatch(span=rhs.span, expected=Ty.TY_INT, got=Ty.TY_FUN)
            case (FunValue(_, _), int(y)):
                raise TypeMismatch(span=lhs.span, expected=Ty.TY_INT, got=Ty.TY_FUN)
            case _:
                raise TypeMismatch(span=span, expected=Ty.TY_INT, got=Ty.TY_FUN)

        assert False, "unreachable"

    def printt(self, expr: Expr) -> Value:
        value = self.interpret(expr)
        match value:
            case int(num):
                print(num)
            case Fun(_, _):
                print("<function value>")

        return value

    def ident(self, span: Span, ident: str) -> Value:
        match self.env[ident]:
            case Spanned(_, value):
                return value
            case None:
                raise NotBound(span)

        assert False, "unreachable"
