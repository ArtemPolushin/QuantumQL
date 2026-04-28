OPENQASM 3.0;
include "stdgates.inc";
qubit[1] qx;
qubit[1] qy;
bit[1] qx_c;
bit[1] qy_c;

h qx[0];
x qy[0];
h qy[0];
cx qx[0], qy[0];
h qx[0];
measure qx -> qx_c;