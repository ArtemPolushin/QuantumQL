CREATE QUBITS q[3];

APPLY H ON q[0];

SELECT marked FROM q WHERE index < 2;
APPLY CX ON marked;

SELECT marked FROM q WHERE index <= 2 AND index != 0;
APPLY CX ON q[1], q[2];

MEASURE q;