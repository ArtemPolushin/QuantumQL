import ply.lex as lex

tokens = (
    'CREATE','QUBITS','APPLY','ON','MEASURE',
    'GATE','SELECT','WHERE',
    'AND','OR', 'FROM',
    'STAR','COLON', 'ARROW',
    'LT','GT','EQEQ','NE','LE','GE', 'ASSIGN',
    'PLUS','MINUS','DIVIDE','POWER', 'PERCENT',
    'PI', 'SIN', 'COS', 'TAN', 'EXP', 'LOG', 'SQRT', 'ABS',
    'ASIN', 'ACOS', 'ATAN',
    'IDENT','INT','FLOAT',
    'LBRACKET','RBRACKET',
    'LPAREN','RPAREN',
    'LBRACE','RBRACE',
    'COMMA','SEMICOLON',
    'INPUT'
)

reserved = {
    'create':'CREATE',
    'qubits':'QUBITS',
    'apply':'APPLY',
    'on':'ON',
    'measure':'MEASURE',
    'gate':'GATE',
    'select':'SELECT',
    'where':'WHERE',
    'and':'AND',
    'or':'OR',
    'from':'FROM',
    'pi':'PI',
    'sin':'SIN',
    'cos':'COS',
    'tan':'TAN',
    'exp':'EXP',
    'log':'LOG',
    'sqrt':'SQRT',
    'abs':'ABS',
    'asin':'ASIN',
    'acos':'ACOS',
    'atan':'ATAN',
    'input':'INPUT'
}

t_LE = r'<='
t_GE = r'>='
t_NE = r'!='
t_LT = r'<'
t_GT = r'>'
t_EQEQ = r'=='
t_ASSIGN = r'='
t_PLUS   = r'\+'
t_MINUS  = r'-'
t_DIVIDE = r'/'
t_POWER  = r'\*\*'
t_PERCENT = r'%'
t_ARROW = r'->'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_COMMA = r','
t_SEMICOLON = r';'
t_STAR = r'\*'
t_COLON = r':'

t_ignore = ' \t'
def t_COMMENT(t):
    r'\-\-.*'
    pass

def t_FLOAT(t):
    r'-?(\d+\.\d*|\.\d+)'
    t.value = float(t.value)
    return t

def t_INT(t):
    r'-?\d+'
    t.value = int(t.value)
    return t

def t_IDENT(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value.lower(),'IDENT')
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    raise SyntaxError(f"Illegal character '{t.value[0]}' at line {t.lineno}")

lexer = lex.lex()