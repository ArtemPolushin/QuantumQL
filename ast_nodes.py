class Program:
    def __init__(self, statements):
        self.statements = statements


class CreateQubits:
    def __init__(self, name, size):
        self.name = name
        self.size = size

class QubitRef:
    def __init__(self, register, index):
        self.register = register
        self.index = index

class ApplyGate:
    def __init__(self, gate, targets):
        self.gate = gate
        self.targets = targets

class Measure:
    def __init__(self, targets):
        self.targets = targets

class GateDef:
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body

class SelectQuery:
    def __init__(self, register, condition):
        self.register = register
        self.condition = condition