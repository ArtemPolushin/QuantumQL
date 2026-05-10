OPENQASM 3.0;
include "stdgates.inc";
qubit[6] q;
bit[6] q_c;

h q[0];
x q[0];
x q[1];
h q[0];
h q[3];
measure q -> q_c;