'''
Created on May 3, 2013

@author: Lubo
'''
import unittest
import PythonParser
from PythonParser import PParser

class TestParser(unittest.TestCase):
    
    def setUp(self):
        pass
    
    
    def test_simple_parse(self):
        code="""
import ast
nieco = 10
"""
        my_parser = PParser(code,False)
        #print(my_parser.output)
        self.assertEqual(len(my_parser.output), 4)
        self.assertEqual(len(my_parser.output_list), 1)
        self.assertIsInstance(my_parser.output, tuple)
        self.assertIsInstance(my_parser.output_list, list)
        
        
    def test_simple_one_def(self):
        code="""
import ast
nieco = 10

def pokus():
    premenna = 10
"""     
        my_parser = PParser(code,False)
        self.assertEqual(len(my_parser.output), 6)
        self.assertEqual(len(my_parser.output_list), 2)
        
        
    def test_simple_def_return(self):
        code="""
def pokus():
    premenna = 10
    return premenna
"""     
        my_parser = PParser(code,False)
        self.assertEqual(my_parser.output_list[0], "def pokus():\n")
        self.assertEqual(my_parser.output_list[1], ['premenna = 10\n', 'return premenna\n'])
        #print(my_parser.output_list)
        #print(PythonParser.print_my_list(my_parser.output_list, 0))
        
        
    def test_wrong_indent_leveL(self):
        code="""
def pokus():
return 5        
"""
        self.assertRaises(IndentationError, PParser, code, False)
    
    
    def test_wrong_indent_complex(self):
        code="""
class moja():
    def moja_funkcia():
        def moja_dalsia_funkcia():
        return 0
    return 1        
"""    
        self.assertRaises(IndentationError, PParser, code, False)
        
    def test_wrong_def(self):
        code="""
de pokus(:
    return 55        
"""
        self.assertRaises(IndentationError, PParser, code, False)
        
    def test_ast(self):
        code="""
de pokus():
    return 55        
"""
        
        my_parser = PParser(code,False)
        err,out = my_parser.parse_with_ast()
        #print(err[0])
        #print(out)
        self.assertEqual(str(err[0]), "invalid syntax (<unknown>, line 1)")
    
if __name__ == '__main__':
    unittest.main()
    