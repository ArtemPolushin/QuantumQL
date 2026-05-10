input theta;
CREATE QUBITS q[8];
CONST SIZE = 6;

CREATE QUBITS q[SIZE];

APPLY RX(theta) ON ALL FROM q WHERE index % 2 == 0;
APPLY X ON ALL FROM q WHERE index % 3 == 0;
APPLY Z ON ALL FROM q WHERE index % 4 == 0;

SELECT special FROM q WHERE index % 3 == 0 AND index % 2 == 0;
APPLY RZ(pi/2) ON ALL FROM special;


MEASURE q;