import pytest
from lexer import lexer
from parser import parser
from generators.qiskit import QiskitTranslator

def translate_qiskit(source_code):
    ast = parser.parse(source_code, lexer=lexer)
    return QiskitTranslator().translate(ast)

def test_basic_apply():
    code = """
    CREATE QUBITS q[2];
    APPLY H ON q[0];
    APPLY CX ON q[0], q[1];
    """
    result = translate_qiskit(code)
    assert "q = QuantumRegister(2, \"q\")" in result
    assert "qc.h(q[0])" in result
    assert "qc.cx(q[0], q[1])" in result

def test_range_and_star():
    code = """
    CREATE QUBITS q[3];
    APPLY X ON q[0:2];
    APPLY Y ON q[*];
    """
    result = translate_qiskit(code)
    for i in range(3):
        assert f"qc.x(q[{i}])" in result
        assert f"qc.y(q[{i}])" in result

def test_select_query():
    code = """
    CREATE QUBITS a[5];
    APPLY H ON a WHERE value < 3;
    """
    result = translate_qiskit(code)
    assert "qc.h(a[0])" in result
    assert "qc.h(a[1])" in result
    assert "qc.h(a[2])" in result

def test_vector_select():
    code = """
    CREATE QUBITS a[5];
    CREATE QUBITS b[5];
    APPLY CX ON a WHERE value < 3, b[0:2];
    """
    result = translate_qiskit(code)
    assert "qc.cx(a[0], b[0])" in result
    assert "qc.cx(a[1], b[1])" in result
    assert "qc.cx(a[2], b[2])" in result

def test_measure_basic():
    code = """
    CREATE QUBITS q[2];
    MEASURE q[0], q[1];
    """
    result = translate_qiskit(code)
    assert "qc.measure(q[0], q_c[0])" in result
    assert "qc.measure(q[1], q_c[1])" in result

def test_measure_select():
    code = """
    CREATE QUBITS q[5];
    MEASURE q WHERE value < 3;
    """
    result = translate_qiskit(code)
    for i in range(3):
        assert f"qc.measure(q[{i}], q_c[{i}])" in result

def test_measure_mixed():
    code = """
    CREATE QUBITS a[5];
    CREATE QUBITS b[5];
    MEASURE a WHERE value < 2, b[0:1];
    """
    result = translate_qiskit(code)
    assert "qc.measure(a[0], a_c[0])" in result
    assert "qc.measure(a[1], a_c[1])" in result
    assert "qc.measure(b[0], b_c[0])" in result
    assert "qc.measure(b[1], b_c[1])" in result

def test_user_gate():
    code = """
    CREATE QUBITS q[1];
    GATE MyGate(a) {
        APPLY H ON a[0];
    }
    APPLY MyGate ON q[0];
    """
    result = translate_qiskit(code)
    assert "qc.h(q[0])" in result

def test_unknown_gate():
    code = """
    CREATE QUBITS q[1];
    APPLY FOO ON q[0];
    """
    with pytest.raises(ValueError):
        translate_qiskit(code)

def test_syntax_error():
    code = """
    CREATE QUBITS q[2]
    APPLY H ON q[0]
    """
    with pytest.raises(SyntaxError):
        parser.parse(code, lexer=lexer)