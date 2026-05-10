from ir.ir_classes import *

class RangeEngine:
    def __init__(self):
        self.reg_sizes = {}
    
    def expand(self, ir: IRProgram):
        for stmt in ir.body:
            if isinstance(stmt, IRCreateQubits):
                self.reg_sizes[stmt.name] = stmt.size
            elif isinstance(stmt, IRCreateBits):
                self.reg_sizes[stmt.name] = stmt.size
        out = []
        for stmt in ir.body:
            if isinstance(stmt, IRCreateQubits):
                out.append(stmt)
            elif isinstance(stmt, IRApply):
                out.extend(self._expand_apply(stmt))
            elif isinstance(stmt, IRMeasure):
                out.append(self._expand_measure(stmt))
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
                resolved = self._resolve_negative(t.reg, t.index)
                return [IRQubit(t.reg, resolved)]
            elif t.index == "*":
                if t.reg not in self.reg_sizes:
                    raise ValueError(f"Unknown register size for '{t.reg}'")
                size = self.reg_sizes[t.reg]
                return [IRQubit(t.reg, i) for i in range(size)]
            elif isinstance(t.index, tuple):
                start, end = t.index
                start = self._resolve_negative(t.reg, start)
                end = self._resolve_negative(t.reg, end)
                if t.reg in self.reg_sizes:
                    size = self.reg_sizes[t.reg]
                    for i in (start, end):
                        if i < 0 or i >= size:
                            raise ValueError(
                                f"Index {i} out of range for register '{t.reg}' of size {size}"
                            )
                if start <= end:
                    return [IRQubit(t.reg, i) for i in range(start, end + 1)]
                else:
                    return [IRQubit(t.reg, i) for i in range(start, end - 1, -1)]
        return [t]
    
    def _resolve_negative(self, reg: str, index: int) -> int:
        if index < 0:
            if reg not in self.reg_sizes:
                raise ValueError(f"Unknown register '{reg}' for negative index")
            size = self.reg_sizes[reg]
            resolved = size + index
            if resolved < 0:
                raise ValueError(
                    f"Negative index {index} out of range for register '{reg}' of size {size}"
                )
            return resolved
        return index
    
    def _expand_measure(self, stmt: IRMeasure):
        if (stmt.target is None and len(stmt.source) == 1 and isinstance(stmt.source[0], IRQubit) and stmt.source[0].index is None):
            return stmt
        def expand_side(targets):
            res = []
            for t in targets:
                if isinstance(t, IRQubit) and t.index is None:
                    size = self.reg_sizes.get(t.reg)
                    if size is None:
                        raise ValueError(f"Unknown register size for '{t.reg}' in measure")
                    res.extend([IRQubit(t.reg, i) for i in range(size)])
                else:
                    res.extend(self._expand_target_to_list(t))
            return res

        new_source = expand_side(stmt.source)
        new_target = expand_side(stmt.target) if stmt.target else None

        if new_target is not None and len(new_source) != len(new_target):
            raise ValueError(
                f"Measure source and target count mismatch: "
                f"{len(new_source)} vs {len(new_target)}"
            )

        return IRMeasure(source=new_source, target=new_target)