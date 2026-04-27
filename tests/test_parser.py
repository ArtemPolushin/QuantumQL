import pytest
from lexer import lexer
from parser import parser
from ast_nodes import *

def parse(data):
    return parser.parse(data, lexer=lexer)

def test_create_basic():
    ast = parse("CREATE QUBITS q[3];")

    stmt = ast.statements[0]
    assert isinstance(stmt, CreateQubits)
    assert stmt.name == "q"
    assert stmt.size == 3

def test_apply_simple():
    ast = parse("APPLY H ON q[0];")

    stmt = ast.statements[0]
    assert isinstance(stmt, ApplyGate)
    assert stmt.gate == "H"
    assert len(stmt.targets) == 1


def test_apply_multiple_targets():
    ast = parse("APPLY CX ON q[0], q[1];")

    stmt = ast.statements[0]
    assert len(stmt.targets) == 2

def test_apply_with_params():
    ast = parse("APPLY RX(3.14) ON q[0];")

    stmt = ast.statements[0]
    assert stmt.gate == "RX"
    assert len(stmt.params) == 1
    assert isinstance(stmt.params[0], Number)
    assert stmt.params[0].value == 3.14
    assert len(stmt.targets) == 1
    assert stmt.targets[0].register == "q"
    assert stmt.targets[0].index == 0


def test_apply_with_multiple_params():
    ast = parse("APPLY U3(1, 2, 3) ON q[0];")

    stmt = ast.statements[0]
    assert stmt.gate == "U3"
    assert len(stmt.params) == 3
    assert all(isinstance(p, Number) for p in stmt.params)
    assert [p.value for p in stmt.params] == [1, 2, 3]

def test_qubit_no_index():
    ast = parse("APPLY H ON q;")

    q = ast.statements[0].targets[0]
    assert isinstance(q, QubitRef)
    assert q.index is None

def test_qubit_index():
    ast = parse("APPLY H ON q[2];")

    q = ast.statements[0].targets[0]
    assert q.index == 2

def test_qubit_star():
    ast = parse("APPLY H ON q[*];")

    q = ast.statements[0].targets[0]
    assert q.index == "*"

def test_qubit_range():
    ast = parse("APPLY H ON q[0:3];")

    q = ast.statements[0].targets[0]
    assert q.index == (0, 3)

def test_measure_basic():
    ast = parse("MEASURE q[0];")

    stmt = ast.statements[0]
    assert isinstance(stmt, Measure)
    assert len(stmt.targets) == 1


def test_measure_multiple():
    ast = parse("MEASURE q[0], q[1];")

    stmt = ast.statements[0]
    assert isinstance(ast.statements[0], Measure)
    assert len(stmt.targets) == 2

def test_gate_def_basic():
    code = """
    GATE MyGate(a) {
        APPLY H ON a;
    }
    """
    ast = parse(code)

    stmt = ast.statements[0]
    assert isinstance(stmt, GateDef)
    assert stmt.name == "MyGate"
    assert stmt.params == ["a"]
    assert len(stmt.body) == 1


def test_gate_def_multiple_params():
    code = """
    GATE G(a, b, c) {
        APPLY H ON a;
    }
    """

    stmt = parse(code).statements[0]
    assert stmt.params == ["a", "b", "c"]


def test_gate_with_apply_inside():
    code = """
    GATE G(a) {
        APPLY RX(3.14) ON a;
    }
    """

    stmt = parse(code).statements[0]
    assert isinstance(stmt, GateDef)
    assert stmt.name == "G"
    assert stmt.params == ["a"]
    
    inner = stmt.body[0]
    assert isinstance(inner, ApplyGate)
    assert inner.gate == "RX"
    assert len(inner.params) == 1
    assert isinstance(inner.params[0], Number)
    assert inner.params[0].value == 3.14
    assert len(inner.targets) == 1
    assert inner.targets[0].register == "a"
    assert inner.targets[0].index is None

def test_missing_semicolon():
    with pytest.raises(SyntaxError):
        parse("CREATE QUBITS q[2]")


def test_invalid_token():
    with pytest.raises(SyntaxError):
        parse("CREATE QUBITS q[2]; @")


def test_unexpected_eof():
    with pytest.raises(SyntaxError):
        parse("APPLY H ON")


def test_broken_apply():
    with pytest.raises(SyntaxError):
        parse("APPLY ON q[0];")


def test_broken_gate():
    with pytest.raises(SyntaxError):
        parse("GATE G(a) APPLY H ON a;")

def test_multiple_statements():
    code = """
    CREATE QUBITS q[2];
    APPLY H ON q[0];
    MEASURE q[0];
    """

    ast = parse(code)
    assert len(ast.statements) == 3

def test_apply_with_expression_params():
    ast = parse("APPLY RX(pi/2) ON q[0];")
    
    stmt = ast.statements[0]
    assert stmt.gate == "RX"
    assert len(stmt.params) == 1
    assert isinstance(stmt.params[0], BinOp)
    assert isinstance(stmt.params[0].left, Constant)
    assert stmt.params[0].left.name == "pi"
    assert stmt.params[0].op == "/"
    assert isinstance(stmt.params[0].right, Number)
    assert stmt.params[0].right.value == 2

def test_select_statement():
    code = "SELECT even FROM a WHERE index % 2 == 0;"
    ast = parse(code)
    
    stmt = ast.statements[0]
    assert isinstance(stmt, SelectStmt)
    assert stmt.alias == "even"
    assert stmt.source == "a"
    assert isinstance(stmt.condition, BinOp)
    assert stmt.condition.op == "=="

def test_apply_with_select_target():
    code = "APPLY H ON SELECT q FROM b WHERE index < 3;"
    ast = parse(code)
    
    stmt = ast.statements[0]
    assert isinstance(stmt, ApplyGate)
    assert stmt.gate == "H"
    assert len(stmt.targets) == 1
    assert isinstance(stmt.targets[0], SelectExpr)
    assert stmt.targets[0].alias == "q"
    assert stmt.targets[0].source == "b"
    assert isinstance(stmt.targets[0].condition, BinOp)
    assert stmt.targets[0].condition.op == "<"