INPUT theta;
INPUT phi;
CONST N = 4;

CREATE QUBITS q[N];

APPLY RY(theta) ON ALL FROM q WHERE index % 2 == 0;
APPLY RZ(phi) ON ALL FROM q WHERE index % 2 == 1;

APPLY CX ON q[0:2], q[1:3];
MEASURE q;