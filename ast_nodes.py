from dataclasses import dataclass, field
from typing import List, Optional, Union

class Stmt:
    pass

class Expr:
    pass

class Target:
    pass

@dataclass
class Program:
    statements: List[Stmt]

@dataclass
class CreateQubits(Stmt):
    name: str
    size: int

@dataclass
class CreateBits(Stmt):
    name: str
    size: int

@dataclass
class QubitRef(Target):
    register: str
    index: Optional[Union[int, str, tuple]] = None

@dataclass
class ApplyGate(Stmt):
    gate: str
    targets: List[Target]
    params: List[Expr] = field(default_factory=list)

@dataclass
class Measure(Stmt):
    targets: List[Target]
    bits: Optional[List[str]] = None

@dataclass
class GateDef(Stmt):
    name: str
    params: List[str]
    body: List[Stmt]

@dataclass
class Number(Expr):
    value: float

@dataclass
class Constant(Expr):
    name: str

@dataclass
class Var(Expr):
    name: str

@dataclass
class BinOp(Expr):
    left: Expr
    op: str
    right: Expr

@dataclass
class UnaryOp(Expr):
    op: str
    expr: Expr

@dataclass
class FuncCall(Expr):
    name: str
    args: List[Expr]

@dataclass
class SelectStmt(Stmt):
    alias: str
    source: str
    condition: Optional[Expr]

@dataclass
class SelectExpr(Target):
    alias: str
    source: str
    condition: Optional[Expr]

@dataclass
class InputParam(Stmt):
    name: str