from ir.ir_classes import *

class RangeEngine:
    def __init__(self):
        self.reg_sizes = {}
    
    def expand(self, ir: IRProgram):
        for stmt in ir.body:
            if isinstance(stmt, IRCreateQubits):
                self.reg_sizes[stmt.name] = stmt.size
        
        out = []
        for stmt in ir.body:
            if isinstance(stmt, IRCreateQubits):
                out.append(stmt)
            elif isinstance(stmt, IRApply):
                out.extend(self._expand_apply(stmt))
            elif isinstance(stmt, IRMeasure):
                out.append(stmt)
            elif isinstance(stmt, IRGateDef):
                out.append(stmt)
            elif isinstance(stmt, IRInputParam):
                out.append(stmt)
            elif isinstance(stmt, IRSelectStmt):
                pass
            else:
                out.append(stmt)
        
        return IRProgram(out)
    
    def _expand_apply(self, stmt: IRApply):
        target_lists = [self._expand_target_to_list(t) for t in stmt.targets]
        
        lengths = [len(lst) for lst in target_lists]
        if len(set(lengths)) != 1:
            raise ValueError(
                f"Mismatched range lengths in apply {stmt.gate}: {lengths}"
            )
        
        length = lengths[0] if lengths else 0
        if length == 0:
            return []
        
        result = []
        for i in range(length):
            targets_i = [lst[i] for lst in target_lists]
            result.append(
                IRApply(
                    gate=stmt.gate,
                    params=stmt.params,
                    targets=targets_i
                )
            )
        return result
    
    def _expand_target_to_list(self, t):
        if isinstance(t, IRQubit):
            if t.index is None:
                return [t]
            elif isinstance(t.index, int):
                return [t]
            elif t.index == "*":
                if t.reg not in self.reg_sizes:
                    raise ValueError(f"Unknown register size for '{t.reg}'")
                size = self.reg_sizes[t.reg]
                return [IRQubit(t.reg, i) for i in range(size)]
            elif isinstance(t.index, tuple):
                start, end = t.index
                if start <= end:
                    return [IRQubit(t.reg, i) for i in range(start, end + 1)]
                else:
                    return [IRQubit(t.reg, i) for i in range(start, end - 1, -1)]
        return [t]