import pytest
from ir.ir_classes import *
from ir.ir_builder import IRBuilder
from lexer import lexer as global_lexer
from parser import parser as global_parser

@pytest.fixture
def lexer():
    return global_lexer

@pytest.fixture
def parser():
    return global_parser

def parse_string(code):
    return global_parser.parse(code, lexer=global_lexer)

def test_parse_and_build_simple(parser, lexer):
    code = """
    CREATE QUBITS q[2];
    APPLY H ON q[0];
    APPLY CX ON q[0], q[1];
    MEASURE q;
    """
    
    ast = parser.parse(code, lexer=lexer)
    builder = IRBuilder()
    ir = builder.build(ast)
    
    assert len(ir.body) == 4
    assert isinstance(ir.body[0], IRCreateQubits)
    assert ir.body[0].name == "q"
    assert ir.body[0].size == 2
    
    assert isinstance(ir.body[1], IRApply)
    assert ir.body[1].gate == "H"
    assert len(ir.body[1].targets) == 1
    assert ir.body[1].targets[0].index == 0
    
    assert isinstance(ir.body[2], IRApply)
    assert ir.body[2].gate == "CX"
    assert len(ir.body[2].targets) == 2
    
    assert isinstance(ir.body[3], IRMeasure)


def test_parse_and_build_with_expressions(parser, lexer):
    code = """
    CREATE QUBITS q[3];
    SELECT even FROM q WHERE index % 2 == 0;
    APPLY RX(pi/2) ON even;
    """
    
    ast = parser.parse(code, lexer=lexer)
    builder = IRBuilder()
    ir = builder.build(ast)
    
    assert len(ir.body) == 3
    assert isinstance(ir.body[0], IRCreateQubits)
    assert isinstance(ir.body[1], IRSelectStmt)
    assert isinstance(ir.body[2], IRApply)
    assert isinstance(ir.body[2].params[0], IRBinOp)


def test_parse_and_build_gate_definition(parser, lexer):
    code = """
    GATE BELL(a, b) {
        APPLY H ON a;
        APPLY CX ON a, b;
    }
    CREATE QUBITS q[2];
    APPLY BELL ON q[0], q[1];
    """
    
    ast = parser.parse(code, lexer=lexer)
    builder = IRBuilder()
    ir = builder.build(ast)
    
    assert len(ir.body) == 3
    assert isinstance(ir.body[0], IRGateDef)
    assert ir.body[0].name == "BELL"
    assert len(ir.body[0].body) == 2
    
    assert isinstance(ir.body[1], IRCreateQubits)
    assert isinstance(ir.body[2], IRApply)
    assert ir.body[2].gate == "BELL"