import python_lexer
import parser
import utils

f = open('sample_prednaska.py')
data = f.read()
f.close()
lexer = python_lexer.PythonLexer()
lexer.input(data)
for token in lexer:
    print(token.value)
res=parser.parse_data(data, lexer)
for node in res:
    if isinstance(node, utils.Node) and (node.kind=='classdef' or node.kind=='funcdef'):
        print(utils.node_to_str(node))

#print(utils.node_to_str(res))
