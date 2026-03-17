import pytest
from ast_nodes import *
from generators.openqasm import OpenQASMTranslator


def parse_dummy(program):
    return program

def test_create_qubits():
    program = Program([CreateQubits("q", 3)])
    translator = OpenQASMTranslator()
    code = translator.translate(program)

    assert "qubit[3] q;" in code
    assert "bit[3] q_c;" in code

def test_apply_single():
    program = Program([
        CreateQubits("q", 2),
        ApplyGate("H", [QubitRef("q", 0)])
    ])

    translator = OpenQASMTranslator()
    code = translator.translate(program)

    assert "h q[0];" in code

def test_apply_range():
    program = Program([
        CreateQubits("q", 3),
        ApplyGate("X", [QubitRef("q", (0,2))])
    ])

    translator = OpenQASMTranslator()
    code = translator.translate(program)

    for i in range(3):
        assert f"x q[{i}];" in code

def test_apply_star():
    program = Program([
        CreateQubits("q", 3),
        ApplyGate("Y", [QubitRef("q", "*")])
    ])

    translator = OpenQASMTranslator()
    code = translator.translate(program)

    for i in range(3):
        assert f"y q[{i}];" in code
        
def test_select_translation():
    program = Program([
        CreateQubits("a", 5),
        ApplyGate(
            "H",
            [
                QubitRef(
                    "a",
                    SelectQuery("a", ('COND', 'value', '<', 3))
                )
            ]
        )
    ])

    translator = OpenQASMTranslator()
    code = translator.translate(program)

    assert "h a[0];" in code
    assert "h a[1];" in code
    assert "h a[2];" in code

def test_vector_select():
    program = Program([
        CreateQubits("a", 5),
        CreateQubits("b", 5),
        ApplyGate(
            "CX",
            [
                QubitRef(
                    "a",
                    SelectQuery("a", ('COND', 'value', '<', 3))
                ),
                QubitRef("b", (0, 2))
            ]
        )
    ])

    translator = OpenQASMTranslator()
    code = translator.translate(program)

    assert "cx a[0], b[0];" in code
    assert "cx a[1], b[1];" in code
    assert "cx a[2], b[2];" in code

def test_measure():
    program = Program([
        CreateQubits("q", 2),
        Measure([QubitRef("q", 0), QubitRef("q", 1)])
    ])

    translator = OpenQASMTranslator()
    code = translator.translate(program)

    assert "q_c[0] = measure q[0];" in code
    assert "q_c[1] = measure q[1];" in code

def test_user_gate():

    body = [
        ApplyGate("H", [QubitRef("a", 0)])
    ]

    gate_def = GateDef("MyGate", ["a"], body)

    program = Program([
        CreateQubits("a", 1),
        gate_def,
        ApplyGate("MyGate", [QubitRef("a", 0)])
    ])

    translator = OpenQASMTranslator()

    code = translator.translate(program)

    assert "h a[0];" in code