#!/usr/bin/env python3
import sys
import importlib.util
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

def run_qiskit_file(file_path, shots=1024):
    
    spec = importlib.util.spec_from_file_location("generated_circuit", file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    if not hasattr(module, "qc"):
        print(f"File {file_path} doesn't contain QuantumCircuit with name 'qc'.")
        return
    
    qc = module.qc

    if not isinstance(qc, QuantumCircuit):
        print(f"'qc' in {file_path} isn't QuantumCircuit.")
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
        print("Usage: run_qiskit_sim.py <file1.py> [file2.py ...]")
        sys.exit(1)
    
    for file_path in sys.argv[1:]:
        run_qiskit_file(file_path)