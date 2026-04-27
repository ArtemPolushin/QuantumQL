import pytest
from ir.ir_classes import *
from ir.ir_select_resolver import SelectResolver


def test_select_all_qubits():
    ir = IRProgram([
        IRCreateQubits("q", 3),
        IRSelectStmt("all_q", "q", None),
        IRApply("H", [], [IRQubit("all_q", None)])
    ])
    
    resolver = SelectResolver()
    resolved = resolver.resolve(ir)
    
    assert len(resolved.body) == 2
    apply_stmt = resolved.body[1]
    assert len(apply_stmt.targets) == 3
    assert apply_stmt.targets[0].reg == "q"
    assert apply_stmt.targets[0].index == 0
    assert apply_stmt.targets[1].index == 1
    assert apply_stmt.targets[2].index == 2


def test_select_even_indices():
    ir = IRProgram([
        IRCreateQubits("q", 5),
        IRSelectStmt(
            "even",
            "q",
            IRBinOp(
                IRBinOp(IRVar("index"), "%", IRNumber(2)),
                "==",
                IRNumber(0.0)
            )
        ),
        IRApply("H", [], [IRQubit("even", None)])
    ])
    
    resolver = SelectResolver()
    resolved = resolver.resolve(ir)
    
    apply_stmt = resolved.body[1]
    assert len(apply_stmt.targets) == 3  # индексы 0, 2, 4
    assert [t.index for t in apply_stmt.targets] == [0, 2, 4]


def test_select_with_comparison():
    ir = IRProgram([
        IRCreateQubits("q", 5),
        IRSelectStmt(
            "first_half",
            "q",
            IRBinOp(IRVar("index"), "<", IRNumber(2.0))
        ),
        IRApply("X", [], [IRQubit("first_half", None)])
    ])
    
    resolver = SelectResolver()
    resolved = resolver.resolve(ir)
    
    apply_stmt = resolved.body[1]
    assert len(apply_stmt.targets) == 2  # индексы 0, 1
    assert [t.index for t in apply_stmt.targets] == [0, 1]


def test_select_with_complex_condition():
    ir = IRProgram([
        IRCreateQubits("q", 10),
        IRSelectStmt(
            "selected",
            "q",
            IRBinOp(
                IRBinOp(IRVar("index"), ">=", IRNumber(3.0)),
                "AND",
                IRBinOp(IRVar("index"), "<=", IRNumber(7.0))
            )
        ),
        IRApply("H", [], [IRQubit("selected", None)])
    ])
    
    resolver = SelectResolver()
    resolved = resolver.resolve(ir)
    
    apply_stmt = resolved.body[1]
    assert len(apply_stmt.targets) == 5  # индексы 3,4,5,6,7
    assert [t.index for t in apply_stmt.targets] == [3, 4, 5, 6, 7]


def test_select_in_apply_directly():
    ir = IRProgram([
        IRCreateQubits("q", 4),
        IRApply("H", [], [
            IRSelectTarget(
                "q_sel",
                "q",
                IRBinOp(
                    IRBinOp(IRVar("index"), "%", IRNumber(2)),
                    "==",
                    IRNumber(0)
                )
            )
        ])
    ])
    
    resolver = SelectResolver()
    resolved = resolver.resolve(ir)
    
    apply_stmt = resolved.body[1]
    assert len(apply_stmt.targets) == 2  # индексы 0, 2
    assert [t.index for t in apply_stmt.targets] == [0, 2]


def test_multiple_selects():
    ir = IRProgram([
        IRCreateQubits("q", 6),
        IRSelectStmt("even", 
                     "q", 
                     IRBinOp(
                        IRBinOp(IRVar("index"), "%", IRNumber(2)),
                        "==",
                        IRNumber(0)
                    )),
        IRSelectStmt("odd", 
                     "q", 
                     IRBinOp(
                        IRBinOp(IRVar("index"), "%", IRNumber(2)),
                        "==",
                        IRNumber(1)
                    )),
        IRApply("H", [], [IRQubit("even", None)]),
        IRApply("X", [], [IRQubit("odd", None)])
    ])
    
    resolver = SelectResolver()
    resolved = resolver.resolve(ir)
    
    assert len(resolved.body) == 3
    
    even_apply = resolved.body[1]
    assert len(even_apply.targets) == 3
    assert [t.index for t in even_apply.targets] == [0, 2, 4]
    
    odd_apply = resolved.body[2]
    assert len(odd_apply.targets) == 3
    assert [t.index for t in odd_apply.targets] == [1, 3, 5]
    pass


def test_select_with_arithmetic():
    ir = IRProgram([
        IRCreateQubits("q", 5),
        IRSelectStmt(
            "power_of_two",
            "q",
            IRBinOp(
                IRFuncCall("pow", [IRNumber(2.0), IRVar("index")]),
                "<=",
                IRNumber(8.0)
            )
        ),
        IRApply("H", [], [IRQubit("power_of_two", None)])
    ])
    
    resolver = SelectResolver()
    resolved = resolver.resolve(ir)
    
    apply_stmt = resolved.body[1]
    assert len(apply_stmt.targets) == 4
    assert [t.index for t in apply_stmt.targets] == [0, 1, 2, 3]


def test_select_unknown_register():
    ir = IRProgram([
        IRSelectStmt("q_sel", "unknown_reg", None),
        IRApply("H", [], [IRQubit("q_sel", None)])
    ])
    
    resolver = SelectResolver()
    with pytest.raises(ValueError, match="Unknown register"):
        resolver.resolve(ir)