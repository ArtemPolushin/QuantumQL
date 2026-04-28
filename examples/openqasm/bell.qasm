OPENQASM 3.0;
include "stdgates.inc";
qubit[2] q;
bit[2] q_c;

h q[0];
cx q[0], q[1];
measure q -> q_c;