CREATE QUBITS q[6];
-- wildcard
APPLY H ON q[*];
-- Возрастающий диапазон
APPLY X ON q[0:2];
APPLY Y ON q[-3:-1];
-- Убывающий диапазон
APPLY Z ON q[3:1];
APPLY X ON q[-5:2];
-- Групповые операции индексы
APPLY SWAP ON q[-1:-5], q[0:4];

MEASURE q;