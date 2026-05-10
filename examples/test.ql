CREATE QUBITS q[4];
CREATE QUBITS anc[3];
CREATE BITS measure_bit[7];
-- Параметр, задаваемый при запуске
INPUT phi;
-- H на всех кубитах q
APPLY H ON q[*];
-- Параметризованные гейты с математическими выражениями
APPLY RX(cos(pi)) ON q[1];
APPLY RZ(phi / 2) ON q[2];

-- SELECT и ALL FROM 
SELECT even FROM q WHERE index % 2 == 0;
APPLY H ON even;
APPLY X ON ALL FROM q WHERE index > 0 AND index + 1 != 2;
-- Групповая операция и диапазон
APPLY CX ON q[0:2], anc[0:2];

-- Измерение в диапазоны классического регистра
MEASURE q -> measure_bit[0:3];
MEASURE anc -> measure_bit[4:6];