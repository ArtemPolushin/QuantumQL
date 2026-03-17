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

    input_file.write_text("CREATE QUBITS q[2];\nAPPLY H ON q[0];\n")

    returncode, stdout, stderr = run_cli([str(input_file), "qiskit", str(output_file)])

    assert returncode == 0
    assert os.path.exists(output_file)
    code = output_file.read_text()
    assert "qc.h(q[0])" in code
    assert "q = QuantumRegister(2, \"q\")" in code

def test_cli_openqasm(tmp_path):
    input_file = tmp_path / "program.qql"
    output_file = tmp_path / "output.qasm"

    input_file.write_text("CREATE QUBITS q[2];\nAPPLY H ON q[0];\n")

    returncode, stdout, stderr = run_cli([str(input_file), "openqasm", str(output_file)])

    assert returncode == 0
    assert os.path.exists(output_file)
    code = output_file.read_text()
    assert "h q[0];" in code
    assert "qubit[2] q;" in code

def test_cli_syntax_error(tmp_path):
    input_file = tmp_path / "program.qql"
    output_file = tmp_path / "output.py"

    input_file.write_text("CREATE QUBITS q[2]\nAPPLY H ON q[0]")

    returncode, stdout, stderr = run_cli([str(input_file), "qiskit", str(output_file)])

    assert returncode != 0
    assert "Syntax error" in stderr
    assert not os.path.exists(output_file)

def test_cli_file_not_found(tmp_path):
    input_file = tmp_path / "nonexistent.qql"
    output_file = tmp_path / "output.py"

    returncode, stdout, stderr = run_cli([str(input_file), "qiskit", str(output_file)])

    assert returncode != 0
    assert "not found" in stderr

def test_cli_translation_error(tmp_path):
    input_file = tmp_path / "program.qql"
    output_file = tmp_path / "output.py"

    input_file.write_text("CREATE QUBITS q[1];\nAPPLY UNKNOWN_GATE ON q[0];\n")

    returncode, stdout, stderr = run_cli([str(input_file), "qiskit", str(output_file)])

    assert returncode != 0
    assert "Translation error" in stderr
    assert not os.path.exists(output_file)