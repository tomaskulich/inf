from ply import (
        yacc,
        )
from utils import Node

import python_lexer
tokens = python_lexer.tokens



"""
parser ludskou recou:
    fragment: nejake hocico v jednom riadku
    stmt: fragment NEWLINE | classdef | funcdef | block
    suite: hocikolko stmt 
    indented_suite: INDENT suite DEDENT
    classdef: DEF stmt: NEWLINE indented_suite
    funcdef: DEF stmt: NEWLINE indented_suite
"""

def p_file_input(p):
    '''
    file_input : suite 
    '''
    p[0] = Node(kind='file_input', childs=p)

def p_block(p):
    '''
    block : block_keyword fragment COLON NEWLINE INDENT suite DEDENT
    '''
    p[0] = Node(kind='block', childs=p)

def p_empty_block(p):
    '''
    block : block_keyword fragment COLON NEWLINE 
    '''
    p[0] = Node(kind='block', childs=p)

def p_block_keyword(p):
    '''
    block_keyword : CLASS
                    | DEF
                    | IF
                    | ELIF
                    | ELSE
                    | TRY
                    | EXCEPT
                    | FINALLY
                    | WITH
                    | WHILE
                    | FOR
    '''
    p[0] = Node(kind='keyword', childs=p)

def p_suite(p):
    '''
    suite : stmt
          | suite stmt
    '''
    p[0]=Node(kind='suite', childs=p)

def p_stmt(p):
    '''
    stmt : fragment NEWLINE
         | fragment ENDMARKER
         | NEWLINE
         | ENDMARKER
         | block
    '''
    p[0]=Node(kind='stmt', childs=p)

def p_fragment(p):
    '''
    fragment : fragment LBRACE
         | fragment RBRACE
         | fragment STRING_END
         | fragment STRING_CONTINUE
         | fragment STRING
         | fragment STRING_START_TRIPLE
         | fragment WS 
         | fragment STRING_START_SINGLE
         | fragment NUMBER
         | fragment NAME
         | fragment LPAR
         | fragment RPAR
         | fragment OPERATOR
         | fragment LSQB
         | fragment RSQB
         | fragment COLON
         | LBRACE
         | RBRACE
         | STRING_END
         | STRING_CONTINUE
         | STRING
         | STRING_START_TRIPLE
         | WS 
         | STRING_START_SINGLE
         | NUMBER
         | NAME
         | LPAR
         | RPAR
         | LSQB
         | RSQB
         | COLON
         | OPERATOR
    '''
    p[0]=Node(kind='fragment', childs=p)

def p_error(e):
    print('error: %s'%e)
    
def parse_data(data,lexer):
    yacc.yacc()
    result = yacc.parse(data, lexer)
    return result
