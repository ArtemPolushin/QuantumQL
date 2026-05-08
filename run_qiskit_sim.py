#!/usr/bin/env python3
import sys
import argparse
import importlib.util
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

def run_qiskit_file(file_path, shots=1024, cli_params=None):
    
    spec = importlib.util.spec_from_file_location("generated_circuit", file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    if not hasattr(module, "qc"):
        print(f"File {file_path} doesn't contain QuantumCircuit 'qc'.")
        return
    
    qc = module.qc
    if not isinstance(qc, QuantumCircuit):
        print(f"'qc' in {file_path} isn't QuantumCircuit.")
        return
    
    if qc.parameters:
        param_list = list(qc.parameters)
        param_names = [p.name for p in param_list]
        print(f"Circuit has parameters: {', '.join(param_names)}")
        
        bind_dict = {}
        for p in param_list:
            if cli_params and p.name in cli_params:
                bind_dict[p] = cli_params[p.name]
            else:
                value = float(input(f"Enter value for '{p.name}': "))
                bind_dict[p] = value
        qc = qc.assign_parameters(bind_dict)

    simulator = AerSimulator()

    compiled = transpile(qc, simulator)
    job = simulator.run(compiled, shots=shots)

    result = job.result()
    counts = result.get_counts()

    print(f"Result for {file_path}:")
    print(counts)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run generated Qiskit circuit on Aer simulator"
    )
    parser.add_argument(
        "files", nargs="+", 
        help="Python file(s) with generated circuit"
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
        run_qiskit_file(file_path, shots=args.shots, cli_params=cli_params)