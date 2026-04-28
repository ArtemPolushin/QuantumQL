OPENQASM 3.0;
include "stdgates.inc";
qubit[3] q;
bit[3] q_c;

h q[0];
cx q[0], q[1];
cx q[1], q[2];
measure q -> q_c;