from dataclasses import dataclass
from enum import Enum

from utils import Spanned


@dataclass
class RawLetBind:
    name: Spanned[str]
    value: "Expr"


@dataclass
class LetIn:
    bindings: list[Spanned[RawLetBind]]
    body: "Expr"


@dataclass
class Fun:
    # Only a single parameter because of auto-currying
    param: Spanned[str]
    body: "Expr"


class Op(Enum):
    OP_ADD = "+"
    OP_SUB = "-"
    OP_MUL = "*"
    OP_DIV = "/"
    OP_MOD = "%"


@dataclass
class BinOp:
    op: Op
    left: "Expr"
    right: "Expr"


@dataclass
class Print:
    value: "Expr"


@dataclass
class Ident:
    ident: Spanned[str]


@dataclass
class IntLit:
    num: int


RawExpr = LetIn | Fun | BinOp | Print | Ident | IntLit

Expr = Spanned[RawExpr]
