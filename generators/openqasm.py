from ast_nodes import *
from generators.range_engine import *
from generators.gates import STANDARD_GATES

class OpenQASMTranslator:

    def __init__(self):
        self.lines = []
        self.registers = {}
        self.user_gates = {}

    def translate(self, program):

        self.lines = []
        self.registers = {}
        self.user_gates = {}

        for stmt in program.statements:

            if isinstance(stmt, CreateQubits):
                self.registers[stmt.name] = stmt.size

            elif isinstance(stmt, GateDef):
                self.user_gates[stmt.name] = stmt

        self.lines.append("OPENQASM 3.0;")
        self.lines.append('include "stdgates.inc";')

        for name, size in self.registers.items():
            self.lines.append(f"qubit[{size}] {name};")
            self.lines.append(f"bit[{size}] {name}_c;")

        for stmt in program.statements:

            if isinstance(stmt, ApplyGate):
                self.emit_apply(stmt)

            elif isinstance(stmt, Measure):
                self.emit_measure(stmt)

        return "\n".join(self.lines)

    def emit_apply(self, stmt):

        if stmt.gate.lower() not in STANDARD_GATES and stmt.gate not in self.user_gates:
                raise ValueError(f"Unknown gate: {stmt.gate}")
        
        if stmt.gate in self.user_gates:

            gate = self.user_gates[stmt.gate]

            mapping = dict(zip(gate.params, stmt.targets))

            for op in gate.body:

                resolved = [
                    mapping[q.register] if q.register in mapping else q
                    for q in op.targets
                ]

                self.emit_apply(ApplyGate(op.gate, resolved))

            return

        expanded = expand_targets(self, stmt.targets)

        for group in expanded:

            targets = [f"{reg}[{idx}]" for reg, idx in group]

            args = ", ".join(targets)

            self.lines.append(f"{stmt.gate.lower()} {args};")

    def emit_measure(self, stmt):
        expanded = expand_targets(self, stmt.targets)

        for group in expanded:
            for reg, idx in group:
                self.lines.append(
                    f"{reg}_c[{idx}] = measure {reg}[{idx}];"
                )