OPENQASM 3.0;
include "stdgates.inc";

input float theta;
qubit[6] q;
bit[6] q_c;

rx(theta) q[0];
rx(theta) q[2];
rx(theta) q[4];
x q[0];
x q[3];
z q[0];
z q[4];
rz(1.5707963268) q[0];
measure q -> q_c;