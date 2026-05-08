#!/usr/bin/env python3
import sys
import argparse
import re
from qiskit import transpile
from qiskit_aer import AerSimulator
from qiskit.qasm3 import loads

def run_qasm_file(file_path, shots=1024, cli_params=None):

    with open(file_path) as f:
        qasm_code = f.read()

    input_params = re.findall(r'input\s+float\s+(\w+)\s*;', qasm_code)
    
    param_values = {}
    if input_params:
        for name in input_params:
            if cli_params and name in cli_params:
                param_values[name] = cli_params[name]
            else:
                value = float(input(f"Enter value for '{name}': "))
                param_values[name] = value
        
        qasm_code = re.sub(r'input\s+float\s+\w+\s*;\s*\n?', '', qasm_code)
        
        for name, value in param_values.items():
            qasm_code = re.sub(
                rf'(?<![a-zA-Z0-9_]){re.escape(name)}(?![a-zA-Z0-9_])',
                str(value),
                qasm_code
            )

    try:
        qc = loads(qasm_code)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return

    simulator = AerSimulator()

    compiled = transpile(qc, simulator)
    job = simulator.run(compiled, shots=shots)

    result = job.result()
    counts = result.get_counts()

    print(f"Result for {file_path}:")
    print(counts)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run OpenQASM 3.0 circuit on Aer simulator"
    )
    parser.add_argument(
        "files", nargs="+",
        help="OpenQASM file(s) to run"
    )
    parser.add_argument(
        "--shots", type=int, default=1024,
        help="Number of shots (default: 1024)"
    )
    parser.add_argument(
        "--params", nargs="*", default=[],
        help="Circuit parameters in format name=value (e.g. --params theta=3.14)"
    )
    
    args = parser.parse_args()
    cli_params = {}
    for p in args.params:
        try:
            name, value = p.split("=", 1)
            cli_params[name.strip()] = float(value)
        except ValueError:
            print(f"Error: invalid parameter format '{p}'. Use name=value")
            sys.exit(1)
    
    for file_path in args.files:
        run_qasm_file(file_path, shots=args.shots, cli_params=cli_params)