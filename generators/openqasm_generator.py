from ir.ir_classes import *
from gates import normalize_gate_name
import math


class OpenQASMGenerator:
    def __init__(self):
        self.lines = []
        self.input_params = []

    def emit(self, s: str):
        self.lines.append(s)

    def generate(self, ir: IRProgram):
        self.input_params = [s.name for s in ir.body if isinstance(s, IRInputParam)]
        
        self.emit("OPENQASM 3.0;")
        self.emit('include "stdgates.inc";')
        
        if self.input_params:
            self.emit("")
            for p in self.input_params:
                self.emit(f"input float {p};")
        
        qubits = {}
        bits = {}
        
        for stmt in ir.body:
            if isinstance(stmt, IRCreateQubits):
                qubits[stmt.name] = stmt.size
                bits[f"{stmt.name}_c"] = stmt.size
            elif isinstance(stmt, IRCreateBits):
                bits[stmt.name] = stmt.size
        
        for name, size in qubits.items():
            self.emit(f"qubit[{size}] {name};")
        
        for name, size in bits.items():
            self.emit(f"bit[{size}] {name};")
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
            if p.name == 'e':
                return math.e
            if p.name == 'tau':
                return math.tau
            raise ValueError(f"Unknown constant: {p.name}")
        if isinstance(p, IRVar):
            return p.name
        if isinstance(p, IRBinOp):
            left = self._eval_param(p.left)
            right = self._eval_param(p.right)
            return f"({left} {p.op} {right})"
        if isinstance(p, IRUnaryOp):
            inner = self._eval_param(p.expr)
            return f"({p.op}{inner})"
        if isinstance(p, IRFuncCall):
            args = [self._eval_param(a) for a in p.args]
            return f"{p.name}({', '.join(args)})"
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