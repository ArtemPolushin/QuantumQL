from dataclasses import dataclass
from typing import List, Optional

@dataclass
class IRProgram:
    body: List["IRStmt"]

class IRStmt:
    pass

class IRExpr:
    pass

class IRTarget: 
    pass

@dataclass
class IRNumber(IRExpr):
    value: float

@dataclass
class IRConst(IRExpr):
    name: str

@dataclass
class IRVar(IRExpr):
    name: str

@dataclass
class IRCreateQubits(IRStmt):
    name: str
    size: int

@dataclass
class IRCreateBits(IRStmt):
    name: str
    size: int

@dataclass
class IRGateDef(IRStmt):
    name: str
    params: List[str]
    body: List[IRStmt]

@dataclass
class IRApply(IRStmt):
    gate: str
    params: List[IRExpr]
    targets: List[IRTarget]

@dataclass
class IRMeasure(IRStmt):
    source: List["IRTarget"]
    target: Optional[List["IRTarget"]] = None

@dataclass
class IRNumber(IRExpr):
    value: float

@dataclass
class IRQubit(IRTarget):
    reg: str
    index: Optional[int] = None

@dataclass
class IRBinOp(IRExpr):
    left: IRExpr
    op: str
    right: IRExpr

@dataclass
class IRUnaryOp(IRExpr):
    op: str
    expr: IRExpr

@dataclass
class IRFuncCall(IRExpr):
    name: str
    args: List[IRExpr]

@dataclass
class IRSelectStmt(IRStmt):
    alias: str
    source: str
    condition: Optional[IRExpr]

@dataclass
class IRSelectTarget(IRTarget):
    alias: str
    source: str
    condition: Optional[IRExpr]

@dataclass
class IRInputParam(IRStmt):
    name: str