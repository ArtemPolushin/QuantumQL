import ply.yacc as yacc
from lexer import tokens
from ast_nodes import *

def p_program(p):
    "program : statement_list"
    p[0] = Program(p[1])

def p_statement_list(p):
    """
    statement_list : statement statement_list
                   | statement
    """
    if len(p) == 3:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = [p[1]]

def p_statement(p):
    """
    statement : create_stmt
              | apply_stmt
              | measure_stmt
              | gate_def
    """
    p[0] = p[1]

def p_create_stmt(p):
    "create_stmt : CREATE QUBITS IDENT LBRACKET INT RBRACKET SEMICOLON"
    p[0] = CreateQubits(p[3], p[5])

def p_condition_expr(p):
    """
    condition_expr : condition_expr AND condition_expr
                   | condition_expr OR condition_expr
                   | simple_condition
    """
    if len(p) == 4:
        p[0] = ('LOGIC', p[2].lower(), p[1], p[3])
    else:
        p[0] = p[1]



def p_number(p):
    """
    number : INT
           | FLOAT
    """
    p[0] = p[1]

def p_simple_condition(p):
    """
    simple_condition : IDENT LT number
                     | IDENT GT number
                     | IDENT LE number
                     | IDENT GE number
                     | IDENT EQ number
                     | IDENT NE number
    """
    p[0] = ('COND', p[1], p[2], p[3])

def p_apply_stmt(p):
    "apply_stmt : APPLY IDENT ON target_list SEMICOLON"
    p[0] = ApplyGate(p[2], p[4])

def p_measure_stmt(p):
    "measure_stmt : MEASURE target_list SEMICOLON"
    p[0] = Measure(p[2])

def p_target_list(p):
    """
    target_list : single_target target_tail
    """
    p[0] = [p[1]] + p[2]

def p_target_tail(p):
    """
    target_tail : COMMA single_target target_tail
                | empty
    """
    if len(p) == 4:
        p[0] = [p[2]] + p[3]
    else:
        p[0] = []

def p_single_target(p):
    """
    single_target : qubit
                  | IDENT WHERE condition_expr
    """
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = QubitRef(p[1], SelectQuery(p[1], p[3]))

def p_qubit_param(p):
    "qubit : IDENT"
    p[0] = QubitRef(p[1], None)

def p_qubit_index(p):
    "qubit : IDENT LBRACKET INT RBRACKET"
    p[0] = QubitRef(p[1], p[3])

def p_qubit_star(p):
    "qubit : IDENT LBRACKET STAR RBRACKET"
    p[0] = QubitRef(p[1], "*")

def p_qubit_range(p):
    "qubit : IDENT LBRACKET INT COLON INT RBRACKET"
    p[0] = QubitRef(p[1], (p[3], p[5]))

def p_gate_def(p):
    "gate_def : GATE IDENT LPAREN param_list RPAREN LBRACE statement_list RBRACE"
    p[0] = GateDef(p[2], p[4], p[7])

def p_param_list(p):
    "param_list : IDENT param_tail"
    p[0] = [p[1]] + p[2]

def p_param_tail(p):
    """
    param_tail : COMMA IDENT param_tail
               | empty
    """
    if len(p) == 4:
        p[0] = [p[2]] + p[3]
    else:
        p[0] = []

def p_empty(p):
    "empty :"
    pass

def p_error(p):
    if p:
        raise SyntaxError(f"Syntax error at '{p.value}' line {p.lineno}")
    else:
        raise SyntaxError(f"Unexpected end of input")

parser = yacc.yacc()