#!/usr/bin/env python3

import sys
import argparse
from parser import parser
from lexer import lexer
from ir.ir_pipeline import IRPipeline
from generators.qiskit_generator import QiskitGenerator
from generators.openqasm_generator import OpenQASMGenerator

def main():
    arg_parser = argparse.ArgumentParser(
        description="QuantumQL compiler — generates Qiskit or OpenQASM 3.0 code"
    )
    arg_parser.add_argument("input", help="Input .ql file")
    arg_parser.add_argument("target", choices=["qiskit", "openqasm"],
                           help="Target language")
    arg_parser.add_argument("output", help="Output file")
    
    args = arg_parser.parse_args()

    try:
        with open(args.input) as f:
            code = f.read()
    except FileNotFoundError:
        print(f"File {args.input} not found", file=sys.stderr)
        sys.exit(1)

    try:
        ast = parser.parse(code, lexer=lexer)
    except SyntaxError as e:
        print(f"Syntax error: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        pipeline = IRPipeline()
        ir = pipeline.run(ast)
    except Exception as e:
        print(f"IR error: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        if args.target == "qiskit":
            generator = QiskitGenerator()
        else:
            generator = OpenQASMGenerator()

        output_code = generator.generate(ir)
    except Exception as e:
        print(f"Generator error: {e}", file=sys.stderr)
        sys.exit(1)
        
    try:
        with open(args.output, "w") as f:
            f.write(output_code)
    except (PermissionError, IOError) as e:
        print(f"Cannot write to {args.output}: {e}", file=sys.stderr)
        sys.exit(1)
    
    print(f"Success, file {args.output} created")

if __name__ == "__main__":
    main()