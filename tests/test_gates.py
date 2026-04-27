import pytest
from gates import (
    GateInfo, GATES, 
    SINGLE_QUBIT_GATES, MULTI_QUBIT_GATES, PARAM_GATES,
    is_single_qubit_gate, get_gate_info, normalize_gate_name, gate_exists
)


class TestGateInfo:
    def test_create_gate_info(self):
        gate = GateInfo("h", 1)
        assert gate.name == "h"
        assert gate.num_qubits == 1
        assert gate.has_params == False
    
    def test_create_gate_info_with_params(self):
        gate = GateInfo("rx", 1, True)
        assert gate.name == "rx"
        assert gate.num_qubits == 1
        assert gate.has_params == True


class TestGatesDictionary:    
    def test_gates_contains_standard_gates(self):
        assert "x" in GATES
        assert "h" in GATES
        assert "cx" in GATES
        assert "ccx" in GATES
    
    def test_gates_contains_parametric_gates(self):
        assert "rx" in GATES
        assert "ry" in GATES
        assert "rz" in GATES
        assert "u3" in GATES
    
    def test_gates_contains_aliases(self):
        assert "cnot" in GATES
        assert GATES["cnot"].name == "cx"
        
        assert "toffoli" in GATES
        assert GATES["toffoli"].name == "ccx"
    
    def test_gate_info_correct(self):
        h_info = GATES["h"]
        assert h_info.num_qubits == 1
        assert h_info.has_params == False
        
        rx_info = GATES["rx"]
        assert rx_info.num_qubits == 1
        assert rx_info.has_params == True
        
        cx_info = GATES["cx"]
        assert cx_info.num_qubits == 2
        assert cx_info.has_params == False
    
    def test_measure_is_special(self):
        assert "measure" in GATES
        assert GATES["measure"].num_qubits == 1
    
    def test_barrier_is_variable(self):
        assert "barrier" in GATES
        assert GATES["barrier"].num_qubits == -1


class TestSingleQubitGates:
    def test_single_qubit_gates_contains_basic(self):
        assert "x" in SINGLE_QUBIT_GATES
        assert "y" in SINGLE_QUBIT_GATES
        assert "z" in SINGLE_QUBIT_GATES
        assert "h" in SINGLE_QUBIT_GATES
        assert "s" in SINGLE_QUBIT_GATES
        assert "t" in SINGLE_QUBIT_GATES
    
    def test_single_qubit_gates_contains_parametric(self):
        assert "rx" in SINGLE_QUBIT_GATES
        assert "ry" in SINGLE_QUBIT_GATES
        assert "rz" in SINGLE_QUBIT_GATES
        assert "u1" in SINGLE_QUBIT_GATES
        assert "u2" in SINGLE_QUBIT_GATES
        assert "u3" in SINGLE_QUBIT_GATES
    
    def test_single_qubit_gates_excludes_multi_qubit(self):
        assert "cx" not in SINGLE_QUBIT_GATES
        assert "swap" not in SINGLE_QUBIT_GATES
        assert "ccx" not in SINGLE_QUBIT_GATES
    
    def test_single_qubit_gates_consistent(self):
        for name in SINGLE_QUBIT_GATES:
            assert GATES[name].num_qubits == 1


class TestMultiQubitGates:
    def test_multi_qubit_gates_contains_two_qubit(self):
        assert "cx" in MULTI_QUBIT_GATES
        assert "swap" in MULTI_QUBIT_GATES
        assert "ch" in MULTI_QUBIT_GATES
    
    def test_multi_qubit_gates_contains_three_qubit(self):
        assert "ccx" in MULTI_QUBIT_GATES
        assert "cswap" in MULTI_QUBIT_GATES
    
    def test_multi_qubit_gates_contains_barrier(self):
        assert "barrier" in MULTI_QUBIT_GATES
    
    def test_multi_qubit_gates_excludes_single_qubit(self):
        assert "h" not in MULTI_QUBIT_GATES
        assert "x" not in MULTI_QUBIT_GATES
        assert "rx" not in MULTI_QUBIT_GATES


class TestParamGates:
    def test_param_gates_contains_parametric(self):
        assert "rx" in PARAM_GATES
        assert "ry" in PARAM_GATES
        assert "rz" in PARAM_GATES
        assert "u1" in PARAM_GATES
        assert "u3" in PARAM_GATES
        assert "cp" in PARAM_GATES
    
    def test_param_gates_excludes_non_parametric(self):
        assert "h" not in PARAM_GATES
        assert "x" not in PARAM_GATES
        assert "cx" not in PARAM_GATES


class TestIsSingleQubitGate:
    def test_single_qubit_gates(self):
        assert is_single_qubit_gate("h") == True
        assert is_single_qubit_gate("x") == True
        assert is_single_qubit_gate("rx") == True
        assert is_single_qubit_gate("u3") == True
    
    def test_multi_qubit_gates(self):
        assert is_single_qubit_gate("cx") == False
        assert is_single_qubit_gate("swap") == False
        assert is_single_qubit_gate("ccx") == False
    
    def test_case_insensitive(self):
        assert is_single_qubit_gate("H") == True
        assert is_single_qubit_gate("RX") == True
        assert is_single_qubit_gate("CX") == False
    
    def test_unknown_gate(self):
        assert is_single_qubit_gate("unknown") == False
    
    def test_measure_is_single_qubit(self):
        assert is_single_qubit_gate("measure") == True
    
    def test_barrier_is_not_single(self):
        assert is_single_qubit_gate("barrier") == False


class TestGetGateInfo:
    def test_known_gate(self):
        info = get_gate_info("h")
        assert info.name == "h"
        assert info.num_qubits == 1
    
    def test_known_gate_case_insensitive(self):
        info = get_gate_info("RX")
        assert info.name == "rx"
        assert info.has_params == True
    
    def test_unknown_gate(self):
        info = get_gate_info("unknown")
        assert info.name == "unknown"
        assert info.num_qubits == -1
        assert info.has_params == False
    
    def test_alias_gate(self):
        info = get_gate_info("cnot")
        assert info.name == "cx"
        assert info.num_qubits == 2
    
    def test_toffoli_alias(self):
        info = get_gate_info("toffoli")
        assert info.name == "ccx"
        assert info.num_qubits == 3


class TestNormalizeGateName:
    def test_lowercase(self):
        assert normalize_gate_name("H") == "h"
        assert normalize_gate_name("Rx") == "rx"
        assert normalize_gate_name("CX") == "cx"
    
    def test_already_lowercase(self):
        assert normalize_gate_name("h") == "h"
        assert normalize_gate_name("rx") == "rx"
    
    def test_mixed_case(self):
        assert normalize_gate_name("Toffoli") == "toffoli"


class TestGateExists:
    def test_existing_gate(self):
        assert gate_exists("h") == True
        assert gate_exists("cx") == True
        assert gate_exists("ccx") == True
        assert gate_exists("rx") == True
    
    def test_nonexistent_gate(self):
        assert gate_exists("unknown") == False
        assert gate_exists("my_custom_gate") == False
    
    def test_case_insensitive(self):
        assert gate_exists("H") == True
        assert gate_exists("CX") == True
        assert gate_exists("Unknown") == False
    
    def test_aliases_exist(self):
        assert gate_exists("cnot") == True
        assert gate_exists("toffoli") == True
        assert gate_exists("fredkin") == True


class TestGateConsistency:
    def test_all_gates_have_valid_qubit_count(self):
        for name, info in GATES.items():
            assert info.num_qubits >= -1
            assert isinstance(info.num_qubits, int)
    
    def test_all_gates_have_name(self):
        for name, info in GATES.items():
            assert len(info.name) > 0
            assert isinstance(info.name, str)
    
    def test_single_qubit_set_consistent(self):
        for name, info in GATES.items():
            if info.num_qubits == 1:
                assert name in SINGLE_QUBIT_GATES
            else:
                assert name not in SINGLE_QUBIT_GATES
    
    def test_param_set_consistent(self):
        for name, info in GATES.items():
            if info.has_params:
                assert name in PARAM_GATES
            else:
                assert name not in PARAM_GATES
    
    def test_no_duplicate_gate_names(self):
        assert len(GATES) == len(set(GATES.keys()))