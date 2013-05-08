'''
Created on Apr 24, 2013

@author: Lubo
'''
from ply import yacc
import MyLexer1
tokens = MyLexer1.tokens

#SKUSIT TO CEZ TOKENY
# file_input: (NEWLINE | stmt)* ENDMARKER
def p_file_input(p):
    '''
    file_input : ENDMARKER
      | file_input_star ENDMARKER
    '''
    if len(p) == 3:
        #p[0] = (p[1],p[2])
        p[0] = (p[1])
        #print()
    else:
        p[0] = p[1]

def p_file_input_star(p):
    '''
    file_input_star : NEWLINE
      | stmt
      | file_input_star NEWLINE
      | file_input_star stmt
    '''
    if len(p) == 3:
        #print("OUTPUT:",p[2])
        #p[0] = ("EXP",)
        #-----------------------
        #p[0] = (p[1]+p[2])
        p[0] = tuple(p[1])+tuple(p[2])
    else:
        #print("VOLA SA ?")
        p[0] = p[1]
  
def p_funcdef(p):
    '''
    funcdef : DEF STATEMENT COLON suite
            | DEF STATEMENT args COLON suite
    '''
    if len(p) == 6:
        p[0] = ("funcdef",(p[1],p[2],p[3],p[4],p[5]))
    else:
        p[0] = ("funcdef",(p[1],p[2],p[3],p[4]))

def p_classdef(p):
    '''
    classdef : CLASS STATEMENT COLON suite
            | CLASS STATEMENT args COLON suite
    '''
    if len(p) == 6:
        p[0] = ("classdef",(p[1],p[2],p[3],p[4],p[5]))
    else:
        p[0] = ("classdef",(p[1],p[2],p[3],p[4]))
    
def p_conddef(p):
    '''
    conddef : STATEMENT COLON suite
            | STATEMENT args COLON suite
    '''
    if len(p) == 5:
        p[0] = ("conddef",(p[1],p[2],p[3],p[4]))
    else:
        p[0] = ("conddef",(p[1],p[2],p[3]))
    #print(p[0])
    
def p_args(p):
    '''
    args : LPAR RPAR
        | LPAR stmt RPAR
        | stmt
    '''
    if len(p) == 4:
        p[0] = ("args",(p[1],p[2],p[3]))
    elif len(p) == 3:
        p[0] = (p[1]+p[2])
    else:
        p[0] = (p[1])
    
def p_suite(p):
    '''
    suite : stmt
      | NEWLINE INDENT suite_plus DEDENT
    '''
    if len(p) == 5:
        #tu bolo p[1] namiesto \n a p[2] namiesto \\t
        #p[0] = ("\\n"+" "+"\\t",p[3],p[4])
        p[0] = p[1],p[2],p[3]
    else:
        p[0] = (p[1])
    
def p_stmt(p):
    '''
    stmt : STATEMENT
        | STATEMENT args
        | STATEMENT NEWLINE
        | STATEMENT args NEWLINE
        | funcdef
        | classdef
        | conddef
        | COMMENT
    '''
    if len(p) == 4:
        p[0] = (p[1],p[2],p[3])
    elif len(p) == 3:
        p[0] = (p[1],p[2])
    else:
        p[0] = (p[1])
    
def p_suite_plus(p):
    '''
    suite_plus : stmt
      | suite_plus stmt
    '''
    if len(p) == 3:
        p[0] = p[1]+tuple(p[2])
    else:
        p[0] = p[1]

def p_error(e):
    print('error: %s'%e)
    
def ParseFile(filename,lexer):
    f = open(filename)
    data = f.read()
    yacc.yacc()
    result = yacc.parse(data, lexer)
    return result

def ParseInput(my_input,lexer):
    data = my_input
    yacc.yacc()
    result = yacc.parse(data, lexer)
    return result