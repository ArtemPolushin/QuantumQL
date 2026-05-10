from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit import Parameter
import math

theta = Parameter("theta")
phi = Parameter("phi")

q = QuantumRegister(4, "q")
q_c = ClassicalRegister(4, "q_c")
qc = QuantumCircuit(q, q_c)
qc.ry(theta, q[0])
qc.ry(theta, q[2])
qc.rz(phi, q[1])
qc.rz(phi, q[3])
qc.cx(q[0], q[1])
qc.cx(q[1], q[2])
qc.cx(q[2], q[3])
qc.measure(q, q_c)