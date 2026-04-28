CREATE QUBITS q[4];
CREATE QUBITS oracle[1];

APPLY H ON q[*];

SELECT marked FROM q WHERE index < 2;
APPLY Z ON marked;

APPLY H ON q[*];
APPLY X ON q[*];
APPLY H ON q[3];
APPLY X ON q[0], q[1], q[2];
APPLY H ON q[3];
APPLY X ON q[*];
APPLY H ON q[*];

MEASURE q;