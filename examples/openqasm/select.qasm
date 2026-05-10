OPENQASM 3.0;
include "stdgates.inc";

input float theta;
input float phi;
qubit[4] q;
bit[4] q_c;

ry(theta) q[0];
ry(theta) q[2];
rz(phi) q[1];
rz(phi) q[3];
cx q[0], q[1];
cx q[1], q[2];
cx q[2], q[3];
measure q -> q_c;