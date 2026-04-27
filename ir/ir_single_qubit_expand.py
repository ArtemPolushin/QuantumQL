from ir.ir_classes import *
from gates import is_single_qubit_gate

class SingleQubitExpand:
    def expand(self, ir_program: IRProgram) -> IRProgram:
        new_body = []
        for stmt in ir_program.body:
            if isinstance(stmt, IRApply):
                new_body.extend(self._expand_apply(stmt))
            else:
                new_body.append(stmt)
        return IRProgram(new_body)
    
    def _expand_apply(self, stmt: IRApply):
        gate_lower = stmt.gate.lower()
        
        if is_single_qubit_gate(gate_lower) and len(stmt.targets) > 1:
            result = []
            for target in stmt.targets:
                result.append(IRApply(
                    gate=stmt.gate,
                    params=stmt.params.copy(),
                    targets=[target]
                ))
            return result
        else:
            return [stmt]
    
    def _expand_gate_def(self, stmt: IRGateDef):
        new_body = []
        for s in stmt.body:
            if isinstance(s, IRApply):
                new_body.extend(self._expand_apply(s))
            else:
                new_body.append(s)
        return IRGateDef(
            name=stmt.name,
            params=stmt.params,
            body=new_body
        )