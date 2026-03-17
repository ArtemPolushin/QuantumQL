import pytest
from lexer import lexer


def tokenize(data):
    lexer.input(data)
    tokens = []

    while True:
        tok = lexer.token()
        if not tok:
            break
        tokens.append((tok.type, tok.value))

    return tokens

@pytest.mark.parametrize("word,token_type", [
    ("create", "CREATE"),
    ("qubits", "QUBITS"),
    ("apply", "APPLY"),
    ("on", "ON"),
    ("measure", "MEASURE"),
    ("gate", "GATE"),
    ("select", "SELECT"),
    ("where", "WHERE"),
])
def test_reserved_words(word, token_type):
    tokens = tokenize(word)
    assert tokens[0][0] == token_type

@pytest.mark.parametrize("int", [
    "0",
    "1"
])
def test_ints(int):
    tokens = tokenize(int)
    assert tokens[0][0] == "INT"

@pytest.mark.parametrize("float", [
    "-3.1415",
    "9.99"
])
def test_floats(float):
    tokens = tokenize(float)
    assert tokens[0][0] == "FLOAT"

@pytest.mark.parametrize("identifier", [
    "q",
    "reg",
    "register1",
    "qubit_array",
    "a123"
])
def test_identifiers(identifier):
    tokens = tokenize(identifier)
    assert tokens[0][0] == "IDENT"

@pytest.mark.parametrize("symbol,token_type", [
    ("<", "LT"),
    (">", "GT"),
    ("=", "EQ"),
    ("*", "STAR"),
    (":", "COLON")
])
def test_operators(symbol, token_type):
    tokens = tokenize(symbol)
    assert tokens[0][0] == token_type

@pytest.mark.parametrize("symbol,token_type", [
    (",", "COMMA"),
    (";", "SEMICOLON")
])
def test_separators(symbol, token_type):
    tokens = tokenize(symbol)
    assert tokens[0][0] == token_type

@pytest.mark.parametrize("symbol,token_type", [
    ("[", "LBRACKET"),
    ("]", "RBRACKET"),
    ("(", "LPAREN"),
    (")", "RPAREN"),
    ("{", "LBRACE"),
    ("}", "RBRACE")
])
def test_brackets(symbol, token_type):
    tokens = tokenize(symbol)
    assert tokens[0][0] == token_type

def test_comment():
    data = "create qubits q[2]; -- comment"

    tokens = tokenize(data)
    types = [t[0] for t in tokens]

    assert "CREATE" in types
    assert "QUBITS" in types

def test_whitespace():
    data = "create   qubits   q[2] ;"

    tokens = tokenize(data)

    assert tokens[0][0] == "CREATE"
    assert tokens[1][0] == "QUBITS"

def test_illegal_character():
    bad_input = "CREATE qubits q0 @ q1;"
    
    lexer.input(bad_input)
    
    with pytest.raises(SyntaxError) as exc_info:
        while True:
            tok = lexer.token()
            if not tok:
                break

    assert "@" in str(exc_info.value)
    assert "line" in str(exc_info.value)