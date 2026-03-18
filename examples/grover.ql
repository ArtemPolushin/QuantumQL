CREATE QUBITS q[2];
CREATE QUBITS anc[1];

APPLY H ON q[*];
APPLY X ON anc[0];
APPLY H ON anc[0];

APPLY CCX ON q[0], q[1], anc[0];

APPLY H ON q[*];
APPLY X ON q[*];
APPLY H ON q[1];
APPLY CX ON q[0], q[1];
APPLY H ON q[1];
APPLY X ON q[*];
APPLY H ON q[*];

MEASURE q;