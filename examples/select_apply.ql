CREATE QUBITS q[6];

APPLY H ON q[0];

SELECT marked FROM q WHERE index < 2;
APPLY X ON marked;

SELECT marked FROM q WHERE index <= 4 AND index % 3 == 0;
APPLY H ON marked;

MEASURE q;