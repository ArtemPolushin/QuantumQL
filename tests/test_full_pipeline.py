import pytest
from ir.ir_pipeline import IRPipeline
from ir.ir_classes import *
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

class TestPipeline:
    
    def setup_method(self):
        self.pipeline = IRPipeline()
    
    def test_simple_program(self):
        code = """
        CREATE QUBITS q[2];
        APPLY H ON q[0];
        """
        
        ast = parse_string(code)
        ir = self.pipeline.run(ast)
        
        assert len(ir.body) == 2
        assert isinstance(ir.body[0], IRCreateQubits)
        assert ir.body[0].name == "q"
        assert ir.body[0].size == 2
        
        assert isinstance(ir.body[1], IRApply)
        assert ir.body[1].gate == "H"
        assert len(ir.body[1].targets) == 1
        assert ir.body[1].targets[0].index == 0
    
    def test_range_expansion(self):
        code = """
        CREATE QUBITS q[5];
        APPLY H ON q[0:2];
        """
        
        ast = parse_string(code)
        ir = self.pipeline.run(ast)
        
        h_stmts = [s for s in ir.body if isinstance(s, IRApply) and s.gate == "H"]
        assert len(h_stmts) == 3
        assert [s.targets[0].index for s in h_stmts] == [0, 1, 2]
    
    def test_range_descending(self):
        code = """
        CREATE QUBITS q[5];
        APPLY H ON q[2:0];
        """
        
        ast = parse_string(code)
        ir = self.pipeline.run(ast)
        
        h_stmts = [s for s in ir.body if isinstance(s, IRApply) and s.gate == "H"]
        assert len(h_stmts) == 3
        assert [s.targets[0].index for s in h_stmts] == [2, 1, 0]
    
    def test_wildcard_expansion(self):
        code = """
        CREATE QUBITS q[3];
        APPLY X ON q[*];
        """
        
        ast = parse_string(code)
        ir = self.pipeline.run(ast)
        
        x_stmts = [s for s in ir.body if isinstance(s, IRApply) and s.gate == "X"]
        assert len(x_stmts) == 3
        assert [s.targets[0].index for s in x_stmts] == [0, 1, 2]
    
    def test_const_expression_evaluation(self):
        code = """
        CREATE QUBITS q[1];
        APPLY RX(pi/2) ON q[0];
        APPLY RY(sin(pi/4)) ON q[0];
        """
        
        ast = parse_string(code)
        ir = self.pipeline.run(ast)
        
        rx_stmt = [s for s in ir.body if isinstance(s, IRApply) and s.gate == "RX"][0]
        ry_stmt = [s for s in ir.body if isinstance(s, IRApply) and s.gate == "RY"][0]
        
        assert isinstance(rx_stmt.params[0], IRNumber)
        assert abs(rx_stmt.params[0].value - 1.5708) < 0.001
        
        assert isinstance(ry_stmt.params[0], IRNumber)
        assert abs(ry_stmt.params[0].value - 0.7071) < 0.001
    
    def test_select_basic(self):
        code = """
        CREATE QUBITS q[4];
        SELECT even FROM q WHERE index % 2 == 0;
        APPLY H ON even;
        """
        
        ast = parse_string(code)
        ir = self.pipeline.run(ast)
        
        h_stmts = [s for s in ir.body if isinstance(s, IRApply) and s.gate == "H"]
        assert len(h_stmts) == 2
        assert [s.targets[0].index for s in h_stmts] == [0, 2]
    
    def test_select_inline(self):
        code = """
        CREATE QUBITS q[5];
        APPLY X ON SELECT qbit FROM q WHERE index < 3;
        """
        
        ast = parse_string(code)
        ir = self.pipeline.run(ast)
        
        x_stmts = [s for s in ir.body if isinstance(s, IRApply) and s.gate == "X"]
        assert len(x_stmts) == 3
        assert [s.targets[0].index for s in x_stmts] == [0, 1, 2]
    
    def test_select_complex_condition(self):
        code = """
        CREATE QUBITS q[10];
        SELECT mid FROM q WHERE index >= 3 AND index <= 6;
        APPLY H ON mid;
        """
        
        ast = parse_string(code)
        ir = self.pipeline.run(ast)
        
        h_stmts = [s for s in ir.body if isinstance(s, IRApply) and s.gate == "H"]
        assert len(h_stmts) == 4
        assert [s.targets[0].index for s in h_stmts] == [3, 4, 5, 6]
    
    def test_gate_definition_simple(self):
        code = """
        GATE BELL(a, b) {
            APPLY H ON a;
            APPLY CX ON a, b;
        }
        CREATE QUBITS q[2];
        APPLY BELL ON q[0], q[1];
        """
        
        ast = parse_string(code)
        ir = self.pipeline.run(ast)
        
        h_stmts = [s for s in ir.body if isinstance(s, IRApply) and s.gate == "H"]
        cx_stmts = [s for s in ir.body if isinstance(s, IRApply) and s.gate == "CX"]
        
        assert len(h_stmts) == 1
        assert h_stmts[0].targets[0].index == 0
        
        assert len(cx_stmts) == 1
        assert cx_stmts[0].targets[0].index == 0
        assert cx_stmts[0].targets[1].index == 1
    
    def test_gate_definition_with_params(self):
        code = """
        GATE MY_RX(theta, q) {
            APPLY RX(theta) ON q;
        }
        CREATE QUBITS q[1];
        APPLY MY_RX(pi/4) ON q[0];
        """
        
        ast = parse_string(code)
        ir = self.pipeline.run(ast)
        
        rx_stmt = [s for s in ir.body if isinstance(s, IRApply) and s.gate == "RX"][0]

        print(f"Param: {rx_stmt.params[0]}")
        print(f"Type: {type(rx_stmt.params[0])}")
        assert isinstance(rx_stmt.params[0], IRNumber)
        assert abs(rx_stmt.params[0].value - 0.7854) < 0.001
    
    def test_nested_gate_definition(self):
        code = """
        GATE H2(q) {
            APPLY H ON q;
            APPLY H ON q;
        }
        GATE H4(q) {
            APPLY H2 ON q;
            APPLY H2 ON q;
        }
        CREATE QUBITS q[1];
        APPLY H4 ON q[0];
        """
        
        ast = parse_string(code)
        ir = self.pipeline.run(ast)
        
        h_stmts = [s for s in ir.body if isinstance(s, IRApply) and s.gate == "H"]
        assert len(h_stmts) == 4
    
    def test_mixed_features(self):
        code = """
        CREATE QUBITS a[4];
        CREATE QUBITS b[4];
        
        GATE SWAP_LIKE(x, y) {
            APPLY CX ON x, y;
            APPLY CX ON y, x;
            APPLY CX ON x, y;
        }
        
        SELECT even FROM a WHERE index % 2 == 0;
        APPLY H ON even;
        APPLY SWAP_LIKE ON a[0], b[0];
        APPLY RX(pi/2) ON a[1:2];
        """
        
        ast = parse_string(code)
        ir = self.pipeline.run(ast)
        
        h_stmts = [s for s in ir.body if isinstance(s, IRApply) and s.gate == "H"]
        assert len(h_stmts) == 2
        assert [s.targets[0].index for s in h_stmts] == [0, 2]
        
        cx_stmts = [s for s in ir.body if isinstance(s, IRApply) and s.gate == "CX"]
        assert len(cx_stmts) == 3
        
        rx_stmts = [s for s in ir.body if isinstance(s, IRApply) and s.gate == "RX"]
        assert len(rx_stmts) == 2
        assert [s.targets[0].index for s in rx_stmts] == [1, 2]
    
    def test_measure_single(self):
        code = """
        CREATE QUBITS q[2];
        APPLY H ON q[0];
        MEASURE q[0];
        """
        
        ast = parse_string(code)
        ir = self.pipeline.run(ast)
        
        measure_stmts = [s for s in ir.body if isinstance(s, IRMeasure)]
        assert len(measure_stmts) == 1
        assert len(measure_stmts[0].source) == 1
        assert measure_stmts[0].source[0].index == 0
    
    def test_measure_register(self):
        code = """
        CREATE QUBITS q[3];
        APPLY H ON q[*];
        MEASURE q;
        """
        
        ast = parse_string(code)
        ir = self.pipeline.run(ast)
        
        measure_stmts = [s for s in ir.body if isinstance(s, IRMeasure)]
        assert len(measure_stmts) == 1
        assert len(measure_stmts[0].source) == 1
        assert measure_stmts[0].source[0].reg == "q"
        assert measure_stmts[0].source[0].index is None


class TestPipelineErrors:
    
    def setup_method(self):
        self.pipeline = IRPipeline()
    
    def test_unknown_gate_error(self):
        code = """
        CREATE QUBITS q[1];
        APPLY UNKNOWN_GATE ON q[0];
        """
        
        ast = parse_string(code)
        with pytest.raises(Exception, match="Unknown gate"):
            self.pipeline.run(ast)
    
    def test_wrong_qubit_count_error(self):
        code = """
        CREATE QUBITS q[2];
        APPLY CX ON q[0];
        """
        
        ast = parse_string(code)
        with pytest.raises(Exception, match="expects 2 qubit"):
            self.pipeline.run(ast)
    
    def test_unknown_register_in_select(self):
        code = """
        CREATE QUBITS q[2];
        SELECT x FROM unknown WHERE index == 0;
        """
        
        ast = parse_string(code)
        with pytest.raises(Exception, match="Unknown register"):
            self.pipeline.run(ast)
    
    def test_infinite_recursion_detection(self):
        code = """
        GATE A(q) {
            APPLY B ON q;
        }
        GATE B(q) {
            APPLY A ON q;
        }
        CREATE QUBITS q[1];
        APPLY A ON q[0];
        """
        
        ast = parse_string(code)
        with pytest.raises(Exception, match="Infinite gate expansion"):
            self.pipeline.run(ast)