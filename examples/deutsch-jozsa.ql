CREATE QUBITS qx[1];
CREATE QUBITS qy[1];

APPLY H ON qx[*];
APPLY X ON qy[0];
APPLY H ON qy[*];

APPLY CX ON qx[0], qy[0];

APPLY H ON qx[*];

MEASURE qx;