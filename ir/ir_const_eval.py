from ir.ir_classes import *
import math


class ConstEvaluator:    
    def __init__(self):
        self.env = {
            'pi': math.pi,
            'e': math.e,
            'tau': math.pi * 2
        }
    
    def evaluate(self, ir_program: IRProgram) -> IRProgram:
        new_body = []
        for stmt in ir_program.body:
            new_body.append(self._eval_stmt(stmt))
        return IRProgram(new_body)
    
    def _eval_stmt(self, stmt: IRStmt) -> IRStmt:
        if isinstance(stmt, IRApply):
            return IRApply(
                gate=stmt.gate,
                params=[self._eval_expr(p) for p in stmt.params],
                targets=stmt.targets
            )
        elif isinstance(stmt, IRGateDef):
            return IRGateDef(
                name=stmt.name,
                params=stmt.params,
                body=[self._eval_stmt(s) for s in stmt.body]
            )
        elif isinstance(stmt, IRSelectStmt):
            if stmt.condition:
                return IRSelectStmt(
                    alias=stmt.alias,
                    source=stmt.source,
                    condition=self._eval_expr(stmt.condition)
                )
            return stmt
        else:
            return stmt
    
    def _eval_expr(self, expr: IRExpr) -> IRExpr:
        try:
            value = self._compute(expr)
            return IRNumber(value)
        except (ValueError, TypeError, KeyError):
            return self._eval_subexprs(expr)
    
    def _eval_subexprs(self, expr: IRExpr) -> IRExpr:
        if isinstance(expr, IRBinOp):
            return IRBinOp(
                self._eval_expr(expr.left),
                expr.op,
                self._eval_expr(expr.right)
            )
        elif isinstance(expr, IRUnaryOp):
            return IRUnaryOp(
                expr.op,
                self._eval_expr(expr.expr)
            )
        elif isinstance(expr, IRFuncCall):
            return IRFuncCall(
                expr.name,
                [self._eval_expr(a) for a in expr.args]
            )
        else:
            return expr
    
    def _compute(self, expr: IRExpr) -> float:
        if isinstance(expr, IRNumber):
            return expr.value
        elif isinstance(expr, IRConst):
            if expr.name in self.env:
                return self.env[expr.name]
            raise ValueError(f"Unknown constant: {expr.name}")
        elif isinstance(expr, IRBinOp):
            left = self._compute(expr.left)
            right = self._compute(expr.right)
            op = expr.op
            if op == '+': return left + right
            if op == '-': return left - right
            if op == '*': return left * right
            if op == '/': return left / right
            if op == '**': return left ** right
            if op == '%': return left % right
            raise ValueError(f"Unknown binary operator: {op}")
        elif isinstance(expr, IRUnaryOp):
            val = self._compute(expr.expr)
            if expr.op == '-': return -val
            if expr.op == '+': return +val
            raise ValueError(f"Unknown unary operator: {expr.op}")
        elif isinstance(expr, IRFuncCall):
            args = [self._compute(a) for a in expr.args]
            name = expr.name.lower()
            if name == 'sin': return math.sin(*args)
            if name == 'cos': return math.cos(*args)
            if name == 'tan': return math.tan(*args)
            if name == 'exp': return math.exp(*args)
            if name == 'log': return math.log(*args)
            if name == 'sqrt': return math.sqrt(*args)
            if name == 'abs': return abs(*args)
            raise ValueError(f"Unknown function: {expr.name}")
        else:
            raise ValueError(f"Cannot compute: {expr}")