from ir.ir_classes import *
from gates import normalize_gate_name
import math


class QiskitGenerator:
    def __init__(self):
        self.lines = []
        self.indent = ""
        self.has_inputs = False
        self.body_lines = []
        self.input_params = []

    def emit(self, s: str):
        self.lines.append(f"{self.indent}{s}")

    def emit_body(self, s: str):
        self.body_lines.append(f"{self.indent}{s}")

    def generate(self, ir: IRProgram):
        self.input_params = [s.name for s in ir.body if isinstance(s, IRInputParam)]
        
        self.emit("from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister")
        self.emit("from qiskit.circuit import Parameter")
        self.emit("import math")
        self.emit("")
        
        param_map = {}
        for p in self.input_params:
            self.emit_body(f'{p} = Parameter("{p}")')
            param_map[p] = p
        
        if self.input_params:
            self.emit_body("")
        
        regs = {}
        cregs = {}
        for stmt in ir.body:
            if isinstance(stmt, IRCreateQubits):
                regs[stmt.name] = stmt.size
            elif isinstance(stmt, IRCreateBits):
                cregs[stmt.name] = stmt.size

        for name in regs:
            if name not in cregs:
                cregs[f"{name}_c"] = regs[name]
        
        for name, size in regs.items():
            self.emit_body(f'{name} = QuantumRegister({size}, "{name}")')
    
        for name, size in cregs.items():
            self.emit_body(f'{name} = ClassicalRegister({size}, "{name}")')
        
        all_regs = list(regs.keys()) + list(cregs.keys())
        if all_regs:
            qargs = ", ".join(all_regs)
            self.emit_body(f"qc = QuantumCircuit({qargs})")
        else:
            self.emit_body("qc = QuantumCircuit()")

        for stmt in ir.body:
            if isinstance(stmt, IRApply):
                self._apply(stmt)
            elif isinstance(stmt, IRMeasure):
                self._measure(stmt)
        
        self.lines.extend(self.body_lines)
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
            if p.name in self.input_params:
                return p.name
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
            return f"math.{p.name}({', '.join(args)})"
        raise ValueError(f"Unexpected expression in generator: {type(p)}")

    def _apply(self, stmt: IRApply):
        gate = normalize_gate_name(stmt.gate)
        
        args = []
        for p in stmt.params:
            val = self._eval_param(p)
            if isinstance(val, float):
                args.append(f"{val:.10f}".rstrip('0').rstrip('.'))
            else:
                args.append(str(val))
        
        targets = [self._q(t) for t in stmt.targets]
        if args:
            self.emit_body(f"qc.{gate}({', '.join(args + targets)})")
        else:
            self.emit_body(f"qc.{gate}({', '.join(targets)})")
    
    def _measure(self, stmt: IRMeasure):
        for i, q in enumerate(stmt.source):
            q_str = self._q(q)
            
            if stmt.target and i < len(stmt.target):
                c_str = self._q(stmt.target[i])
            else:
                c_str = q_str.replace('[', '_c[') if '[' in q_str else f"{q_str}_c"
            
            self.emit_body(f"qc.measure({q_str}, {c_str})")
    
    def _q(self, q: IRQubit):
        if q.index is None:
            return f"{q.reg}"
        return f"{q.reg}[{q.index}]"