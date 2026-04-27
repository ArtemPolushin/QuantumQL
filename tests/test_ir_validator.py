import pytest
from ir.ir_classes import *
from ir.ir_validator import IRValidator


def test_validate_known_gate():
    ir = IRProgram([
        IRApply("H", [], [IRQubit("q", 0)])
    ])
    
    validator = IRValidator()
    validator.validate(ir)


def test_validate_unknown_gate():
    ir = IRProgram([
        IRApply("UNKNOWN", [], [IRQubit("q", 0)])
    ])
    
    validator = IRValidator()
    with pytest.raises(ValueError, match="Unknown gate"):
        validator.validate(ir)


def test_validate_wrong_qubit_count():
    ir = IRProgram([
        IRApply("CX", [], [IRQubit("q", 0)])  # CX требует 2 кубита
    ])
    
    validator = IRValidator()
    with pytest.raises(ValueError, match="expects 2 qubit"):
        validator.validate(ir)


def test_validate_user_gate():
    ir = IRProgram([
        IRGateDef("MY_GATE", ["a"], [
            IRApply("H", [], [IRQubit("a", None)])
        ]),
        IRApply("MY_GATE", [], [IRQubit("q", 0)])
    ])
    
    validator = IRValidator()
    validator.validate(ir)


def test_validate_param_gate_without_params():
    ir = IRProgram([
        IRApply("RX", [], [IRQubit("q", 0)])
    ])
    
    validator = IRValidator()
    with pytest.raises(ValueError, match="requires parameters"):
        validator.validate(ir)