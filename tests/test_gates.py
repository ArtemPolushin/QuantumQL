import pytest
from ast_nodes import *
from generators.qiskit import QiskitTranslator
from generators.openqasm import OpenQASMTranslator

def test_known_gates_qiskit():
    program = Program([CreateQubits("q", 1)])
    translator = QiskitTranslator()
    for gate in ["h", "x", "y", "z", "s", "sdg", "t", "tdg", "cx", "cz", "swap"]:
        program.statements.append(ApplyGate(gate.upper(), [QubitRef("q", 0)]))
        code = translator.translate(program)
        assert any(gate.lower() in line for line in code.splitlines())

def test_unknown_gate_qiskit():
    program = Program([CreateQubits("q", 1), ApplyGate("FOO", [QubitRef("q", 0)])])
    translator = QiskitTranslator()
    with pytest.raises(ValueError, match="Unknown gate"):
        translator.translate(program)

def test_known_gates_openqasm():
    program = Program([CreateQubits("q", 1)])
    translator = OpenQASMTranslator()
    for gate in ["h", "x", "y", "z", "s", "sdg", "t", "tdg", "cx", "cz", "swap"]:
        program.statements.append(ApplyGate(gate.upper(), [QubitRef("q", 0)]))
        code = translator.translate(program)
        assert any(gate.lower() in line for line in code.splitlines())

def test_unknown_gate_openqasm():
    program = Program([CreateQubits("q", 1), ApplyGate("FOO", [QubitRef("q", 0)])])
    translator = OpenQASMTranslator()
    with pytest.raises(ValueError, match="Unknown gate"):
        translator.translate(program)