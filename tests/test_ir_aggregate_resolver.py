import pytest
from lexer import lexer
from parser import parser
from ir.ir_classes import *
from ir.ir_pipeline import IRPipeline


def get_all_targets_from_applies(ir_body, gate_name=None):
    targets = []
    for stmt in ir_body:
        if isinstance(stmt, IRApply):
            if gate_name is None or stmt.gate.lower() == gate_name.lower():
                targets.extend(stmt.targets)
    return targets

def test_aggregate_alias():
    code = """
    create qubits q[4];
    select even from q where index % 2 == 0;
    apply h on all from even;
    measure q;
    """
    ast = parser.parse(code, lexer=lexer)
    pipeline = IRPipeline()
    ir = pipeline.run(ast)
    
    all_targets = get_all_targets_from_applies(ir.body, 'h')
    assert len(all_targets) == 2
    assert IRQubit("q", 0) in all_targets
    assert IRQubit("q", 2) in all_targets


def test_aggregate_alias_used_twice():
    code = """
    create qubits q[6];
    select first_half from q where index < 3;
    apply h on all from first_half;
    apply x on all from first_half;
    """
    ast = parser.parse(code, lexer=lexer)
    pipeline = IRPipeline()
    ir = pipeline.run(ast)
    
    h_targets = get_all_targets_from_applies(ir.body, 'h')
    x_targets = get_all_targets_from_applies(ir.body, 'x')
    assert len(h_targets) == 3
    assert len(x_targets) == 3
    assert h_targets == x_targets


def test_aggregate_multiple_aliases():
    code = """
    create qubits q[8];
    select low from q where index < 4;
    select high from q where index >= 4;
    select odd from q where index % 2 == 1;
    apply h on all from low;
    apply x on all from high;
    apply z on all from odd;
    """
    ast = parser.parse(code, lexer=lexer)
    pipeline = IRPipeline()
    ir = pipeline.run(ast)
    
    h_targets = get_all_targets_from_applies(ir.body, 'h')
    x_targets = get_all_targets_from_applies(ir.body, 'x')
    z_targets = get_all_targets_from_applies(ir.body, 'z')
    
    assert len(h_targets) == 4
    assert len(x_targets) == 4
    assert len(z_targets) == 4

def test_aggregate_inline():
    code = """
    create qubits q[5];
    apply h on all from q where index >= 2;
    """
    ast = parser.parse(code, lexer=lexer)
    pipeline = IRPipeline()
    ir = pipeline.run(ast)
    
    all_targets = get_all_targets_from_applies(ir.body, 'h')
    assert len(all_targets) == 3
    assert IRQubit("q", 2) in all_targets
    assert IRQubit("q", 3) in all_targets
    assert IRQubit("q", 4) in all_targets


def test_aggregate_mixed():
    code = """
    create qubits q[5];
    apply h on q[0], all from q where index > 0;
    """
    ast = parser.parse(code, lexer=lexer)
    pipeline = IRPipeline()
    ir = pipeline.run(ast)
    
    all_targets = get_all_targets_from_applies(ir.body, 'h')
    assert len(all_targets) == 5
    for i in range(5):
        assert IRQubit("q", i) in all_targets

def test_aggregate_all_no_condition():
    code = """
    create qubits q[4];
    apply x on all from q where index >= 0;
    """
    ast = parser.parse(code, lexer=lexer)
    pipeline = IRPipeline()
    ir = pipeline.run(ast)
    
    all_targets = get_all_targets_from_applies(ir.body, 'x')
    assert len(all_targets) == 4
    for i in range(4):
        assert IRQubit("q", i) in all_targets

def test_aggregate_condition_gt():
    code = """
    create qubits q[5];
    apply h on all from q where index > 2;
    """
    ast = parser.parse(code, lexer=lexer)
    pipeline = IRPipeline()
    ir = pipeline.run(ast)
    
    targets = get_all_targets_from_applies(ir.body, 'h')
    assert len(targets) == 2
    assert IRQubit("q", 3) in targets
    assert IRQubit("q", 4) in targets


def test_aggregate_condition_lt():
    code = """
    create qubits q[5];
    apply h on all from q where index < 3;
    """
    ast = parser.parse(code, lexer=lexer)
    pipeline = IRPipeline()
    ir = pipeline.run(ast)
    
    targets = get_all_targets_from_applies(ir.body, 'h')
    assert len(targets) == 3
    assert IRQubit("q", 0) in targets
    assert IRQubit("q", 1) in targets
    assert IRQubit("q", 2) in targets


def test_aggregate_condition_eq():
    code = """
    create qubits q[5];
    apply h on all from q where index == 3;
    """
    ast = parser.parse(code, lexer=lexer)
    pipeline = IRPipeline()
    ir = pipeline.run(ast)
    
    targets = get_all_targets_from_applies(ir.body, 'h')
    assert len(targets) == 1
    assert IRQubit("q", 3) in targets


def test_aggregate_condition_ne():
    code = """
    create qubits q[5];
    apply h on all from q where index != 2;
    """
    ast = parser.parse(code, lexer=lexer)
    pipeline = IRPipeline()
    ir = pipeline.run(ast)
    
    targets = get_all_targets_from_applies(ir.body, 'h')
    assert len(targets) == 4
    assert IRQubit("q", 2) not in targets


def test_aggregate_condition_le():
    code = """
    create qubits q[5];
    apply h on all from q where index <= 2;
    """
    ast = parser.parse(code, lexer=lexer)
    pipeline = IRPipeline()
    ir = pipeline.run(ast)
    
    targets = get_all_targets_from_applies(ir.body, 'h')
    assert len(targets) == 3
    assert IRQubit("q", 0) in targets
    assert IRQubit("q", 1) in targets
    assert IRQubit("q", 2) in targets



def test_aggregate_condition_ge():
    code = """
    create qubits q[5];
    apply h on all from q where index >= 1;
    """
    ast = parser.parse(code, lexer=lexer)
    pipeline = IRPipeline()
    ir = pipeline.run(ast)
    
    targets = get_all_targets_from_applies(ir.body, 'h')
    assert len(targets) == 4
    assert IRQubit("q", 1) in targets
    assert IRQubit("q", 2) in targets
    assert IRQubit("q", 3) in targets
    assert IRQubit("q", 4) in targets

def test_aggregate_condition_and():
    code = """
    create qubits q[10];
    apply h on all from q where index > 2 AND index < 6;
    """
    ast = parser.parse(code, lexer=lexer)
    pipeline = IRPipeline()
    ir = pipeline.run(ast)
    
    targets = get_all_targets_from_applies(ir.body, 'h')
    assert len(targets) == 3
    assert IRQubit("q", 3) in targets
    assert IRQubit("q", 4) in targets
    assert IRQubit("q", 5) in targets


def test_aggregate_condition_or():
    code = """
    create qubits q[10];
    apply h on all from q where index < 2 OR index > 7;
    """
    ast = parser.parse(code, lexer=lexer)
    pipeline = IRPipeline()
    ir = pipeline.run(ast)
    
    targets = get_all_targets_from_applies(ir.body, 'h')
    assert len(targets) == 4
    assert IRQubit("q", 0) in targets
    assert IRQubit("q", 1) in targets
    assert IRQubit("q", 8) in targets
    assert IRQubit("q", 9) in targets


def test_aggregate_condition_complex():
    code = """
    create qubits q[10];
    apply h on all from q where (index % 2 == 0 AND index < 5) OR index == 7;
    """
    ast = parser.parse(code, lexer=lexer)
    pipeline = IRPipeline()
    ir = pipeline.run(ast)
    
    targets = get_all_targets_from_applies(ir.body, 'h')
    assert IRQubit("q", 0) in targets
    assert IRQubit("q", 2) in targets
    assert IRQubit("q", 4) in targets
    assert IRQubit("q", 7) in targets

def test_aggregate_arithmetic_plus():
    code = """
    create qubits q[5];
    apply h on all from q where index + 1 == 3;
    """
    ast = parser.parse(code, lexer=lexer)
    pipeline = IRPipeline()
    ir = pipeline.run(ast)
    
    targets = get_all_targets_from_applies(ir.body, 'h')
    assert len(targets) == 1
    assert IRQubit("q", 2) in targets


def test_aggregate_arithmetic_minus():
    code = """
    create qubits q[5];
    apply h on all from q where index - 1 > 0;
    """
    ast = parser.parse(code, lexer=lexer)
    pipeline = IRPipeline()
    ir = pipeline.run(ast)
    
    targets = get_all_targets_from_applies(ir.body, 'h')
    assert len(targets) == 3
    assert IRQubit("q", 2) in targets
    assert IRQubit("q", 3) in targets
    assert IRQubit("q", 4) in targets



def test_aggregate_arithmetic_mul():
    code = """
    create qubits q[10];
    apply h on all from q where index * 2 < 10;
    """
    ast = parser.parse(code, lexer=lexer)
    pipeline = IRPipeline()
    ir = pipeline.run(ast)
    
    targets = get_all_targets_from_applies(ir.body, 'h')
    assert len(targets) == 5
    for i in range(5):
        assert IRQubit("q", i) in targets


def test_aggregate_arithmetic_div():
    code = """
    create qubits q[10];
    apply h on all from q where index / 3 == 1;
    """
    ast = parser.parse(code, lexer=lexer)
    pipeline = IRPipeline()
    ir = pipeline.run(ast)
    
    targets = get_all_targets_from_applies(ir.body, 'h')
    assert len(targets) == 1
    assert IRQubit("q", 3) in targets

def test_aggregate_condition_with_abs():
    code = """
    create qubits q[5];
    apply h on all from q where abs(index - 3) <= 1;
    """
    ast = parser.parse(code, lexer=lexer)
    pipeline = IRPipeline()
    ir = pipeline.run(ast)
    
    targets = get_all_targets_from_applies(ir.body, 'h')
    assert len(targets) == 3
    assert IRQubit("q", 2) in targets
    assert IRQubit("q", 3) in targets
    assert IRQubit("q", 4) in targets

def test_aggregate_empty_result():
    code = """
    create qubits q[5];
    apply h on all from q where index > 100;
    """
    ast = parser.parse(code, lexer=lexer)
    pipeline = IRPipeline()
    ir = pipeline.run(ast)
    
    h_applies = [s for s in ir.body if isinstance(s, IRApply) and s.gate == 'h']
    assert len(h_applies) == 0


def test_aggregate_single_qubit_register():
    code = """
    create qubits q[1];
    apply h on all from q where index == 0;
    """
    ast = parser.parse(code, lexer=lexer)
    pipeline = IRPipeline()
    ir = pipeline.run(ast)
    
    targets = get_all_targets_from_applies(ir.body, 'h')
    assert len(targets) == 1
    assert IRQubit("q", 0) in targets


def test_aggregate_multiple_registers():
    code = """
    create qubits a[3];
    create qubits b[4];
    apply h on all from a where index >= 1;
    apply x on all from b where index < 2;
    """
    ast = parser.parse(code, lexer=lexer)
    pipeline = IRPipeline()
    ir = pipeline.run(ast)
    
    a_targets = get_all_targets_from_applies(ir.body, 'h')
    b_targets = get_all_targets_from_applies(ir.body, 'x')
    
    assert len(a_targets) == 2
    assert len(b_targets) == 2
    assert all(t.reg == 'a' for t in a_targets)
    assert all(t.reg == 'b' for t in b_targets)
    assert IRQubit("a", 1) in a_targets
    assert IRQubit("a", 2) in a_targets
    assert IRQubit("b", 0) in b_targets
    assert IRQubit("b", 1) in b_targets


def test_aggregate_all_from_alias_no_condition():
    code = """
    create qubits q[5];
    select all_qubits from q;
    apply h on all from all_qubits;
    """
    ast = parser.parse(code, lexer=lexer)
    pipeline = IRPipeline()
    ir = pipeline.run(ast)
    
    targets = get_all_targets_from_applies(ir.body, 'h')
    assert len(targets) == 5
    for i in range(5):
        assert IRQubit("q", i) in targets

def test_aggregate_unknown_alias_error():
    code = """
    create qubits q[4];
    apply h on all from nonexistent;
    """
    ast = parser.parse(code, lexer=lexer)
    pipeline = IRPipeline()
    
    with pytest.raises(Exception) as exc_info:
        pipeline.run(ast)
    
    assert "Unknown alias" in str(exc_info.value) or "nonexistent" in str(exc_info.value)


def test_aggregate_unknown_register_error():
    code = """
    create qubits q[4];
    apply h on all from fake_reg where index > 0;
    """
    ast = parser.parse(code, lexer=lexer)
    pipeline = IRPipeline()
    
    with pytest.raises(Exception) as exc_info:
        pipeline.run(ast)
    
    assert "Unknown register" in str(exc_info.value) or "fake_reg" in str(exc_info.value)

def test_aggregate_full_circuit():
    code = """
    create qubits q[8];
    create bits c[8];
    
    select first_half from q where index < 4;
    select second_half from q where index >= 4;
    select control_qubits from q where index % 2 == 0;
    
    apply x on all from first_half;
    apply h on all from second_half;
    apply z on all from control_qubits;
    
    measure q -> c;
    """
    ast = parser.parse(code, lexer=lexer)
    pipeline = IRPipeline()
    ir = pipeline.run(ast)
    
    x_targets = get_all_targets_from_applies(ir.body, 'x')
    h_targets = get_all_targets_from_applies(ir.body, 'h')
    z_targets = get_all_targets_from_applies(ir.body, 'z')
    
    assert len(x_targets) == 4
    assert len(h_targets) == 4
    assert len(z_targets) == 4
    
    for t in x_targets + h_targets + z_targets:
        assert isinstance(t, IRQubit), f"Unresolved target: {type(t)}"
    measures = [s for s in ir.body if isinstance(s, IRMeasure)]
    assert len(measures) == 1