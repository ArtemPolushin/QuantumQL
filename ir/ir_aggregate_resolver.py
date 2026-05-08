from ir.ir_classes import *
from ir.ir_expr_evaluator import IRExprEvaluator
from typing import Dict, List, Optional


class IRAggregateResolver:
    def __init__(self):
        self.reg_sizes: Dict[str, int] = {}
        self.aliases: Dict[str, List[IRQubit]] = {}
        self.evaluator = IRExprEvaluator()
    
    def resolve(self, ir_program: IRProgram) -> IRProgram:
        for stmt in ir_program.body:
            if isinstance(stmt, IRCreateQubits):
                self.reg_sizes[stmt.name] = stmt.size
        
        for stmt in ir_program.body:
            if isinstance(stmt, IRSelectStmt):
                qubits = self._resolve_aggregate(stmt.source, stmt.condition)
                self.aliases[stmt.alias] = qubits
        
        new_body = []
        for stmt in ir_program.body:
            if isinstance(stmt, IRApply):
                new_targets = self._resolve_targets(stmt.targets)
                if len(new_targets) == 0:
                    continue
                stmt.targets = new_targets
                new_body.append(stmt)
            
            elif isinstance(stmt, IRMeasure):
                new_source = self._resolve_targets(stmt.source)
                if len(new_source) == 0:
                    continue
                stmt.source = new_source
                
                if stmt.target:
                    stmt.target = self._resolve_targets(stmt.target)
                
                new_body.append(stmt)
            
            else:
                new_body.append(stmt)
        
        return IRProgram(new_body)
    
    def _resolve_targets(self, targets: List[IRTarget]) -> List[IRQubit]:
        result = []
        for target in targets:
            if isinstance(target, IRAggregateAlias):
                result.extend(self._resolve_alias_target(target))
            elif isinstance(target, IRAggregateTarget):
                result.extend(self._resolve_aggregate_target(target))
            else:
                result.append(target)
        return result
    
    def _resolve_alias_target(self, target: IRAggregateAlias) -> List[IRQubit]:
        if target.alias in self.aliases:
            return self.aliases[target.alias]
        elif target.alias in self.reg_sizes:
            return self._resolve_aggregate(target.alias, None)
        else:
            raise ValueError(
                f"Unknown alias or register in ALL FROM: {target.alias}"
            )
    
    def _resolve_aggregate_target(self, target: IRAggregateTarget) -> List[IRQubit]:
        return self._resolve_aggregate(target.source, target.condition)
    
    def _resolve_aggregate(self, source_reg: str,
                          condition: Optional[IRExpr]) -> List[IRQubit]:
        if source_reg not in self.reg_sizes:
            raise ValueError(f"Unknown register: {source_reg}")
        
        size = self.reg_sizes[source_reg]
        qubits = []
        
        for idx in range(size):
            if condition is None:
                qubits.append(IRQubit(source_reg, idx))
            else:
                if self.evaluator.eval_condition(condition, idx):
                    qubits.append(IRQubit(source_reg, idx))
        
        return qubits