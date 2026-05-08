from ir.ir_classes import *
from ir.ir_expr_evaluator import IRExprEvaluator
from typing import List, Optional, Dict


class SelectResolver:
    def __init__(self):
        self.reg_sizes: Dict[str, int] = {}
        self.aliases: Dict[str, List[IRQubit]] = {}
        self.evaluator = IRExprEvaluator()
    
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
                if self.evaluator.eval_condition(condition, idx):
                    qubits.append(IRQubit(source_reg, idx))
        
        return qubits