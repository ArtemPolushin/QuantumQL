from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
import math

q = QuantumRegister(3, "q")
q_c = ClassicalRegister(3, "q_c")
qc = QuantumCircuit(q, q_c)
qc.h(q[0])
qc.cx(q[0], q[1])
qc.cx(q[1], q[2])
qc.measure(q, q_c)