import pytest
from lexer import lexer
from parser import parser
from ir.ir_classes import *
from ir.ir_builder import IRBuilder
from ir.ir_lowering import IRLowering

def compile_to_ir(source):
    ast = parser.parse(source, lexer=lexer)
    ir = IRBuilder().build(ast)
    ir = IRLowering().lower(ir)
    return ir

def test_ir_create():
    ir = compile_to_ir("CREATE QUBITS q[2];")
    stmt = ir.body[0]

    assert isinstance(stmt, IRCreateQubits)
    assert stmt.name == "q"
    assert stmt.size == 2


def test_ir_apply_basic():
    ir = compile_to_ir("CREATE QUBITS q[1]; APPLY H ON q[0];")
    apply = [s for s in ir.body if isinstance(s, IRApply)][0]

    assert apply.gate == "H"
    assert len(apply.targets) == 1
    assert isinstance(apply.targets[0], IRQubit)


def test_ir_apply_params():
    ir = compile_to_ir("CREATE QUBITS q[1]; APPLY RX(3.14) ON q[0];")
    apply = [s for s in ir.body if isinstance(s, IRApply)][0]

    assert isinstance(apply.params[0], IRNumber)
    assert apply.params[0].value == 3.14


def test_ir_multiple_params():
    ir = compile_to_ir("CREATE QUBITS q[1]; APPLY U3(1,2,3) ON q[0];")
    apply = [s for s in ir.body if isinstance(s, IRApply)][0]

    assert len(apply.params) == 3

def test_ir_qubit_index():
    ir = compile_to_ir("CREATE QUBITS q[3]; APPLY H ON q[2];")
    apply = [s for s in ir.body if isinstance(s, IRApply)][0]
    q = apply.targets[0]

    assert q.reg == "q"
    assert q.index == 2


def test_ir_qubit_no_index():
    ir = compile_to_ir("CREATE QUBITS q[3]; APPLY H ON q;")
    apply = [s for s in ir.body if isinstance(s, IRApply)][0]
    q = apply.targets[0]

    assert q.index is None

def test_ir_user_gate_expansion():
    source = """
    CREATE QUBITS q[1];

    GATE MyGate(x) {
        APPLY H ON x;
    }

    APPLY MyGate ON q[0];
    """

    ir = compile_to_ir(source)
    applys = [s for s in ir.body if isinstance(s, IRApply)]

    assert len(applys) == 1
    assert applys[0].gate == "H"


def test_ir_user_gate_targets_substitution():
    source = """
    CREATE QUBITS q[1];

    GATE G(x) {
        APPLY H ON x;
    }

    APPLY G ON q[0];
    """

    ir = compile_to_ir(source)
    apply = [s for s in ir.body if isinstance(s, IRApply)][0]
    q = apply.targets[0]

    assert q.reg == "q"
    assert q.index == 0

def test_ir_multiple_statements():
    source = """
    CREATE QUBITS q[2];
    APPLY H ON q[0];
    APPLY H ON q[1];
    """

    ir = compile_to_ir(source)
    applys = [s for s in ir.body if isinstance(s, IRApply)]

    assert len(applys) == 2

def test_ir_unknown_gate_passthrough():
    source = """
    CREATE QUBITS q[1];
    APPLY FOO ON q[0];
    """

    ir = compile_to_ir(source)
    apply = [s for s in ir.body if isinstance(s, IRApply)][0]

    assert apply.gate == "FOO"

def test_ir_nested_gate():
    source = """
    CREATE QUBITS q[1];

    GATE A(x) {
        APPLY H ON x;
    }

    GATE B(y) {
        APPLY A ON y;
    }

    APPLY B ON q[0];
    """

    ir = compile_to_ir(source)
    applys = [s for s in ir.body if isinstance(s, IRApply)]

    assert len(applys) == 1
    assert applys[0].gate == "H"