OPENQASM 3.0;
include "stdgates.inc";
qubit[3] q;
bit[3] q_c;

h q[0];
cx q[1], q[0];
cx q[2], q[0];
h q[1];
cx q[2], q[1];
h q[2];
measure q -> q_c;