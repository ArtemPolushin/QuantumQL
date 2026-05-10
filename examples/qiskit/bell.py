from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit import Parameter
import math

q = QuantumRegister(2, "q")
q_c = ClassicalRegister(2, "q_c")
qc = QuantumCircuit(q, q_c)
qc.h(q[0])
qc.cx(q[0], q[1])
qc.measure(q, q_c)