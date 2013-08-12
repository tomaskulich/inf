import python_lexer
import python_parser as parser
import utils

f = open('samples/sample_prednaska.py')
data = f.read()
f.close()
lexer = python_lexer.PythonLexer()
lexer.input(data)
for token in lexer:
    print(token.value)
res=parser.parse_data(data, lexer)

#for node in res:
    #if isinstance(node, utils.Node) and (node.kind=='classdef' or node.kind=='funcdef'):
    #if isinstance(node, utils.Node) and (node.kind=='block'):
    #    print('@'*50)
    #    print(utils.node_to_str(node))

#print(utils.node_to_str(res))

print(utils.node_to_tree(res))
utils.traverse_ast(res)
print("-----ONLY VALID PART-----")  
print(utils.node_to_str(res))

try:
    ast_tree = utils.parse_with_ast(res)
    print(utils.astNode_to_tree(ast_tree))
except Exception as error:
    print("Error in part which should be valid: ",error)
