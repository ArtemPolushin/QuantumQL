import subprocess
import sys
import os
import pytest

CLI_SCRIPT = "cli.py"

def run_cli(args):
    result = subprocess.run(
        [sys.executable, CLI_SCRIPT] + args,
        capture_output=True,
        text=True
    )
    return result.returncode, result.stdout, result.stderr

def test_cli_qiskit(tmp_path):
    input_file = tmp_path / "program.qql"
    output_file = tmp_path / "output.py"

    input_file.write_text("""
    CREATE QUBITS q[2];
    APPLY H ON q[0];
    APPLY CX ON q[0], q[1];
    """)

    returncode, stdout, stderr = run_cli([
        str(input_file), "qiskit", str(output_file)
    ])

    assert returncode == 0, f"CLI failed with stderr: {stderr}"
    assert output_file.exists()
    
    code = output_file.read_text()
    assert "from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister" in code
    assert 'q = QuantumRegister(2, "q")' in code
    assert "qc.h(q[0])" in code
    assert "qc.cx(q[0], q[1])" in code
    assert "Success" in stdout


def test_cli_openqasm(tmp_path):
    input_file = tmp_path / "program.qql"
    output_file = tmp_path / "output.qasm"

    input_file.write_text("""
    CREATE QUBITS q[2];
    APPLY H ON q[0];
    APPLY CX ON q[0], q[1];
    MEASURE q;
    """)

    returncode, stdout, stderr = run_cli([
        str(input_file), "openqasm", str(output_file)
    ])

    assert returncode == 0, f"CLI failed with stderr: {stderr}"
    assert output_file.exists()
    
    code = output_file.read_text()
    assert "OPENQASM 3.0;" in code
    assert 'include "stdgates.inc";' in code
    assert "qubit[2] q;" in code
    assert "bit[2] q_c;" in code
    assert "h q[0];" in code
    assert "cx q[0], q[1];" in code
    assert "measure" in code
    assert "Success" in stdout


def test_cli_with_params(tmp_path):
    input_file = tmp_path / "program.qql"
    output_file = tmp_path / "output.py"

    input_file.write_text("""
    CREATE QUBITS q[2];
    APPLY RX(3.14) ON q[0];
    APPLY RZ(1.57) ON q[1];
    """)

    returncode, stdout, stderr = run_cli([
        str(input_file), "qiskit", str(output_file)
    ])

    assert returncode == 0, f"CLI failed with stderr: {stderr}"
    assert output_file.exists()
    
    code = output_file.read_text()
    assert "qc.rx(3.14, q[0])" in code
    assert "qc.rz(1.57, q[1])" in code


def test_cli_with_expressions(tmp_path):
    input_file = tmp_path / "program.qql"
    output_file = tmp_path / "output.py"

    input_file.write_text("""
    CREATE QUBITS q[2];
    APPLY RX(pi/2) ON q[0];
    """)

    returncode, stdout, stderr = run_cli([
        str(input_file), "qiskit", str(output_file)
    ])

    assert returncode == 0, f"CLI failed with stderr: {stderr}"
    assert output_file.exists()
    
    code = output_file.read_text()
    assert "1.5707" in code


def test_cli_with_select(tmp_path):
    input_file = tmp_path / "program.qql"
    output_file = tmp_path / "output.py"

    input_file.write_text("""
    CREATE QUBITS q[5];
    SELECT even FROM q WHERE index % 2 == 0;
    APPLY H ON even;
    """)

    returncode, stdout, stderr = run_cli([
        str(input_file), "qiskit", str(output_file)
    ])

    assert returncode == 0, f"CLI failed with stderr: {stderr}"
    assert output_file.exists()
    
    code = output_file.read_text()
    assert "qc.h(q[0])" in code
    assert "qc.h(q[2])" in code
    assert "qc.h(q[4])" in code


def test_cli_with_gate_definition(tmp_path):
    input_file = tmp_path / "program.qql"
    output_file = tmp_path / "output.py"

    input_file.write_text("""
    GATE BELL(a, b) {
        APPLY H ON a;
        APPLY CX ON a, b;
    }
    CREATE QUBITS q[2];
    APPLY BELL ON q[0], q[1];
    """)

    returncode, stdout, stderr = run_cli([
        str(input_file), "qiskit", str(output_file)
    ])

    assert returncode == 0, f"CLI failed with stderr: {stderr}"
    assert output_file.exists()
    
    code = output_file.read_text()
    assert "qc.h(q[0])" in code
    assert "qc.cx(q[0], q[1])" in code


def test_cli_syntax_error(tmp_path):
    input_file = tmp_path / "program.qql"
    output_file = tmp_path / "output.py"

    input_file.write_text("""
    CREATE QUBITS q[2]
    APPLY H ON q[0];
    """)

    returncode, stdout, stderr = run_cli([
        str(input_file), "qiskit", str(output_file)
    ])

    assert returncode != 0
    assert "Syntax error" in stderr or "syntax" in stderr.lower()
    assert not output_file.exists() or output_file.stat().st_size == 0


def test_cli_file_not_found(tmp_path):
    input_file = tmp_path / "nonexistent.qql"
    output_file = tmp_path / "output.py"

    returncode, stdout, stderr = run_cli([
        str(input_file), "qiskit", str(output_file)
    ])

    assert returncode != 0
    assert "not found" in stderr.lower() or "no such file" in stderr.lower()


def test_cli_unknown_gate_error(tmp_path):
    input_file = tmp_path / "program.qql"
    output_file = tmp_path / "output.py"

    input_file.write_text("""
    CREATE QUBITS q[1];
    APPLY UNKNOWN_GATE ON q[0];
    """)

    returncode, stdout, stderr = run_cli([
        str(input_file), "qiskit", str(output_file)
    ])

    assert returncode != 0
    assert "Unknown gate" in stderr or "Generator error" in stderr or "IR error" in stderr
    assert not output_file.exists() or output_file.stat().st_size == 0


def test_cli_wrong_qubit_count_error(tmp_path):
    input_file = tmp_path / "program.qql"
    output_file = tmp_path / "output.py"

    input_file.write_text("""
    CREATE QUBITS q[2];
    APPLY CX ON q[0];  -- CX требует 2 кубита
    """)

    returncode, stdout, stderr = run_cli([
        str(input_file), "qiskit", str(output_file)
    ])

    assert returncode != 0
    assert "expects" in stderr.lower() or "qubit" in stderr.lower()


def test_cli_unsupported_target(tmp_path):
    input_file = tmp_path / "program.qql"
    output_file = tmp_path / "output.txt"

    input_file.write_text("CREATE QUBITS q[1];")

    returncode, stdout, stderr = run_cli([
        str(input_file), "invalid_target", str(output_file)
    ])

    assert returncode != 0
    assert "Unsupported target" in stderr or "target" in stderr.lower()


def test_cli_missing_arguments():
    returncode, stdout, stderr = run_cli([])

    assert returncode != 0
    assert "Usage" in stderr or "usage" in stderr.lower()

def test_cli_complex_program(tmp_path):
    input_file = tmp_path / "program.qql"
    output_file = tmp_path / "output.py"

    input_file.write_text("""
    CREATE QUBITS a[3];
    CREATE QUBITS b[3];
    
    GATE SWAP_LIKE(x, y) {
        APPLY CX ON x, y;
        APPLY CX ON y, x;
        APPLY CX ON x, y;
    }
    
    APPLY H ON a[0:2];
    APPLY SWAP_LIKE ON a[0], b[0];
    APPLY RX(pi/4) ON a[1];
    MEASURE a;
    """)

    returncode, stdout, stderr = run_cli([
        str(input_file), "qiskit", str(output_file)
    ])

    assert returncode == 0, f"CLI failed with stderr: {stderr}"
    assert output_file.exists()
    
    code = output_file.read_text()
    assert "QuantumRegister(3, \"a\")" in code
    assert "QuantumRegister(3, \"b\")" in code
    assert "qc.h(a[0])" in code
    assert "qc.h(a[1])" in code
    assert "qc.h(a[2])" in code
    assert "qc.measure" in code
    assert "Success" in stdout

def test_cli_success_message(tmp_path):
    input_file = tmp_path / "program.qql"
    output_file = tmp_path / "output.py"

    input_file.write_text("CREATE QUBITS q[1];")

    returncode, stdout, stderr = run_cli([
        str(input_file), "qiskit", str(output_file)
    ])

    assert returncode == 0
    assert "Success" in stdout
    assert str(output_file) in stdout

def test_cli_with_select(tmp_path):
    input_file = tmp_path / "program.qql"
    output_file = tmp_path / "output.py"

    input_file.write_text("""
    CREATE QUBITS q[6];
    SELECT even FROM q WHERE index % 2 == 0;
    SELECT odd FROM q WHERE index % 2 == 1;
    APPLY H ON even;
    APPLY X ON odd;
    MEASURE q;
    """)

    returncode, stdout, stderr = run_cli([
        str(input_file), "qiskit", str(output_file)
    ])

    assert returncode == 0, f"CLI failed with stderr: {stderr}"
    assert output_file.exists()
    
    code = output_file.read_text()
    
    assert "qc.h(q[0])" in code
    assert "qc.h(q[2])" in code
    assert "qc.h(q[4])" in code
    
    assert "qc.x(q[1])" in code
    assert "qc.x(q[3])" in code
    assert "qc.x(q[5])" in code
    
    assert "qc.measure(q, q_c)" in code


def test_cli_with_inline_select(tmp_path):
    input_file = tmp_path / "program.qql"
    output_file = tmp_path / "output.py"

    input_file.write_text("""
    CREATE QUBITS q[5];
    APPLY H ON SELECT qbit FROM q WHERE index < 3;
    """)

    returncode, stdout, stderr = run_cli([
        str(input_file), "qiskit", str(output_file)
    ])

    assert returncode == 0, f"CLI failed with stderr: {stderr}"
    assert output_file.exists()
    
    code = output_file.read_text()
    
    assert "qc.h(q[0])" in code
    assert "qc.h(q[1])" in code
    assert "qc.h(q[2])" in code
    assert "qc.h(q[3])" not in code
    assert "qc.h(q[4])" not in code