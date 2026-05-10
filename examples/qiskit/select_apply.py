from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit import Parameter
import math

q = QuantumRegister(6, "q")
q_c = ClassicalRegister(6, "q_c")
qc = QuantumCircuit(q, q_c)
qc.h(q[0])
qc.x(q[0])
qc.x(q[1])
qc.h(q[0])
qc.h(q[3])
qc.measure(q, q_c)