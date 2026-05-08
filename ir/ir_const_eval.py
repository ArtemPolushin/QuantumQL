from ir.ir_classes import *
from ir.ir_expr_evaluator import IRExprEvaluator


class ConstEvaluator:
    def __init__(self):
        self.constants = {}
        self.evaluator = IRExprEvaluator()
    
    def evaluate(self, ir_program: IRProgram) -> IRProgram:
        new_body = []
        for stmt in ir_program.body:
            if isinstance(stmt, IRConstDecl):
                try:
                    value = self.evaluator.eval_to_value(stmt.value)
                    self.constants[stmt.name] = value
                    self.evaluator.env[stmt.name] = value
                except Exception:
                    raise ValueError(f"Cannot evaluate const '{stmt.name}' at compile time")
            else:
                new_body.append(stmt)
        
        result = []
        for stmt in new_body:
            result.append(self._eval_stmt(stmt))
        
        return IRProgram(result)
    
    def _eval_stmt(self, stmt: IRStmt) -> IRStmt:
        if isinstance(stmt, IRApply):
            return IRApply(
                gate=stmt.gate,
                params=[self.evaluator.eval_to_expr(p) for p in stmt.params],
                targets=[self._subst_target(t) for t in stmt.targets]
            )
        elif isinstance(stmt, IRGateDef):
            return IRGateDef(
                name=stmt.name,
                params=stmt.params,
                body=[self._eval_stmt(s) for s in stmt.body]
            )
        elif isinstance(stmt, IRCreateQubits):
            new_size = self._subst_const_in_value(stmt.size)
            return IRCreateQubits(stmt.name, new_size)
        elif isinstance(stmt, IRCreateBits):
            new_size = self._subst_const_in_value(stmt.size)
            return IRCreateBits(stmt.name, new_size)
        elif isinstance(stmt, IRSelectStmt):
            if stmt.condition:
                return IRSelectStmt(
                    alias=stmt.alias,
                    source=stmt.source,
                    condition=self.evaluator.eval_to_expr(stmt.condition)
                )
            return stmt
        elif isinstance(stmt, IRAggregateTarget):
            return IRAggregateTarget(
                source=stmt.source,
                condition=self.evaluator.eval_to_expr(stmt.condition) if stmt.condition else None
            )
        elif isinstance(stmt, IRMeasure):
            return IRMeasure(
                source=[self._subst_target(t) for t in stmt.source],
                target=[self._subst_target(t) for t in stmt.target] if stmt.target else None
            )
        else:
            return stmt
    
    def _subst_const_in_value(self, value):
        if isinstance(value, str) and value in self.constants:
            return int(self.constants[value])
        return value
    
    def _subst_target(self, target):
        if isinstance(target, IRQubit):
            new_index = target.index
            if isinstance(new_index, str) and new_index in self.constants:
                new_index = int(self.constants[new_index])
            elif isinstance(new_index, (int, float)) and new_index < 0:
                pass
            return IRQubit(target.reg, new_index)
        if isinstance(target, IRAggregateTarget):
            return IRAggregateTarget(
                source=target.source,
                condition=self.evaluator.eval_to_expr(target.condition) if target.condition else None
            )
        return target