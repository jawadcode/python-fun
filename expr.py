from dataclasses import dataclass
from enum import Enum


@dataclass
class LetBind:
    name: str
    value: "Expr"


@dataclass
class LetIn:
    bindings: list[LetBind]
    body: "Expr"


@dataclass
class Fun:
    # Only a single parameter because of auto-currying
    param: str
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
    ident: str


@dataclass
class IntLit:
    num: int


Expr = LetBind | Fun | BinOp | Print | Ident | IntLit
