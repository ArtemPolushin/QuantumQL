from ir.ir_classes import *
from gates import GATES, gate_exists


class IRValidator:
    def __init__(self):
        self.user_gates = set()
    
    def validate(self, ir_program: IRProgram):
        for stmt in ir_program.body:
            if isinstance(stmt, IRGateDef):
                self.user_gates.add(stmt.name.lower())
        
        for stmt in ir_program.body:
            self._validate_stmt(stmt)
        
        return ir_program
    
    def _validate_stmt(self, stmt):
        if isinstance(stmt, IRApply):
            self._validate_apply(stmt)
        elif isinstance(stmt, IRMeasure):
            self._validate_measure(stmt)
        elif isinstance(stmt, IRGateDef):
            for inner_stmt in stmt.body:
                self._validate_stmt(inner_stmt)
    
    def _validate_apply(self, stmt: IRApply):
        gate_lower = stmt.gate.lower()
        
        if not gate_exists(gate_lower) and gate_lower not in self.user_gates:
            raise ValueError(f"Unknown gate: {stmt.gate}")
        
        if gate_lower in GATES:
            gate_info = GATES[gate_lower]
            num_targets = len(stmt.targets)
            
            if gate_info.num_qubits != -1 and num_targets != gate_info.num_qubits:
                raise ValueError(
                    f"Gate '{stmt.gate}' expects {gate_info.num_qubits} qubit(s), "
                    f"but got {num_targets}"
                )
        
        if gate_lower in GATES:
            gate_info = GATES[gate_lower]
            if gate_info.has_params and len(stmt.params) == 0:
                raise ValueError(f"Gate '{stmt.gate}' requires parameters")
            
    def _validate_measure(self, stmt: IRMeasure):
        if stmt.target and len(stmt.source) != len(stmt.target):
            raise ValueError(
                f"Measure source and target count mismatch: "
                f"{len(stmt.source)} sources, {len(stmt.target)} targets"
            )