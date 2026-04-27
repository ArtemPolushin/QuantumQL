from ir.ir_classes import *
from ast_nodes import *

class IRBuilder:
    def build(self, program):
        return IRProgram([self._stmt(s) for s in program.statements])

    def _stmt(self, stmt):
        if isinstance(stmt, CreateQubits):
            return IRCreateQubits(stmt.name, stmt.size)

        if isinstance(stmt, ApplyGate):
            return IRApply(
                gate=stmt.gate,
                params=[self._value(p) for p in (stmt.params or [])],
                targets=[self._target(t) for t in stmt.targets]
            )
        if isinstance(stmt, SelectStmt):
            return IRSelectStmt(
                stmt.alias,
                stmt.source,
                self._expr(stmt.condition) if stmt.condition else None
            )
        if isinstance(stmt, Measure):
            return IRMeasure(
                source=[self._target(t) for t in stmt.targets],
                target=[self._target(t) for t in stmt.bits] if stmt.bits else None
            )
        if isinstance(stmt, GateDef):
            return IRGateDef(
                stmt.name,
                stmt.params,
                [self._stmt(s) for s in stmt.body]
            )
        
        if isinstance(stmt, IRInputParam):
            return IRInputParam(stmt.name)

        raise ValueError(f"Unknown statement type: {type(stmt)}")

    def _value(self, v):
        if isinstance(v, (Number, Constant, Var, BinOp, UnaryOp, FuncCall)):
            return self._expr(v)
        raise ValueError(f"Unknown value type: {type(v)}")

    def _expr(self, e: Expr) -> IRExpr:
        if isinstance(e, Number):
            return IRNumber(e.value)
        if isinstance(e, Constant):
            return IRConst(e.name)
        if isinstance(e, Var):
            return IRVar(e.name)
        if isinstance(e, BinOp):
            return IRBinOp(self._expr(e.left), e.op, self._expr(e.right))
        if isinstance(e, UnaryOp):
            return IRUnaryOp(e.op, self._expr(e.expr))
        if isinstance(e, FuncCall):
            return IRFuncCall(e.name, [self._expr(a) for a in e.args])
        raise ValueError(f"Unknown expression type: {type(e)}")

    def _target(self, t):
        if isinstance(t, QubitRef):
            return IRQubit(t.register, t.index)
        if isinstance(t, SelectExpr):
            return IRSelectTarget(
                t.alias,
                t.source,
                self._expr(t.condition) if t.condition else None
            )
        if isinstance(t, str):
            return IRQubit(t)
        return t