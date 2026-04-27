class GateInfo:
    def __init__(self, name: str, num_qubits: int, has_params: bool = False):
        self.name = name
        self.num_qubits = num_qubits
        self.has_params = has_params

GATES = {
    "x": GateInfo("x", 1),
    "y": GateInfo("y", 1),
    "z": GateInfo("z", 1),
    "h": GateInfo("h", 1),
    "s": GateInfo("s", 1),
    "sdg": GateInfo("sdg", 1),
    "t": GateInfo("t", 1),
    "tdg": GateInfo("tdg", 1),
    "id": GateInfo("id", 1),
    
    "rx": GateInfo("rx", 1, True),
    "ry": GateInfo("ry", 1, True),
    "rz": GateInfo("rz", 1, True),
    "p": GateInfo("p", 1, True),
    "u1": GateInfo("u1", 1, True),
    "u2": GateInfo("u2", 1, True),
    "u3": GateInfo("u3", 1, True),
    "u": GateInfo("u", 1, True),
    
    "cx": GateInfo("cx", 2),
    "cy": GateInfo("cy", 2),
    "cz": GateInfo("cz", 2),
    "ch": GateInfo("ch", 2),
    "swap": GateInfo("swap", 2),
    "cnot": GateInfo("cx", 2),
    
    "cp": GateInfo("cp", 2, True),
    "crx": GateInfo("crx", 2, True),
    "cry": GateInfo("cry", 2, True),
    "crz": GateInfo("crz", 2, True),
    "cu1": GateInfo("cu1", 2, True),
    "cu3": GateInfo("cu3", 2, True),
    "rxx": GateInfo("rxx", 2, True),
    "ryy": GateInfo("ryy", 2, True),
    "rzz": GateInfo("rzz", 2, True),
    
    "ccx": GateInfo("ccx", 3),
    "cswap": GateInfo("cswap", 3),
    "toffoli": GateInfo("ccx", 3),
    "fredkin": GateInfo("cswap", 3),
    
    "measure": GateInfo("measure", 1),
    "barrier": GateInfo("barrier", -1),
    "reset": GateInfo("reset", 1),
}

SINGLE_QUBIT_GATES = {name for name, info in GATES.items() 
                      if info.num_qubits == 1}

MULTI_QUBIT_GATES = {name for name, info in GATES.items() 
                     if info.num_qubits > 1 or info.num_qubits == -1}

PARAM_GATES = {name for name, info in GATES.items() 
               if info.has_params}

def is_single_qubit_gate(gate_name: str) -> bool:
    gate_lower = gate_name.lower()
    return gate_lower in SINGLE_QUBIT_GATES

def get_gate_info(gate_name: str) -> GateInfo:
    gate_lower = gate_name.lower()
    if gate_lower not in GATES:
        return GateInfo(gate_lower, -1, False)
    return GATES[gate_lower]

def normalize_gate_name(gate_name: str) -> str:
    return gate_name.lower()

def gate_exists(gate_name: str) -> bool:
    return gate_name.lower() in GATES