#!/usr/bin/env python3

import sys
from parser import parser
from lexer import lexer
from generators.qiskit import QiskitTranslator
from generators.openqasm import OpenQASMTranslator

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
        if target.lower() == "qiskit":
            translator = QiskitTranslator()
        elif target.lower() == "openqasm":
            translator = OpenQASMTranslator()
        else:
            print(f"Unsupported target language: {target}", file=sys.stderr)
            sys.exit(1)

        output_code = translator.translate(ast)

    except Exception as e:
        print(f"Translation error: {e}", file=sys.stderr)
        sys.exit(1)

    with open(outfile, "w") as f:
        f.write(output_code)

    print(f"Success, file {outfile} created")
    sys.exit(0)

if __name__ == "__main__":
    main()