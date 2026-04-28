import ply.yacc as yacc
from lexer import tokens
from ast_nodes import *

precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('left', 'EQEQ', 'NE', 'LT', 'GT', 'LE', 'GE'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'STAR', 'DIVIDE', 'PERCENT'),
    ('right', 'POWER'),
    ('right', 'UMINUS'),
)

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
              | select_stmt
              | gate_def
              | input_stmt
    """
    p[0] = p[1]

def p_create_stmt(p):
    "create_stmt : CREATE QUBITS IDENT LBRACKET INT RBRACKET SEMICOLON"
    p[0] = CreateQubits(p[3], p[5])

def p_apply_stmt(p):
    "apply_stmt : APPLY gate_call ON target_list SEMICOLON"
    p[0] = ApplyGate(p[2][0], p[4], params=p[2][1])

def p_input_stmt(p):
    "input_stmt : INPUT IDENT SEMICOLON"
    p[0] = InputParam(p[2])

def p_gate_call(p):
    """
    gate_call : IDENT
              | IDENT LPAREN arg_list RPAREN
    """
    if len(p) == 2:
        p[0] = (p[1], [])
    else:
        p[0] = (p[1], p[3])

def p_select_stmt(p):
    """
    select_stmt : SELECT IDENT FROM IDENT where_clause SEMICOLON
    """
    p[0] = SelectStmt(p[2], p[4], p[5])

def p_where_clause(p):
    """
    where_clause : WHERE expr
                 | empty
    """
    if len(p) == 3:
        p[0] = p[2]
    else:
        p[0] = None

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
                  | select_expr
    """
    p[0] = p[1]

def p_select_expr(p):
    """
    select_expr : SELECT IDENT FROM IDENT where_clause
    """
    p[0] = SelectExpr(p[2], p[4], p[5])

def p_qubit(p):
    """
    qubit : IDENT
          | IDENT LBRACKET INT RBRACKET
          | IDENT LBRACKET STAR RBRACKET
          | IDENT LBRACKET INT COLON INT RBRACKET
    """
    if len(p) == 2:
        p[0] = QubitRef(p[1], None)
    elif len(p) == 5:
        if p[3] == "*":
            p[0] = QubitRef(p[1], "*")
        else:
            p[0] = QubitRef(p[1], p[3])
    else:  # len == 7
        p[0] = QubitRef(p[1], (p[3], p[5]))

def p_measure_stmt(p):
    """
    measure_stmt : MEASURE target_list ARROW target_list SEMICOLON
                 | MEASURE target_list SEMICOLON
    """
    if len(p) == 6:  # MEASURE q -> c;
        p[0] = Measure(p[2], p[4])
    else:  # MEASURE q;
        p[0] = Measure(p[2], None)

def p_gate_def(p):
    "gate_def : GATE IDENT LPAREN param_list RPAREN LBRACE statement_list RBRACE"
    p[0] = GateDef(p[2], p[4], p[7])

def p_param_list(p):
    """
    param_list : param_tail
               | empty
    """
    p[0] = p[1] if p[1] is not None else []

def p_param_tail(p):
    """
    param_tail : IDENT
               | IDENT COMMA param_tail
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]

def p_expr_bool(p):
    """
    expr : expr AND expr
         | expr OR expr
         | expr EQEQ expr
         | expr NE expr
         | expr LT expr
         | expr GT expr
         | expr LE expr
         | expr GE expr
    """
    p[0] = BinOp(p[1], p[2], p[3])

def p_expr_arith(p):
    """
    expr : expr PLUS expr
         | expr MINUS expr
         | expr STAR expr
         | expr DIVIDE expr
         | expr PERCENT expr
         | expr POWER expr
    """
    p[0] = BinOp(p[1], p[2], p[3])

def p_expr_unary(p):
    "expr : MINUS expr %prec UMINUS"
    p[0] = UnaryOp('-', p[2])

def p_expr_paren(p):
    "expr : LPAREN expr RPAREN"
    p[0] = p[2]

def p_expr_number(p):
    """
    expr : INT
         | FLOAT
    """
    if isinstance(p[1], int):
        p[0] = Number(float(p[1]))
    else:
        p[0] = Number(p[1])

def p_expr_const(p):
    "expr : PI"
    p[0] = Constant('pi')

def p_expr_var(p):
    "expr : IDENT"
    p[0] = Var(p[1])

def p_expr_funcall(p):
    """
    expr : SIN LPAREN arg_list RPAREN
         | COS LPAREN arg_list RPAREN
         | TAN LPAREN arg_list RPAREN
         | EXP LPAREN arg_list RPAREN
         | LOG LPAREN arg_list RPAREN
         | SQRT LPAREN arg_list RPAREN
         | ABS LPAREN arg_list RPAREN
         | ASIN LPAREN arg_list RPAREN
         | ACOS LPAREN arg_list RPAREN
         | ATAN LPAREN arg_list RPAREN
         | IDENT LPAREN arg_list RPAREN
    """
    func_name = p[1].lower() if isinstance(p[1], str) else p[1]
    p[0] = FuncCall(func_name, p[3])

def p_arg_list(p):
    """
    arg_list : expr_list
             | empty
    """
    p[0] = p[1] if p[1] is not None else []

def p_expr_list(p):
    """
    expr_list : expr
              | expr COMMA expr_list
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]

def p_empty(p):
    "empty :"
    p[0] = None

def p_error(p):
    if p:
        raise SyntaxError(f"Syntax error at '{p.value}' line {p.lineno}")
    else:
        raise SyntaxError("Unexpected EOF")

parser = yacc.yacc()