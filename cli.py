#!/usr/bin/env python3

import sys
from parser import parser
from lexer import lexer
from ir.ir_pipeline import IRPipeline
from generators.qiskit_generator import QiskitGenerator
from generators.openqasm_generator import OpenQASMGenerator

def main():
    if len(sys.argv) != 4:
        print("Usage: cli.py <input> <qiskit|openqasm> <output>", file=sys.stderr)
        sys.exit(1)

    infile, target, outfile = sys.argv[1], sys.argv[2], sys.argv[3]

    try:
        with open(infile) as f:
            code = f.read()
    except FileNotFoundError:
        print(f"File {infile} not found", file=sys.stderr)
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
        if target.lower() == "qiskit":
            generator = QiskitGenerator()
        elif target.lower() == "openqasm":
            generator = OpenQASMGenerator()
        else:
            print(f"Unsupported target language: {target}", file=sys.stderr)
            sys.exit(1)

        output_code = generator.generate(ir)

    except Exception as e:
        print(f"Generator error: {e}", file=sys.stderr)
        sys.exit(1)

    with open(outfile, "w") as f:
        f.write(output_code)

    print(f"Success, file {outfile} created")
    sys.exit(0)

if __name__ == "__main__":
    main()