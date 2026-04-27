import pytest
from ir.ir_classes import *
from ast_nodes import *
from ir.ir_builder import IRBuilder

class TestIRBuilder:
    
    def setup_method(self):
        self.builder = IRBuilder()
    
    def test_empty_program(self):
        ast = Program([])
        ir = self.builder.build(ast)
        
        assert isinstance(ir, IRProgram)
        assert ir.body == []
    
    def test_create_qubits(self):
        ast = Program([
            CreateQubits("q", 5)
        ])
        
        ir = self.builder.build(ast)
        
        assert len(ir.body) == 1
        stmt = ir.body[0]
        assert isinstance(stmt, IRCreateQubits)
        assert stmt.name == "q"
        assert stmt.size == 5
    
    def test_multiple_create_qubits(self):
        ast = Program([
            CreateQubits("a", 3),
            CreateQubits("b", 4),
            CreateQubits("c", 2)
        ])
        
        ir = self.builder.build(ast)
        
        assert len(ir.body) == 3
        assert all(isinstance(s, IRCreateQubits) for s in ir.body)
        assert [s.name for s in ir.body] == ["a", "b", "c"]
        assert [s.size for s in ir.body] == [3, 4, 2]
    
    def test_apply_single_qubit_gate(self):
        ast = Program([
            ApplyGate("H", [QubitRef("q", 0)], [])
        ])
        
        ir = self.builder.build(ast)
        
        stmt = ir.body[0]
        assert isinstance(stmt, IRApply)
        assert stmt.gate == "H"
        assert stmt.params == []
        assert len(stmt.targets) == 1
        assert isinstance(stmt.targets[0], IRQubit)
        assert stmt.targets[0].reg == "q"
        assert stmt.targets[0].index == 0
    
    def test_apply_two_qubit_gate(self):
        ast = Program([
            ApplyGate("CX", [
                QubitRef("q", 0),
                QubitRef("q", 1)
            ], [])
        ])
        
        ir = self.builder.build(ast)
        
        stmt = ir.body[0]
        assert isinstance(stmt, IRApply)
        assert stmt.gate == "CX"
        assert len(stmt.targets) == 2
        assert stmt.targets[0].reg == "q"
        assert stmt.targets[0].index == 0
        assert stmt.targets[1].reg == "q"
        assert stmt.targets[1].index == 1
    
    def test_apply_with_register_target(self):
        ast = Program([
            ApplyGate("H", [QubitRef("q", None)], [])
        ])
        
        ir = self.builder.build(ast)
        
        stmt = ir.body[0]
        assert isinstance(stmt, IRApply)
        assert len(stmt.targets) == 1
        assert stmt.targets[0].reg == "q"
        assert stmt.targets[0].index is None
    
    def test_apply_with_range_target(self):
        ast = Program([
            ApplyGate("H", [QubitRef("q", (0, 3))], [])
        ])
        
        ir = self.builder.build(ast)
        
        stmt = ir.body[0]
        assert isinstance(stmt, IRApply)
        assert len(stmt.targets) == 1
        assert stmt.targets[0].reg == "q"
        assert stmt.targets[0].index == (0, 3)
    
    def test_apply_with_wildcard_target(self):
        ast = Program([
            ApplyGate("H", [QubitRef("q", "*")], [])
        ])
        
        ir = self.builder.build(ast)
        
        stmt = ir.body[0]
        assert isinstance(stmt, IRApply)
        assert len(stmt.targets) == 1
        assert stmt.targets[0].reg == "q"
        assert stmt.targets[0].index == "*"
    
    def test_apply_multiple_targets_mixed(self):
        ast = Program([
            ApplyGate("BARRIER", [
                QubitRef("q", 0),
                QubitRef("q", (1, 3)),
                QubitRef("r", None)
            ], [])
        ])
        
        ir = self.builder.build(ast)
        
        stmt = ir.body[0]
        assert isinstance(stmt, IRApply)
        assert len(stmt.targets) == 3
        assert stmt.targets[0].index == 0
        assert stmt.targets[1].index == (1, 3)
        assert stmt.targets[2].index is None
    
    def test_apply_with_number_param(self):
        ast = Program([
            ApplyGate("RX", [QubitRef("q", 0)], [Number(3.14)])
        ])
        
        ir = self.builder.build(ast)
        
        stmt = ir.body[0]
        assert len(stmt.params) == 1
        assert isinstance(stmt.params[0], IRNumber)
        assert stmt.params[0].value == 3.14
    
    def test_apply_with_float_param(self):
        ast = Program([
            ApplyGate("RX", [QubitRef("q", 0)], [Number(2.5)])
        ])
        
        ir = self.builder.build(ast)
        
        stmt = ir.body[0]
        assert len(stmt.params) == 1
        assert isinstance(stmt.params[0], IRNumber)
        assert stmt.params[0].value == 2.5
    
    def test_apply_with_multiple_number_params(self):
        ast = Program([
            ApplyGate("U3", [QubitRef("q", 0)], [
                Number(1.0),
                Number(2.0),
                Number(3.0)
            ])
        ])
        
        ir = self.builder.build(ast)
        
        stmt = ir.body[0]
        assert len(stmt.params) == 3
        assert all(isinstance(p, IRNumber) for p in stmt.params)
        assert [p.value for p in stmt.params] == [1.0, 2.0, 3.0]
    
    def test_apply_with_variable_param(self):
        ast = Program([
            ApplyGate("RX", [QubitRef("q", 0)], [Var("theta")])
        ])
        
        ir = self.builder.build(ast)
        
        stmt = ir.body[0]
        assert len(stmt.params) == 1
        assert isinstance(stmt.params[0], IRVar)
        assert stmt.params[0].name == "theta"
    
    def test_apply_with_constant_param(self):
        ast = Program([
            ApplyGate("RX", [QubitRef("q", 0)], [Constant("pi")])
        ])
        
        ir = self.builder.build(ast)
        
        stmt = ir.body[0]
        assert len(stmt.params) == 1
        assert isinstance(stmt.params[0], IRConst)
        assert stmt.params[0].name == "pi"
    
    def test_apply_with_binary_expression_param(self):
        ast = Program([
            ApplyGate("RX", [QubitRef("q", 0)], [
                BinOp(Constant("pi"), "/", Number(2.0))
            ])
        ])
        
        ir = self.builder.build(ast)
        
        stmt = ir.body[0]
        assert len(stmt.params) == 1
        param = stmt.params[0]
        assert isinstance(param, IRBinOp)
        assert param.op == "/"
        assert isinstance(param.left, IRConst)
        assert param.left.name == "pi"
        assert isinstance(param.right, IRNumber)
        assert param.right.value == 2.0
    
    def test_apply_with_complex_expression_param(self):
        ast = Program([
            ApplyGate("RX", [QubitRef("q", 0)], [
                BinOp(
                    BinOp(Number(3.0), "*", Var("theta")),
                    "+",
                    Constant("pi")
                )
            ])
        ])
        
        ir = self.builder.build(ast)
        
        stmt = ir.body[0]
        param = stmt.params[0]
        assert isinstance(param, IRBinOp)
        assert param.op == "+"
        assert isinstance(param.left, IRBinOp)
        assert param.left.op == "*"
        assert isinstance(param.right, IRConst)
        assert param.right.name == "pi"
    
    def test_apply_with_unary_expression_param(self):
        ast = Program([
            ApplyGate("RX", [QubitRef("q", 0)], [
                UnaryOp("-", Number(3.14))
            ])
        ])
        
        ir = self.builder.build(ast)
        
        stmt = ir.body[0]
        param = stmt.params[0]
        assert isinstance(param, IRUnaryOp)
        assert param.op == "-"
        assert isinstance(param.expr, IRNumber)
        assert param.expr.value == 3.14
    
    def test_apply_with_function_call_param(self):
        ast = Program([
            ApplyGate("RX", [QubitRef("q", 0)], [
                FuncCall("sin", [Constant("pi")])
            ])
        ])
        
        ir = self.builder.build(ast)
        
        stmt = ir.body[0]
        param = stmt.params[0]
        assert isinstance(param, IRFuncCall)
        assert param.name == "sin"
        assert len(param.args) == 1
        assert isinstance(param.args[0], IRConst)
        assert param.args[0].name == "pi"
    
    def test_apply_with_mixed_param_types(self):
        ast = Program([
            ApplyGate("U3", [QubitRef("q", 0)], [
                Number(1.0),
                Var("theta"),
                BinOp(Constant("pi"), "/", Number(2.0))
            ])
        ])
        
        ir = self.builder.build(ast)
        
        stmt = ir.body[0]
        assert len(stmt.params) == 3
        assert isinstance(stmt.params[0], IRNumber)
        assert isinstance(stmt.params[1], IRVar)
        assert isinstance(stmt.params[2], IRBinOp)
    
    def test_measure_single_qubit(self):
        ast = Program([
            Measure([QubitRef("q", 0)], None)
        ])
        
        ir = self.builder.build(ast)
        
        stmt = ir.body[0]
        assert isinstance(stmt, IRMeasure)
        assert len(stmt.source) == 1
        assert stmt.source[0].reg == "q"
        assert stmt.source[0].index == 0
        assert stmt.target is None
    
    def test_measure_multiple_qubits(self):
        ast = Program([
            Measure([
                QubitRef("q", 0),
                QubitRef("q", 1),
                QubitRef("q", 2)
            ], None)
        ])
        
        ir = self.builder.build(ast)
        
        stmt = ir.body[0]
        assert isinstance(stmt, IRMeasure)
        assert len(stmt.source) == 3
        assert [q.index for q in stmt.source] == [0, 1, 2]
    
    def test_measure_register(self):
        ast = Program([
            Measure([QubitRef("q", None)], None)
        ])
        
        ir = self.builder.build(ast)
        
        stmt = ir.body[0]
        assert isinstance(stmt, IRMeasure)
        assert len(stmt.source) == 1
        assert stmt.source[0].reg == "q"
        assert stmt.source[0].index is None
    
    def test_measure_with_bits(self):
        ast = Program([
            CreateQubits("q", 2),
            Measure([QubitRef("q", 0)], [QubitRef("c", 0)])
        ])
        
        ir = self.builder.build(ast)
        
        assert len(ir.body) == 2  # CreateQubits + Measure
        stmt = ir.body[1]  # Measure
        assert isinstance(stmt, IRMeasure)
        assert len(stmt.source) == 1
        assert stmt.source[0].reg == "q"
        assert stmt.source[0].index == 0
        assert len(stmt.target) == 1
        assert stmt.target[0].reg == "c"
        assert stmt.target[0].index == 0
    
    def test_gate_definition_simple(self):
        ast = Program([
            GateDef("MY_GATE", ["a", "b"], [
                ApplyGate("CX", [QubitRef("a", None), QubitRef("b", None)], [])
            ])
        ])
        
        ir = self.builder.build(ast)
        
        stmt = ir.body[0]
        assert isinstance(stmt, IRGateDef)
        assert stmt.name == "MY_GATE"
        assert stmt.params == ["a", "b"]
        assert len(stmt.body) == 1
        assert isinstance(stmt.body[0], IRApply)
        assert stmt.body[0].gate == "CX"
    
    def test_gate_definition_with_params(self):
        ast = Program([
            GateDef("MY_RX", ["theta", "q"], [
                ApplyGate("RX", [QubitRef("q", None)], [Var("theta")])
            ])
        ])
        
        ir = self.builder.build(ast)
        
        stmt = ir.body[0]
        assert isinstance(stmt, IRGateDef)
        assert stmt.name == "MY_RX"
        assert stmt.params == ["theta", "q"]
        assert len(stmt.body) == 1
        body_stmt = stmt.body[0]
        assert body_stmt.gate == "RX"
        assert len(body_stmt.params) == 1
        assert isinstance(body_stmt.params[0], IRVar)
        assert body_stmt.params[0].name == "theta"
    
    def test_gate_definition_multiple_statements(self):
        ast = Program([
            GateDef("COMPLEX", ["a", "b", "c"], [
                ApplyGate("H", [QubitRef("a", None)], []),
                ApplyGate("CX", [QubitRef("a", None), QubitRef("b", None)], []),
                ApplyGate("CX", [QubitRef("b", None), QubitRef("c", None)], [])
            ])
        ])
        
        ir = self.builder.build(ast)
        
        stmt = ir.body[0]
        assert isinstance(stmt, IRGateDef)
        assert len(stmt.body) == 3
        assert [s.gate for s in stmt.body] == ["H", "CX", "CX"]
    
    def test_nested_gate_definitions(self):
        ast = Program([
            GateDef("OUTER", ["a"], [
                GateDef("INNER", ["b"], [
                    ApplyGate("H", [QubitRef("b", None)], [])
                ]),
                ApplyGate("INNER", [QubitRef("a", None)], [])
            ])
        ])
        
        ir = self.builder.build(ast)
        
        stmt = ir.body[0]
        assert isinstance(stmt, IRGateDef)
        assert len(stmt.body) == 2
        assert isinstance(stmt.body[0], IRGateDef)
        assert stmt.body[0].name == "INNER"
        assert isinstance(stmt.body[1], IRApply)
        assert stmt.body[1].gate == "INNER"
    
    def test_select_statement(self):
        ast = Program([
            SelectStmt("even", "q", 
                      BinOp(Var("index"), "%", Number(2.0)))
        ])
        
        ir = self.builder.build(ast)
        
        stmt = ir.body[0]
        assert isinstance(stmt, IRSelectStmt)
        assert stmt.alias == "even"
        assert stmt.source == "q"
        assert isinstance(stmt.condition, IRBinOp)
        assert stmt.condition.op == "%"
    
    def test_select_statement_without_condition(self):
        ast = Program([
            SelectStmt("all", "q", None)
        ])
        
        ir = self.builder.build(ast)
        
        stmt = ir.body[0]
        assert isinstance(stmt, IRSelectStmt)
        assert stmt.alias == "all"
        assert stmt.source == "q"
        assert stmt.condition is None
    
    def test_select_statement_with_complex_condition(self):
        ast = Program([
            SelectStmt("selected", "q",
                BinOp(
                    BinOp(Var("index"), ">=", Number(2.0)),
                    "AND",
                    BinOp(Var("index"), "<=", Number(5.0))
                )
            )
        ])
        
        ir = self.builder.build(ast)
        
        stmt = ir.body[0]
        assert isinstance(stmt, IRSelectStmt)
        condition = stmt.condition
        assert isinstance(condition, IRBinOp)
        assert condition.op == "AND"
        assert isinstance(condition.left, IRBinOp)
        assert condition.left.op == ">="
        assert isinstance(condition.right, IRBinOp)
        assert condition.right.op == "<="
    
    def test_apply_with_select_target(self):
        ast = Program([
            ApplyGate("H", [
                SelectExpr("q", "a", 
                    BinOp(Var("index"), "<", Number(3.0)))
            ], [])
        ])
        
        ir = self.builder.build(ast)
        
        stmt = ir.body[0]
        assert isinstance(stmt, IRApply)
        assert len(stmt.targets) == 1
        target = stmt.targets[0]
        assert isinstance(target, IRSelectTarget)
        assert target.alias == "q"
        assert target.source == "a"
        assert isinstance(target.condition, IRBinOp)
    
    def test_apply_with_mixed_targets(self):
        ast = Program([
            ApplyGate("BARRIER", [
                QubitRef("q", 0),
                SelectExpr("s", "a", None),
                QubitRef("q", 1)
            ], [])
        ])
        
        ir = self.builder.build(ast)
        
        stmt = ir.body[0]
        assert len(stmt.targets) == 3
        assert isinstance(stmt.targets[0], IRQubit)
        assert isinstance(stmt.targets[1], IRSelectTarget)
        assert isinstance(stmt.targets[2], IRQubit)
    
    def test_complete_program(self):
        ast = Program([
            CreateQubits("q", 5),
            CreateQubits("anc", 2),
            SelectStmt("control", "q", BinOp(Var("index"), "<", Number(2.0))),
            GateDef("MY_CNOT", ["c", "t"], [
                ApplyGate("CX", [QubitRef("c", None), QubitRef("t", None)], [])
            ]),
            ApplyGate("H", [SelectExpr("c", "q", None)], []),
            ApplyGate("MY_CNOT", [
                QubitRef("q", 0),
                QubitRef("anc", 0)
            ], []),
            ApplyGate("RX", [QubitRef("q", 1)], [BinOp(Constant("pi"), "/", Number(4.0))]),
            Measure([QubitRef("q", None)], None)
        ])
        
        ir = self.builder.build(ast)
        
        assert len(ir.body) == 8
        assert isinstance(ir.body[0], IRCreateQubits)
        assert isinstance(ir.body[1], IRCreateQubits)
        assert isinstance(ir.body[2], IRSelectStmt)
        assert isinstance(ir.body[3], IRGateDef)
        assert isinstance(ir.body[4], IRApply)
        assert isinstance(ir.body[5], IRApply)
        assert isinstance(ir.body[6], IRApply)
        assert isinstance(ir.body[7], IRMeasure)
    
    def test_unknown_statement_type(self):
        class UnknownStmt:
            pass
        
        ast = Program([UnknownStmt()])
        
        with pytest.raises(ValueError, match="Unknown statement"):
            self.builder.build(ast)
    
    def test_unknown_value_type(self):
        class UnknownValue:
            pass
        
        ast = Program([
            ApplyGate("RX", [QubitRef("q", 0)], [UnknownValue()])
        ])
        
        with pytest.raises(ValueError, match="Unknown value type"):
            self.builder.build(ast)
    
    def test_unknown_expression_type(self):
        class UnknownExpr(Expr):
            pass
        
        ast = Program([
            ApplyGate("RX", [QubitRef("q", 0)], [UnknownExpr()])
        ])
        
        with pytest.raises(ValueError, match="Unknown value type"):
            self.builder.build(ast)