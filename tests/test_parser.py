import pytest
from lexer import lexer
from parser import parser
from ast_nodes import *

def parse(data):
    return parser.parse(data, lexer=lexer)

def test_create():
    ast = parse("create qubits q[3];")
    assert isinstance(ast.statements[0], CreateQubits)
    assert ast.statements[0].name == "q"
    assert ast.statements[0].size == 3

def test_apply():
    ast = parse("apply H on q[0];")
    assert isinstance(ast.statements[0], ApplyGate)
    assert ast.statements[0].gate == "H"

def test_measure():
    ast = parse("measure q[0], q[1];")
    assert isinstance(ast.statements[0], Measure)
    assert len(ast.statements[0].targets) == 2

def test_select():
    ast = parse("APPLY H ON reg WHERE value < 5;")
    
    apply = ast.statements[0]
    qubit = apply.targets[0]

    assert isinstance(qubit.index, SelectQuery)
    assert qubit.index.condition == ('COND', 'value', '<', 5)

def test_gate_def():
    code = """
    gate MyGate(a, b) {
        apply H on a;
    }
    """
    ast = parse(code)
    stmt = ast.statements[0]
    assert isinstance(stmt, GateDef)
    assert stmt.name == "MyGate"
    assert stmt.params == ["a", "b"]

def test_syntax_error():
    with pytest.raises(SyntaxError):
        parse("create qubits q[3]")

def test_unexpected_end():
    with pytest.raises(SyntaxError):
        parse("apply H on")

def test_syntax_error_on_token():
    bad_code = "create qubits q[3] @"
    with pytest.raises(SyntaxError) as exc_info:
        parse(bad_code + ";")
    
    msg = str(exc_info.value)
    assert "@" in msg
    assert "line" in msg

def test_syntax_error_end_of_input():
    incomplete_code = "apply H on"
    with pytest.raises(SyntaxError) as exc_info:
        parse(incomplete_code + " ")

    msg = str(exc_info.value)
    assert "Unexpected end of input" in msg

def test_parse_create():
    code = "CREATE QUBITS q[2];"
    ast = parser.parse(code)

    assert ast is not None
    assert len(ast.statements) == 1


def test_parse_apply():
    code = """
    CREATE QUBITS q[2];
    APPLY H ON q[0];
    """

    ast = parser.parse(code)

    assert len(ast.statements) == 2


def test_parse_measure():
    code = """
    CREATE QUBITS q[2];
    MEASURE q[0];
    """

    ast = parser.parse(code)
    assert ast is not None