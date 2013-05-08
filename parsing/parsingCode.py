RESERVED = {
  "def": "DEF",
  "if": "IF",
  "return": "RETURN",
  "class" : "CLASS"
  }

tokens = (
    "CLASS",
    "DEF",
    "IF",
    "RETURN",
    "NAME",
    "NEWLINE",
    "COMMENT",
  #  "WS",
    "STATEMENT",
    "LPAR",
    "RPAR",
    "COLON",
    "ENDMARKER",
    "COMMA"
    )

t_CLASS = r'class'
t_COLON = r':'
t_COMMA = r','

def t_NAME(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = RESERVED.get(t.value, "NAME")
    return t

def t_STATEMENT(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = RESERVED.get(t.value, "STATEMENT")    # Check for reserved words
    return t

def t_COMMENT(t):
    r"[ ]*\043[^\n]*"  # \043 is '#'
    return t

#def t_COMMENT(t):
#    r'\#.*'
#    return t
    # No return value. Token discarded

#def t_WS(t):
#    r' [ ]+ '
#    if t.lexer.at_line_start and t.lexer.paren_count == 0:
#        return t

def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")
    return t

# Ignored characters: whitespace
t_ignore = " \t"

def t_LPAR(t):
    r'\('
    t.lexer.paren_count += 1
    return t

def t_RPAR(t):
    r'\)'
    # check for underflow?  should be the job of the parser
    t.lexer.paren_count -= 1
    return t

#def t_error(t):
#    print ("Illegal character ’%s’" % t.value[0])
#    t.lexer.skip(1)

def t_error(t):
    raise SyntaxError("Unknown symbol %r" % (t.value[0],))
    print ("Skipping", repr(t.value[0]))
    t.lexer.skip(1)

import ply.lex as lex
lex.lex()

# I use the Python AST
import ast

#parsing rules

#def p_file_input_end(p):
#    """file_input_end : file_input ENDMARKER"""
#    p[0] = ast.Stmt(p[1])

def p_file_input(p):
    """file_input : file_input NEWLINE
                  | file_input stmt
                  | NEWLINE
                  | stmt"""
    if isinstance(p[len(p)-1], basestring):
        if len(p) == 3:
            p[0] = p[1]
        else:
            p[0] = [] # p == 2 --> only a blank line
    else:
        if len(p) == 3:
            p[0] = p[1] + p[2]
        else:
            p[0] = p[1]

def p_funcdef(p):
   "funcdef : DEF NAME parameters COLON suite"
   p[0] = ast.Function(None, p[2], tuple(p[3]), (), 0, None, p[5])

def p_parameters(p):
    """parameters : LPAR RPAR
                  | LPAR varargslist RPAR"""
    if len(p) == 3:
        p[0] = []
    else:
        p[0] = p[2]

def p_varargslist(p):
    """varargslist : varargslist COMMA NAME
                   | NAME"""
    if len(p) == 4:
        p[0] = p[1] + p[3]
    else:
        p[0] = [p[1]]

def p_suite(p):
    """suite : simple_stmt
            | NEWLINE stmts"""
    if len(p) == 2:
        p[0] = ast.Stmt(p[1])
    else:
        p[0] = ast.Stmt(p[3])

def p_simple_stmt(p):
    """simple_stmt : stmt NEWLINE"""
    p[0] = p[1]

def p_stmts(p):
    """stmts : stmts stmt
             | stmt"""
    if len(p) == 3:
        p[0] = p[1] + p[2]
    else:
        p[0] = p[1]

def p_stmt(p):
    """stmt : STATEMENT"""
           # | funcdef"""
    # simple_stmt is a list
    p[0] = p[1]

#def p_program(p):
#    '''program : program STATEMENT
#               | program NEWLINE
#               | STATEMENT'''
#    if len(p) == 2:
#        p[0] = [p[1]]
#    else:
#        p[0] = p[1]
#        p[0].append(p[2])
#    print(p)
#    #print(p[1])
#    #print(p[2])
#def p_statement(t):
#    '''statement : CLASS STATEMENT NEWLINE
#                 | FUNCDEF STATEMENT NEWLINE
#                 | COMMENT
#                 | STATEMENT'''

#def p_error(t):
#    print("Syntax error at '%s'" % t.value)

def p_error(e):
    print('error: %s'%e)

import ply.yacc as yacc
yacc.yacc()
                    
f= open("input_for_ply.py", "r")
data = f.read()
result = yacc.parse(data)
print(result)
# Test it out
#data = '''class
#          #comment
#          def'''

# Give the lexer some input
#lex.input(data)

# Tokenize
#while True:
#    tok = lex.token()
#    if not tok: break      # No more input
#    print(tok)