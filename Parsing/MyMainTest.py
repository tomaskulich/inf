'''
Created on May 1, 2013

@author: Lubo
'''
import PythonParser
from PythonParser import print_my_list
import Tree

#File we're checking for input
filename = "input_for_ply.py"

#Create instance of class
my_parser = PythonParser.PParser(filename, True)

#To print token values uncomment the next line
my_parser.print_tokens(filename)

#Print output from parser
print(my_parser.output,"\n")
print(type(my_parser.output[1][1]),"\n")

#Tree.treeprint(my_parser.output)
#Print list created from output
print(my_parser.output_list)
print(type(my_parser.output_list[0]))
print(print_my_list(my_parser.output_list, 0))
#err,out = my_parser.parse_with_ast()
#print(err)

