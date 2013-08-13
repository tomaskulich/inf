import unittest
import ast
import logging
from parse_ast import Parser
from typez import extern_scope
from  typez import (
        Scope,
        Typez,
        none_type
        )
import re

def makecode(code):
    return re.sub(r'[ \t]+\|','',code)

class TestResolve(unittest.TestCase): #{{{

    def setUp(self):
        pr_num = Typez(kind = 'prim', node = ast.Num())
        pr_str = Typez(kind = 'prim', node = ast.Str())
        self.scope = Scope(is_root = True)
        self.scope.update({'xxx':pr_str})

        scope1 = Scope(parent = self.scope)
        scope1.update({'a': pr_num, 'b': pr_str})
        self.type1 = Typez(kind = 'obj', scope = scope1)

        scope2 = Scope(parent = self.scope)
        scope2.update({'c': pr_num, 'd': pr_str})
        self.type2 = Typez(kind = 'obj', scope = scope2)
        self.type2 = scope2

        scope12 = Scope(parent = self.scope)
        scope12.update({'a':self.type1, 'b': self.type2})
        self.type12 = Typez(kind = 'obj', scope = scope12)

        self.scope.update({'type1':self.type1, 'type2': self.type2, 'type12': self.type12})

    def test_resolve_type1_in_scope(self):
        res = self.scope.resolve('type1', 'straight')
        self.assertEqual(res, self.type1)

    def test_resolve_in_type(self):
        res = self.type1.resolve('a', 'straight')
        self.assertEqual(res.kind,'prim')
        self.assertIsInstance(res.node, ast.Num)
        self.assertEqual(self.scope.resolve('c'), None)


    def test_resolve_cascade(self):
        self.assertRaises(Exception, self.type1.resolve, 'xxx','cascade')
        res1 = self.type1.scope.resolve('xxx','cascade')
        res2 = self.scope.resolve('xxx','straight')
        self.assertEqual(res1,res2)

    def test_resolve_class(self):
        num = self.type1.resolve('a', 'straight')
        self.assertRaises(Exception, num.resolve, '__add__', 'cascade')
        add = num.resolve('__add__', 'straight')
        self.assertEqual(add, None)
        add = num.resolve('__add__', 'class')
        self.assertIsInstance(add, Typez)
        self.assertEqual(add.kind, 'func')
        self.assertIsInstance(add.node, ast.FunctionDef)

#}}}

class TestScope(unittest.TestCase): #{{{
    def setUp(self):
        scope = Scope(is_root = True)
        scope['a'] = 'a'
        scope['b'] = 'b'
        child_scope = Scope(parent = scope)
        child_scope['c'] = 'c'
        self.scope = scope
        self.child_scope = child_scope

    def test_basic(self):
        self.assertEqual(self.scope.resolve('a', 'straight'), 'a')
        self.assertEqual(self.scope['a'], 'a')
        self.assertEqual(self.scope.resolve('a', 'cascade'), 'a')
        self.assertEqual(self.scope.resolve('c', 'cascade'), None)
        self.assertEqual(self.child_scope.resolve('a', 'straight'), None)
        self.assertEqual(self.child_scope.resolve('a', 'cascade'), 'a')
        self.assertEqual(self.child_scope.resolve('c', 'straight'), 'c')
        self.assertEqual(self.child_scope.resolve('c', 'cascade'), 'c')
        self.assertRaises(Exception, self.child_scope.resolve, 'c', 'class')

#}}}

class TestInfer(unittest.TestCase): #{{{


    def setUp(self):
        def assertIsNum(typez):
            self.assertIsInstance(typez, ast.Num)
        self.assertIsNum = assertIsNum
        def assertIsStr(typez):
            self.assertIsInstance(typez, ast.Str)
        self.assertIsStr = assertIsStr
   
    def test_simple_parse(self):
        code = makecode("""
            |x = 3
            |a = 'ahoj'
            |y = 6
            |z = 3+x
            |zz = x+y
            |b = 'jozo'
            |c = a+b
            |x = 'mumly'
        """)
        node = ast.parse(code, mode = 'exec')
        parser = Parser()
        module_scope = parser.eval_code(node)
        x = module_scope.resolve('x')
        y = module_scope.resolve('y')
        z = module_scope.resolve('z')
        zz = module_scope.resolve('zz')
        a = module_scope.resolve('a')
        b = module_scope.resolve('b')
        c = module_scope.resolve('c')
        self.assertIsStr(x.node)
        self.assertIsNum(y.node)
        self.assertIsNum(z.node)
        self.assertIsNum(zz.node)
        self.assertIsStr(a.node)
        self.assertIsStr(b.node)
        self.assertIsStr(c.node)

    def test_fun_parse(self):
        code = makecode("""
            |def mean(x,y):
            |    return (x+y)/2

            |def gean(x,y):
            |    return x+y

            |x = 3
            |y = x+2
            |z = mean(x,y)
            |x = "jozo"
            |zz = gean(x,"fero")
        """)
        node = ast.parse(code, mode = 'exec')
        parser = Parser()
        module_scope = parser.eval_code(node)
        x = module_scope.resolve('x')
        y = module_scope.resolve('y')
        z = module_scope.resolve('z')
        zz = module_scope.resolve('zz')
        self.assertIsStr(x.node)
        self.assertIsNum(y.node)
        self.assertIsNum(z.node)
        self.assertIsStr(zz.node)
    
    def test_default_object(self):
        code = makecode("""
            |class A():
            |   pass
            |a = A()
        """)
        node = ast.parse(code, mode = 'exec')
        parser = Parser()
        module_scope = parser.eval_code(node)
        a = module_scope.resolve('a')
        __setattr__ = a.resolve('__setattr__', 'straight')
        self.assertEqual(__setattr__, None)
        __setattr__ = a.resolve('__setattr__', mode = 'class')
        self.assertEqual(__setattr__.node.name, '__setattr__')

    def test_closure(self):
        code = makecode("""
            |def f(x):
            |    z = x
            |    def g(y):
            |        return(x+y)
            |    return g

            |g1 = f(3)
            |g2 = f('jozo')

            |a = g1(4)
            |b = g2('fero')
        """)
        node = ast.parse(code, mode = 'exec')
        parser = Parser()
        module_scope = parser.eval_code(node)
        a = module_scope.resolve('a')
        b = module_scope.resolve('b')
        self.assertIsNum(a.node)
        self.assertIsStr(b.node)


    def test_class(self):
        code = makecode("""
                |class A:
                |    def __init__(self, x, y, z):
                |        self.x = x
                |        self.y = y
                |a = A(3,"ahoj", "svet")
        """)
        node = ast.parse(code, mode = 'exec')
        parser = Parser()
        module_scope = parser.eval_code(node)
        a = module_scope.resolve('a')
        self.assertIsNum(a.scope['x'].node)
        self.assertIsStr(a.scope['y'].node)
        self.assertEqual(a.scope.resolve('z'),None)

    def test_override_setattr(self):
        code = makecode("""
            |class A:
            |    def __init__(self, x, y):
            |        pass
            |
            |    def __setattr__(self, attr, val):
            |        object.__setattr__(self, attr, 4)
            |
            |
            |a = A(3,4)
            |a.x = 'jozo'
            |key = 'z'
            |object.__setattr__(a,key,'jozo')
        """)
        node = ast.parse(code, mode = 'exec')
        parser = Parser()
        module_scope = parser.eval_code(node)
        a = module_scope.resolve('a')
        self.assertIsNum(a.scope['x'].node)
        self.assertIsStr(a.scope['z'].node)

    def test_method_lookup(self):
        code = makecode("""
            |class A:
            |    def __init__(self, x):
            |        self.x = x

            |    def get_x(self):
            |        return self.x

            |a = A('jozo')
            |b = a.get_x()
            |getx = a.get_x
            |a = A(3)
            |c = a.get_x()
        """)
        node = ast.parse(code, mode = 'exec')
        parser = Parser()
        module_scope = parser.eval_code(node)
        a = module_scope.resolve('a')
        A = module_scope.resolve('A')
        self.assertNotIn('get_x', a.scope)
        self.assertIn('get_x', A.scope)
        b = module_scope.resolve('b')
        c = module_scope.resolve('c')
        getx = module_scope.resolve('getx')
        self.assertIsStr(b.node)
        self.assertIsNum(c.node)
        self.assertEqual(getx.kind, 'func')

    def test_inheritance(self):
        code = makecode("""
           |class A:
           |    def __init__(self):
           |        pass
           |    def get_x(self):
           |        return self.x

           |class B(A):
           |    def __init__(self):
           |        pass
           |    def get_y(self):
           |        return self.y

           |b = B()
           |b.x = 'jozo'
           |b.y = 4
""")
        node = ast.parse(code, mode = 'exec')
        parser = Parser()
        module_scope = parser.eval_code(node)
        b = module_scope.resolve('b')
        self.assertIsNum(b.scope['y'].node)
        self.assertIsStr(b.scope['x'].node)
        self.assertEqual(b.resolve('get_x', 'class').kind, 'func')

#}}}

class TestWarnings(unittest.TestCase): #{{{
    
    def test_nonexistent_attribute(self):
        code = makecode("""
            |class A:
            |    def __init__(self, x, y):
            |        self.x = x
            |        self.y = y
            |a = A(3,4)
            |a.x = a.z
            |a.z = a.x
            |a.y = a.z
            |a.w = a.w
""")

        node = ast.parse(code, mode = 'exec')
        parser = Parser()
        parser.eval_code(node)
        problem_symbols = {problem.symbol for problem in parser.problems}
        self.assertEqual(problem_symbols, {'w', 'z'})

    def test_nonexistent_function(self):
        code = makecode("""
            |class A:
            |    def __init__(self, x, y):
            |        self.x = x
            |        self.y = y
            |
            |    def fun1(self):
            |        return self.x+self.y
            |a = A(3,4)
            |a.z = a.fun1()
            |a.gun1()
            |a.fun2 = a.fun1
            |a.fun2()
            |# since the problem with nonexistent gun1 is already reported, gun1 and gun2 are to be considered as
            |# any_type making all invocations and other manipulations with it legal
            |a.gun2 = a.gun1
            |a.gun2()
            |a.gun3()
""")

        node = ast.parse(code, mode = 'exec')
        parser = Parser()
        parser.eval_code(node)
        problem_symbols = {problem.symbol for problem in parser.problems}
        self.assertEqual(problem_symbols, {'gun1', 'gun3'})

    def test_nonexistent_class(self):
        code = makecode("""
            |class A:
            |    def __init__(self, x, y):
            |        self.x = x
            |        self.y = y
            |
            |class B:
            |  pass
            |
            |a = A(1,2)
            |b = B()
            |c = C()
            |#a = D()
""")

        node = ast.parse(code, mode = 'exec')
        parser = Parser()
        parser.eval_code(node)
        problem_symbols = {problem.symbol for problem in parser.problems}
        print(problem_symbols)
        #self.assertEqual(problem_symbols, {'gun1', 'gun3'})



#}}}

if __name__ == '__main__':
    #run_all = True
    run_all = False

    if run_all:
        logger = logging.getLogger('')
        logger.setLevel(logging.WARN)
        unittest.main()
    else:
        suite = unittest.TestSuite()
        suite.addTest(TestWarnings('test_nonexistent_class'))
        unittest.TextTestRunner().run(suite)
