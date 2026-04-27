from ir.ir_classes import *
from generators.qiskit_generator import QiskitGenerator
from generators.openqasm_generator import OpenQASMGenerator

def make_simple_ir():
    return IRProgram([
        IRCreateQubits("q", 2),

        IRApply(
            gate="H",
            params=[],
            targets=[IRQubit("q", 0)]
        ),

        IRApply(
            gate="RX",
            params=[IRNumber(3.14)],
            targets=[IRQubit("q", 1)]
        ),

        IRMeasure(
            source=[IRQubit("q", 0), IRQubit("q", 1)]
        )
    ])


def test_qiskit_basic_structure():
    ir = make_simple_ir()
    code = QiskitGenerator().generate(ir)

    assert "QuantumRegister" in code
    assert "ClassicalRegister" in code
    assert "QuantumCircuit" in code


def test_qiskit_h_gate():
    ir = make_simple_ir()
    code = QiskitGenerator().generate(ir)

    assert "qc.h(q[0])" in code or "qc.h(q0)" in code


def test_qiskit_rx_gate_with_param():
    ir = make_simple_ir()
    code = QiskitGenerator().generate(ir)

    assert "qc.rx(3.14, q[1])" in code


def test_qiskit_measure():
    ir = make_simple_ir()
    code = QiskitGenerator().generate(ir)

    assert "measure" in code
    assert "q" in code



def test_qasm_header():
    ir = make_simple_ir()
    code = OpenQASMGenerator().generate(ir)

    assert "OPENQASM 3.0" in code
    assert "stdgates.inc" in code


def test_qasm_qubit_decl():
    ir = make_simple_ir()
    code = OpenQASMGenerator().generate(ir)

    assert "qubit[2] q;" in code


def test_qasm_h_gate():
    ir = make_simple_ir()
    code = OpenQASMGenerator().generate(ir)

    assert "h q[0];" in code


def test_qasm_rx_gate():
    ir = make_simple_ir()
    code = OpenQASMGenerator().generate(ir)

    assert "rx(3.14" in code


def test_qasm_measure():
    ir = make_simple_ir()
    code = OpenQASMGenerator().generate(ir)

    assert "measure" in code

def test_generators_determinism():
    ir = make_simple_ir()

    code1 = QiskitGenerator().generate(ir)
    code2 = QiskitGenerator().generate(ir)

    assert code1 == code2

def test_ir_order_preserved():
    ir = make_simple_ir()
    code = QiskitGenerator().generate(ir)

    i_h = code.index("h")
    i_rx = code.index("rx")

    assert i_h < i_rx


def test_qasm_full_program_shape():
    ir = make_simple_ir()
    code = OpenQASMGenerator().generate(ir)

    assert "qubit" in code
    assert "bit" in code
    assert "measure" in code
    assert "h" in code
    assert "rx" in code

