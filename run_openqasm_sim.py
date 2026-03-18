#!/usr/bin/env python3
import sys
from qiskit import transpile
from qiskit_aer import AerSimulator
from qiskit.qasm3 import loads

def run_qasm_file(file_path, shots=1024):

    with open(file_path) as f:
        qasm_code = f.read()

    try:
        qc = loads(qasm_code)
    except Exception as e:
        print(f"Error with {file_path}: {e}")
        return

    simulator = AerSimulator()

    compiled = transpile(qc, simulator)
    job = simulator.run(compiled, shots=shots)

    result = job.result()
    counts = result.get_counts()

    print(f"Result for {file_path}:")
    print(counts)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: run_qasm_sim.py <filename.qasm>")
        sys.exit(1)

    for file_path in sys.argv[1:]:
        run_qasm_file(file_path)