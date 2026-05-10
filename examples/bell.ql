GATE BELL(a, b) {
    APPLY H ON a;
    APPLY CX ON a, b;
}

CREATE QUBITS q[2];
APPLY BELL ON q[0], q[1];

MEASURE q;