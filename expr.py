from dataclasses import dataclass
from enum import Enum
from lexer import TK

from utils import Spanned


@dataclass
class RawLetBind:
    name: Spanned[str]
    value: "Expr"

    def __str__(self) -> str:
        return f"({self.name.data} {str(self.value.data)})"


@dataclass
class LetIn:
    bindings: list[Spanned[RawLetBind]]
    body: "Expr"

    def __str__(self) -> str:
        bindings = " ".join(map(str, self.bindings))
        return f"(let [{bindings}] {str(self.body)})"


@dataclass
class Fun:
    # Only a single parameter because of auto-currying
    param: Spanned[str]
    body: "Expr"

    def __str__(self) -> str:
        return f"(fun {self.param.data} {str(self.body)})"


@dataclass
class App:
    f: "Expr"
    arg: "Expr"

    def __str__(self) -> str:
        return f"({str(self.f.data)} {str(self.arg.data)})"


@dataclass
class Negate:
    expr: "Expr"

    def __str__(self) -> str:
        return f"(- {str(self.expr.data)})"


class Op(Enum):
    OP_ADD = "+"
    OP_SUB = "-"
    OP_MUL = "*"
    OP_DIV = "/"
    OP_MOD = "%"

    @staticmethod
    def from_tk(kind: TK) -> "Op":
        match kind:
            case TK.TK_ADD:
                return Op.OP_ADD
            case TK.TK_SUB:
                return Op.OP_SUB
            case TK.TK_MUL:
                return Op.OP_MUL
            case TK.TK_DIV:
                return Op.OP_DIV
            case TK.TK_MOD:
                return Op.OP_MOD
            case _:
                assert False, "unreachable"


@dataclass
class BinOp:
    op: Spanned[Op]
    lhs: "Expr"
    rhs: "Expr"

    def __str__(self) -> str:
        return f"({self.op.data.value} {str(self.lhs.data)} {str(self.rhs.data)})"


@dataclass
class Print:
    value: "Expr"

    def __str__(self) -> str:
        return f"(print {str(self.value.data)})"


@dataclass
class Ident:
    ident: str

    def __str__(self) -> str:
        return self.ident


@dataclass
class IntLit:
    num: int

    def __str__(self) -> str:
        return str(self.num)


RawExpr = LetIn | Fun | App | Negate | BinOp | Print | Ident | IntLit

Expr = Spanned[RawExpr]
