from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
import math

qx = QuantumRegister(1, "qx")
qy = QuantumRegister(1, "qy")
qx_c = ClassicalRegister(1, "qx_c")
qy_c = ClassicalRegister(1, "qy_c")
qc = QuantumCircuit(qx, qy, qx_c, qy_c)
qc.h(qx[0])
qc.x(qy[0])
qc.h(qy[0])
qc.cx(qx[0], qy[0])
qc.h(qx[0])
qc.measure(qx, qx_c)