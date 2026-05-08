from ir.ir_classes import *
import math
from typing import Dict


class IRExprEvaluator:    
    def __init__(self, env: Dict[str, float] = None):
        self.env = env if env is not None else {
            'pi': math.pi,
            'e': math.e,
            'tau': math.pi * 2,
        }
    
    def eval_to_value(self, expr: IRExpr) -> float:
        return self._eval_expr(expr)
    
    def eval_to_expr(self, expr: IRExpr) -> IRExpr:
        try:
            value = self._eval_expr(expr)
            return IRNumber(value)
        except (ValueError, KeyError):
            return self._simplify(expr)
    
    def _simplify(self, expr: IRExpr) -> IRExpr:
        if isinstance(expr, IRBinOp):
            return IRBinOp(
                self.eval_to_expr(expr.left),
                expr.op,
                self.eval_to_expr(expr.right)
            )
        elif isinstance(expr, IRUnaryOp):
            return IRUnaryOp(
                expr.op,
                self.eval_to_expr(expr.expr)
            )
        elif isinstance(expr, IRFuncCall):
            return IRFuncCall(
                expr.name,
                [self.eval_to_expr(a) for a in expr.args]
            )
        else:
            return expr
    
    def eval_condition(self, expr: IRExpr, index: int) -> bool:
        env_with_index = dict(self.env)
        env_with_index['index'] = float(index)
        env_with_index['i'] = float(index)
        
        evaluator = IRExprEvaluator(env_with_index)
        try:
            result = evaluator._eval_expr(expr)
            return bool(result)
        except Exception as e:
            raise ValueError(
                f"Cannot evaluate condition for index {index}: {e}"
            )
    
    def _eval_expr(self, expr: IRExpr) -> float:
        if isinstance(expr, IRNumber):
            return expr.value
        
        elif isinstance(expr, IRConst):
            if expr.name in self.env:
                return self.env[expr.name]
            raise ValueError(f"Unknown constant: {expr.name}")
        
        elif isinstance(expr, IRVar):
            if expr.name in self.env:
                return self.env[expr.name]
            raise ValueError(f"Unknown variable: {expr.name}")
        
        elif isinstance(expr, IRBinOp):
            left = self._eval_expr(expr.left)
            right = self._eval_expr(expr.right)
            op = expr.op
            
            return _apply_binary_op(left, op, right)
        
        elif isinstance(expr, IRUnaryOp):
            val = self._eval_expr(expr.expr)
            return _apply_unary_op(val, expr.op)
        
        elif isinstance(expr, IRFuncCall):
            args = [self._eval_expr(a) for a in expr.args]
            return _apply_function(expr.name, args)
        
        else:
            raise ValueError(
                f"Cannot evaluate expression of type: {type(expr)}"
            )

def _apply_binary_op(left: float, op: str, right: float) -> float:
    ops = {
        '+': lambda a, b: a + b,
        '-': lambda a, b: a - b,
        '*': lambda a, b: a * b,
        '/': lambda a, b: a / b,
        '**': lambda a, b: a ** b,
        '%': lambda a, b: a % b,
    }
    if op in ops:
        return ops[op](left, right)

    comparisons = {
        '==': lambda a, b: float(a == b),
        '!=': lambda a, b: float(a != b),
        '<':  lambda a, b: float(a < b),
        '>':  lambda a, b: float(a > b),
        '<=': lambda a, b: float(a <= b),
        '>=': lambda a, b: float(a >= b),
    }
    if op in comparisons:
        return comparisons[op](left, right)
    
    # Логические
    if op in ('AND', 'and', '&&'):
        return float(bool(left) and bool(right))
    if op in ('OR', 'or', '||'):
        return float(bool(left) or bool(right))
    
    raise ValueError(f"Unknown binary operator: {op}")


def _apply_unary_op(val: float, op: str) -> float:
    if op == '-':
        return -val
    if op == '+':
        return +val
    raise ValueError(f"Unknown unary operator: {op}")


def _apply_function(name: str, args: list) -> float:
    funcs = {
        'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
        'exp': math.exp, 'log': math.log, 'sqrt': math.sqrt,
        'abs': abs,
        'asin': math.asin, 'acos': math.acos, 'atan': math.atan,
        'pow': math.pow,
    }
    name_lower = name.lower()
    if name_lower in funcs:
        return funcs[name_lower](*args)
    raise ValueError(f"Unknown function: {name}")