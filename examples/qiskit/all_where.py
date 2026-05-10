from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit import Parameter
import math

theta = Parameter("theta")

q = QuantumRegister(6, "q")
q_c = ClassicalRegister(6, "q_c")
qc = QuantumCircuit(q, q_c)
qc.rx(theta, q[0])
qc.rx(theta, q[2])
qc.rx(theta, q[4])
qc.x(q[0])
qc.x(q[3])
qc.z(q[0])
qc.z(q[4])
qc.rz(1.5707963268, q[0])
qc.measure(q, q_c)