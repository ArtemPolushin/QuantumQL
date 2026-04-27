from ir.ir_classes import *
from gates import normalize_gate_name
import math


class OpenQASMGenerator:
    def __init__(self):
        self.lines = []

    def emit(self, s: str):
        self.lines.append(s)

    def generate(self, ir: IRProgram):
        self.emit("OPENQASM 3.0;")
        self.emit('include "stdgates.inc";')
        
        has_inputs = False
        for stmt in ir.body:
            if isinstance(stmt, IRInputParam):
                self.emit(f"input float {stmt.name};")
                has_inputs = True
        
        if has_inputs:
            self.emit("")
        
        qubits = {}
        bits = {}

        for stmt in ir.body:
            if isinstance(stmt, IRCreateQubits):
                qubits[stmt.name] = stmt.size
                bits[stmt.name] = stmt.size
                self.emit(f"qubit[{stmt.size}] {stmt.name};")
                self.emit(f"bit[{stmt.size}] {stmt.name}_c;")

        self.emit("")

        for stmt in ir.body:
            if isinstance(stmt, IRApply):
                self._apply(stmt)
            elif isinstance(stmt, IRMeasure):
                self._measure(stmt)

        return "\n".join(self.lines)

    def _eval_param(self, p: IRExpr):
        if isinstance(p, IRNumber):
            return p.value
        if isinstance(p, IRConst):
            if p.name == 'pi':
                return math.pi
            raise ValueError(f"Unknown constant: {p.name}")
        if isinstance(p, IRVar):
            return p.name
        raise ValueError(f"Unexpected expression in generator: {type(p)}")

    def _apply(self, stmt: IRApply):
        gate = normalize_gate_name(stmt.gate)

        params = []
        for p in stmt.params:
            val = self._eval_param(p)
            if isinstance(val, float):
                params.append(f"{val:.10f}".rstrip('0').rstrip('.'))
            else:
                params.append(str(val))

        targets = [self._q(t) for t in stmt.targets]
        
        if params:
            self.emit(f"{gate}({', '.join(params)}) {', '.join(targets)};")
        else:
            self.emit(f"{gate} {', '.join(targets)};")

    def _measure(self, stmt: IRMeasure):
        for i, q in enumerate(stmt.source):
            qstr = self._q(q)
            
            if stmt.target and i < len(stmt.target):
                cstr = self._q(stmt.target[i])
            else:
                cstr = qstr.split("[")[0] + "_c" if "[" in qstr else qstr + "_c"
            
            self.emit(f"measure {qstr} -> {cstr};")
    def _q(self, q: IRQubit):
        if q.index is None:
            return q.reg
        return f"{q.reg}[{q.index}]"