# QuantumQL

**QuantumQL** — декларативный SQL-подобный язык для описания квантовых алгоритмов и транслятор, преобразующий программы в код на OpenQASM 3.0 и Python (Qiskit).

## Установка
```bash
git clone https://github.com/ArtemPolushin/QuantumQL.git
cd <путь к папке с репозиторием>
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

```

## Запуск
```bash
python cli.py <входной_файл> <qiskit|openqasm> <выходной_файл>
```

## Тестирование
```bash
pytest -v
pytest -v tests/test_cli.py
```
## Запуск на квантовом симуляторе
```bash
python run_qiskit_sim.py <путь к файлу>
python run_openqasm_sim.py <путь к файлу> --params alpha=0.5 beta=1.5
```
