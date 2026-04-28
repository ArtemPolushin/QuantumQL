-- определение пользовательского гейта
GATE BELL(a, b) {
    APPLY H ON a;
    APPLY CX ON a, b;
}

-- создание регистров
CREATE QUBITS q[4];
CREATE QUBITS anc[3];
CREATE BITS measure_bit[1];

-- применение гейтов с выражениями
APPLY H ON q[0];
APPLY RX(pi/2) ON q[1];
APPLY RZ(pi) ON q[2];

-- select и групповая операция
SELECT even FROM q WHERE index % 2 == 0;
APPLY H ON even;

-- использование пользовательского гейта
APPLY BELL ON q[0], anc[0];

-- групповые операции с диапазонами
APPLY CX ON q[0:2], anc[0:2];
APPLY H ON q[*];

-- измерение
MEASURE anc[0] -> measure_bit[0];