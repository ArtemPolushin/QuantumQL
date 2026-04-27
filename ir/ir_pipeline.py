from ir.ir_builder import IRBuilder
from ir.ir_const_eval import ConstEvaluator
from ir.ir_lowering import IRLowering
from ir.ir_select_resolver import SelectResolver
from range_engine import RangeEngine
from ir.ir_single_qubit_expand import SingleQubitExpand
from ir.ir_validator import IRValidator


class IRPipeline:    
    def __init__(self, debug=False):
        self.debug = debug
        self.passes = [
            ("Build IR", IRBuilder()),
            ("Const Eval 1", ConstEvaluator()),
            ("Lowering", IRLowering()),
            ("Const Eval 2", ConstEvaluator()),
            ("Select Resolver", SelectResolver()),
            ("Range Engine", RangeEngine()),
            ("Single Qubit Expand", SingleQubitExpand()),
            ("Validator", IRValidator()),
        ]
    
    def run(self, ast):
        ir = None
        
        for name, pass_obj in self.passes:
            try:
                if name == "Build IR":
                    ir = pass_obj.build(ast)
                else:
                    ir = self._run_pass(pass_obj, ir)
                
                if self.debug:
                    self._dump_ir(name, ir)
                    
            except Exception as e:
                raise Exception(f"IR error in '{name}': {e}") from e
        
        return ir
    
    def _run_pass(self, pass_obj, ir):
        if hasattr(pass_obj, 'evaluate'):
            return pass_obj.evaluate(ir)
        elif hasattr(pass_obj, 'lower'):
            return pass_obj.lower(ir)
        elif hasattr(pass_obj, 'resolve'):
            return pass_obj.resolve(ir)
        elif hasattr(pass_obj, 'expand'):
            return pass_obj.expand(ir)
        elif hasattr(pass_obj, 'validate'):
            return pass_obj.validate(ir)
        else:
            raise ValueError(f"Unknown pass interface for {type(pass_obj)}")
    
    def _dump_ir(self, name, ir):
        print(f"\n=== After {name} ===")
        for stmt in ir.body:
            print(f"  {stmt}")
    
    def add_pass(self, name, pass_obj, position=None):
        if position is None:
            self.passes.append((name, pass_obj))
        else:
            self.passes.insert(position, (name, pass_obj))
    
    def remove_pass(self, name):
        self.passes = [(n, p) for n, p in self.passes if n != name]