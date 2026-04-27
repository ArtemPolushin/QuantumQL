from ir.ir_classes import *
import math
from typing import List, Optional, Dict


class SelectResolver:
    def __init__(self):
        self.reg_sizes: Dict[str, int] = {}
        self.aliases: Dict[str, List[IRQubit]] = {}
        self.env = {
            'pi': math.pi,
            'e': math.e,
        }
    
    def resolve(self, ir_program: IRProgram) -> IRProgram:
        for stmt in ir_program.body:
            if isinstance(stmt, IRCreateQubits):
                self.reg_sizes[stmt.name] = stmt.size
        
        new_body = []
        for stmt in ir_program.body:
            if isinstance(stmt, IRSelectStmt):
                qubits = self._evaluate_select(stmt.source, stmt.condition)
                self.aliases[stmt.alias] = qubits
                continue
            elif isinstance(stmt, IRCreateQubits):
                new_body.append(stmt)
            elif isinstance(stmt, IRApply):
                new_targets = []
                for t in stmt.targets:
                    if isinstance(t, IRSelectTarget):
                        qubits = self._evaluate_select(t.source, t.condition)
                        new_targets.extend(qubits)
                    elif isinstance(t, IRQubit):
                        if t.reg in self.aliases and t.index is None:
                            new_targets.extend(self.aliases[t.reg])
                        else:
                            new_targets.append(t)
                    else:
                        new_targets.append(t)
                stmt.targets = new_targets
                new_body.append(stmt)
            elif isinstance(stmt, IRMeasure):
                new_source = []
                for t in stmt.source:
                    if isinstance(t, IRSelectTarget):
                        qubits = self._evaluate_select(t.source, t.condition)
                        new_source.extend(qubits)
                    elif isinstance(t, IRQubit):
                        if t.reg in self.aliases and t.index is None:
                            new_source.extend(self.aliases[t.reg])
                        else:
                            new_source.append(t)
                    else:
                        new_source.append(t)
                stmt.source = new_source
                
                if stmt.target:
                    new_target = []
                    for t in stmt.target:
                        if isinstance(t, IRSelectTarget):
                            qubits = self._evaluate_select(t.source, t.condition)
                            new_target.extend(qubits)
                        else:
                            new_target.append(t)
                    stmt.target = new_target
                
                new_body.append(stmt)
            else:
                new_body.append(stmt)
        
        return IRProgram(new_body)
    
    def _evaluate_select(self, source_reg: str, condition: Optional[IRExpr]) -> List[IRQubit]:
        if source_reg not in self.reg_sizes:
            raise ValueError(f"Unknown register '{source_reg}' in SELECT")
        
        size = self.reg_sizes[source_reg]
        qubits = []
        
        for idx in range(size):
            if condition is None:
                qubits.append(IRQubit(source_reg, idx))
            else:
                if self._eval_condition(condition, idx, source_reg):
                    qubits.append(IRQubit(source_reg, idx))
        
        return qubits
    
    def _eval_condition(self, expr: IRExpr, index: int, reg_name: str = None) -> bool:
        env = {
            'index': float(index),
            'i': float(index),
        }
        
        env.update(self.env)
        
        try:
            result = self._eval_expr(expr, env)
            return bool(result)
        except Exception as e:
            raise ValueError(f"Cannot evaluate condition for index {index}: {e}")
    
    def _eval_expr(self, expr: IRExpr, env: dict) -> float:
        if isinstance(expr, IRNumber):
            return expr.value
        
        elif isinstance(expr, IRConst):
            if expr.name in env:
                return env[expr.name]
            raise ValueError(f"Unknown constant: {expr.name}")
        
        elif isinstance(expr, IRVar):
            if expr.name in env:
                return env[expr.name]
            raise ValueError(f"Unknown variable: {expr.name}")
        
        elif isinstance(expr, IRBinOp):
            left = self._eval_expr(expr.left, env)
            right = self._eval_expr(expr.right, env)
            op = expr.op
            
            if op == '+': return left + right
            if op == '-': return left - right
            if op == '*': return left * right
            if op == '/': return left / right
            if op == '**': return left ** right
            if op == '%': return left % right
            if op == '==': return float(left == right)
            if op == '!=': return float(left != right)
            if op == '<': return float(left < right)
            if op == '>': return float(left > right)
            if op == '<=': return float(left <= right)
            if op == '>=': return float(left >= right)
            if op == 'AND': return float(bool(left) and bool(right))
            if op == 'OR': return float(bool(left) or bool(right))
            
            raise ValueError(f"Unknown binary operator: {op}")
        
        elif isinstance(expr, IRUnaryOp):
            val = self._eval_expr(expr.expr, env)
            if expr.op == '-': return -val
            if expr.op == '+': return +val
            raise ValueError(f"Unknown unary operator: {expr.op}")
        
        elif isinstance(expr, IRFuncCall):
            args = [self._eval_expr(a, env) for a in expr.args]
            name = expr.name.lower()
            
            if name == 'sin' : return math.sin(*args)
            if name == 'cos' : return math.cos(*args)
            if name == 'tan' : return math.tan(*args)
            if name == 'exp' : return math.exp(*args)
            if name == 'log' : return math.log(*args)
            if name == 'sqrt': return math.sqrt(*args)
            if name == 'abs' : return abs(*args)
            if name == 'asin': return math.asin(*args)
            if name == 'acos': return math.acos(*args)
            if name == 'atan': return math.atan(*args)
            if name == 'pow' : return math.pow(*args)
            raise ValueError(f"Unknown function: {expr.name}")
        
        else:
            raise ValueError(f"Cannot evaluate expression of type: {type(expr)}")