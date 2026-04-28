from ir.ir_classes import *
import math

class IRLowering:
    def __init__(self):
        self.env = {}

    def lower(self, ir_program):
        for stmt in ir_program.body:
            if isinstance(stmt, IRGateDef):
                self.env[stmt.name] = stmt

        out = []
        for stmt in ir_program.body:
            if isinstance(stmt, IRApply):
                out.extend(self._apply(stmt))
            else:
                out.append(stmt)

        return IRProgram(out)
    def _apply(self, stmt, depth=0):
        if depth > 10:
            raise RecursionError("Infinite gate expansion detected")
        if stmt.gate in self.env:
            expanded = self._expand_user_gate(stmt)

            result = []
            for s in expanded:
                if isinstance(s, IRApply):
                    result.extend(self._apply(s, depth+1))
                else:
                    result.append(s)

            return result

        return [stmt]
    def _expand_user_gate(self, stmt):
        gate = self.env[stmt.gate]
        param_map = {}
        target_map = {}

        for i, p in enumerate(stmt.params):
            param_map[gate.params[i]] = p

        for i, t in enumerate(stmt.targets):
            target_map[gate.params[len(stmt.params) + i]] = t

        result = []

        for s in gate.body:
            result.append(self._subst(s, param_map, target_map))

        return result
    def _subst(self, stmt, param_map, target_map):
        if isinstance(stmt, IRApply):
            return IRApply(
                gate=stmt.gate,
                params=[
                    self._resolve_value(p, param_map)
                    for p in stmt.params
                ],
                targets=[
                    self._resolve_target(t, target_map)
                    for t in stmt.targets
                ]
            )

        return stmt
    def _resolve_value(self, t, param_map):
        if isinstance(t, IRNumber):
            return t
        if isinstance(t, IRVar):
            if t.name in param_map:
                value = param_map[t.name]
                if isinstance(value, IRConst) and value.name == 'pi':
                    return IRNumber(math.pi)
                return value
            return t
        if isinstance(t, IRBinOp):
            return IRBinOp(
                self._resolve_value(t.left, param_map),
                t.op,
                self._resolve_value(t.right, param_map)
            )
        if isinstance(t, IRUnaryOp):
            return IRUnaryOp(
                t.op,
                self._resolve_value(t.expr, param_map)
            )
        return t
    def _resolve_target(self, t, target_map):
        if isinstance(t, IRQubit):
            if t.reg in target_map:
                return target_map[t.reg]
            return t

        return t