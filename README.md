# QuantumQL

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
## Запуск симулятора
```bash
python run_qiskit_sim.py <путь к файлу>
python run_openqasm_sim.py <путь к файлу>
```
