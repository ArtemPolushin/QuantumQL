CREATE QUBITS a[4];
CREATE QUBITS b[4];
CREATE QUBITS cin[1];
CREATE QUBITS cout[1];
-- MAJORITY FUNCTION
GATE MAJORITY(a,b,c) {

    APPLY CX ON c, b;
    APPLY CX ON c, a;
    APPLY CCX ON a, b, c;
}
-- UNMAJ FUNCTION
GATE UNMAJ(a,b,c) {
    APPLY CCX ON a,b,c;
    APPLY CX ON c,a;
    APPLY CX ON a,b;

}

APPLY X ON a[0];
APPLY X ON cin;
APPLY X ON b[0];

APPLY MAJORITY ON cin[0], b[0], a[0];

APPLY MAJORITY ON a[0:2], b[1:3], a[1:3];

APPLY CX ON a[3], cout[0];

APPLY UNMAJ ON a[2:0], b[1:3], a[1:3];

APPLY UNMAJ ON cin[0], b[0], a[0];

MEASURE a;
MEASURE b;