from ast_nodes import *
def resolve_select(self, select):
    register = select.register
    size = self.registers[register]

    def eval_condition(cond):
        if cond[0] == 'COND':
            field, op, value = cond[1:]
            if field != "value":
                raise ValueError("Unsupported select field")
            if op == "<": return list(range(0, value))
            if op == "<=": return list(range(0, value + 1))
            if op == ">": return list(range(value + 1, size))
            if op == ">=": return list(range(value, size))
            if op == "==": return [value]
            if op == "!=": return [i for i in range(size) if i != value]
            raise ValueError(f"Unsupported operator {op}")

        elif cond[0] == 'LOGIC':
            _, op, left, right = cond
            left_indices = set(eval_condition(left))
            right_indices = set(eval_condition(right))
            if op == 'and':
                return list(left_indices & right_indices)
            elif op == 'or':
                return list(left_indices | right_indices)
            else:
                raise ValueError(f"Unsupported logic operator {op}")
        else:
            raise ValueError(f"Unknown condition type {cond[0]}")

    return sorted(eval_condition(select.condition))

def expand_index(index, size):
    if index is None:
        return list(range(size))

    if index == "*":
        return list(range(size))

    if isinstance(index, tuple):

        start, end = index

        step = 1 if start <= end else -1

        return list(range(start, end + step, step))

    return [index]

def expand_targets(self, targets):

    expanded_lists = []

    for q in targets:

        if isinstance(q.index, SelectQuery):

            indices = resolve_select(self, q.index)

        else:

            size = self.registers[q.register]

            indices = expand_index(q.index, size)

        expanded_lists.append(
            [(q.register, i) for i in indices]
        )

    lengths = [len(x) for x in expanded_lists]

    max_len = max(lengths)

    for i, lst in enumerate(expanded_lists):

        if len(lst) == 1 and max_len > 1:
            expanded_lists[i] = lst * max_len

    lengths = [len(x) for x in expanded_lists]

    if len(set(lengths)) != 1:
        raise ValueError("Vector size mismatch in APPLY")

    result = []

    for i in range(max_len):

        group = []

        for lst in expanded_lists:
            group.append(lst[i])

        result.append(group)

    return result