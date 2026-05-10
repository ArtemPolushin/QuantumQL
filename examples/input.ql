CONST N = 8;
INPUT A;
INPUT B;
CREATE QUBITS q[N];
CREATE BITS c[N];

SELECT first_half FROM q WHERE index < N/2;
SELECT second_half FROM q WHERE index >= N/2;
SELECT every_third FROM q WHERE index % 3 == 0;

APPLY H ON ALL FROM first_half;
APPLY X ON ALL FROM second_half;
APPLY Z ON ALL FROM every_third;

GATE entangle(a, b) {
    APPLY H ON a;
    APPLY CX ON a, b;
}

APPLY entangle ON q[0:3], q[-4:-1];
MEASURE q -> c;