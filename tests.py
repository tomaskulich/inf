import unittest
import ast
import logging
from parse_ast import Parser
from  typez import (
        Scope,
        Typez,
        extern_scope
        )


pr_num=Typez(kind='prim', node=ast.Num())
pr_str=Typez(kind='prim', node=ast.Str())

class TestResolve(unittest.TestCase): #{{{

    def setUp(self):
        self.scope=Scope(root=True)
        self.scope.update({'xxx':pr_str})

        scope1=Scope(parent=self.scope)
        scope1.update({'a': pr_num, 'b': pr_str})
        self.type1=Typez(kind='obj', scope=scope1)

        scope2=Scope(parent=self.scope)
        scope2.update({'c': pr_num, 'd': pr_str})
        self.type2=Typez(kind='obj', scope=scope2)
        self.type2=scope2

        scope12=Scope(parent=self.scope)
        scope12.update({'a':self.type1, 'b': self.type2})
        self.type12=Typez(kind='obj', scope=scope12)

        self.type3=Typez(kind='multi', scope=Scope(parent=self.scope))
        self.type3.multi=[self.type12, self.type1]

        self.scope.update({'type1':self.type1, 'type2': self.type2, 'type12': self.type12, 'type3': self.type3})

    def test_resolve_type1_in_scope(self):
        res=self.scope.resolve('type1', 'straight')
        self.assertEqual(res, self.type1)

    def test_resolve_in_type(self):
        res=self.type1.resolve('a', 'straight')
        self.assertEqual(res.kind,'prim')
        self.assertIsInstance(res.node, ast.Num)
        self.assertEqual(self.scope.resolve('c', 'straight').value, 'None')

    def test_resolve_multi(self):
        res=self.type3.resolve('a', 'straight')
        self.assertEqual(res.kind,'multi')
        self.assertEqual(len(res.multi),2)
        prim=[val_type for _type in res.multi for key,val_type in _type.scope.items() if _type.kind=='prim']
        self.assertEqual(len(prim),1)

    def test_resolve_cascade(self):
        self.assertRaises(Exception, self.type1.resolve, 'xxx','cascade')
        res1=self.type1.scope.resolve('xxx','cascade')
        res2=self.scope.resolve('xxx','straight')
        self.assertEqual(res1,res2)

    def test_resolve_class(self):
        num=self.type1.resolve('a', 'straight')
        self.assertRaises(Exception, num, '__add__','cascade')
        self.assertRaises(Exception, num, '__add__','straight')
        add=num.resolve('__add__', 'class')
        self.assertIsInstance(add, Typez)
        self.assertEqual(add.kind, 'func')
        self.assertIsInstance(add.node, ast.FunctionDef)

#}}}

class TestInfer(unittest.TestCase): #{{{

    def test_simple_parse(self):
        code="""
x=3
a='ahoj'
y=6
z=3+x
zz=x+y
b='jozo'
c=a+b
x='mumly'

        """
        node=ast.parse(code, mode='exec')
        parser=Parser()
        module_scope=parser.eval_code(node)
        x=module_scope.resolve('x','straight')
        y=module_scope.resolve('y','straight')
        z=module_scope.resolve('z','straight')
        zz=module_scope.resolve('zz','straight')
        a=module_scope.resolve('a','straight')
        b=module_scope.resolve('b','straight')
        c=module_scope.resolve('c','straight')
        self.assertIsInstance(x.node, ast.Str)
        self.assertIsInstance(y.node, ast.Num)
        self.assertIsInstance(z.node, ast.Num)
        self.assertIsInstance(zz.node, ast.Num)
        self.assertIsInstance(a.node, ast.Str)
        self.assertIsInstance(b.node, ast.Str)
        self.assertIsInstance(c.node, ast.Str)

    def test_fun_parse(self):
        code="""
def mean(x,y):
    return (x+y)/2

def gean(x,y):
    return x+y

x=3
y=x+2
z=mean(x,y)
x="jozo"
zz=gean(x,"fero")

        """
        node=ast.parse(code, mode='exec')
        parser=Parser()
        module_scope=parser.eval_code(node)
        x=module_scope.resolve('x','straight')
        y=module_scope.resolve('y','straight')
        z=module_scope.resolve('z','straight')
        zz=module_scope.resolve('zz','straight')
        self.assertIsInstance(x.node, ast.Str)
        self.assertIsInstance(y.node, ast.Num)
        self.assertIsInstance(z.node, ast.Num)
        self.assertIsInstance(zz.node, ast.Str)
    
    def test_closure(self):
        code="""
def f(x):
    z=x
    def g(y):
        return(x+y)
    return g

g1=f(3)
g2=f('jozo')

a=g1(4)
b=g2('fero')

"""
        node=ast.parse(code, mode='exec')
        parser=Parser()
        module_scope=parser.eval_code(node)
        a=module_scope.resolve('a','straight')
        b=module_scope.resolve('b','straight')
        self.assertIsInstance(a.node, ast.Num)
        self.assertIsInstance(b.node, ast.Str)

    def test_class(self):
        code="""
class A:
    def __init__(self, x, y, z):
        self.x=x
        self.y=y
a=A(3,"ahoj", "svet")
"""
        node=ast.parse(code, mode='exec')
        parser=Parser()
        module_scope=parser.eval_code(node)
        a=module_scope.resolve('a','straight')
        self.assertIsInstance(a.scope['x'].node, ast.Num)
        self.assertIsInstance(a.scope['y'].node, ast.Str)
        self.assertEqual(a.scope.resolve('z','straight').value,'None')

    def test_override_setattr(self):
        code="""
class A:
    def __init__(self, x, y):
        pass

    def __setattr__(self, attr, val):
        object.__setattr__(self, attr, 4)


a=A(3,4)
a.x='jozo'
key='z'
object.__setattr__(a,key,'jozo')

"""
        node=ast.parse(code, mode='exec')
        parser=Parser()
        module_scope=parser.eval_code(node)
        a=module_scope.resolve('a','straight')
        self.assertIsInstance(a.scope['x'].node, ast.Num)
        self.assertIsInstance(a.scope['z'].node, ast.Str)

    def test_method_lookup(self):
        code="""
class A:
    def __init__(self, x):
        self.x=x

    def get_x(self):
        return self.x

a=A('jozo')
b=a.get_x()
getx=a.get_x
a=A(3)
c=a.get_x()

"""
        node=ast.parse(code, mode='exec')
        parser=Parser()
        module_scope=parser.eval_code(node)
        a=module_scope.resolve('a','straight')
        A=module_scope.resolve('A','straight')
        self.assertNotIn('get_x', a.scope)
        self.assertIn('get_x', A.scope)
        b=module_scope.resolve('b','straight')
        c=module_scope.resolve('c','straight')
        getx=module_scope.resolve('getx', 'straight')
        self.assertIsInstance(b.node, ast.Str)
        self.assertIsInstance(c.node, ast.Num)
        self.assertEqual(getx.kind, 'func')

    def test_inheritance(self):
        code="""
class A:
    def __init__(self):
        pass
    def get_x(self):
        return self.x

class B(A):
    def __init__(self):
        pass
    def get_y(self):
        return self.y

b=B()
b.x='jozo'
b.y=4
"""
        node=ast.parse(code, mode='exec')
        parser=Parser()
        module_scope=parser.eval_code(node)
        b=module_scope.resolve('b','straight')
        self.assertIsInstance(b.scope['y'].node, ast.Num)
        self.assertIsInstance(b.scope['x'].node, ast.Str)


#}}}

class TestWarnings(unittest.TestCase): #{{{
    
    def test_nonexistent_attribute(self):
        code="""
class A:
    def __init__(self, x, y):
        self.x=x
        self.y=y
a=A(3,4)
a.x=a.z
a.method()
"""

        node=ast.parse(code, mode='exec')
        parser=Parser()
        module_scope=parser.eval_code(node)
        problem_symbols={problem.symbol for problem in parser.problems}
        self.assertEqual(problem_symbols, {'method', 'z'})

#}}}

if __name__ == '__main__':
    run_all=True
    #run_all=False

    if run_all:
        logger=logging.getLogger('')
        logger.setLevel(logging.WARN)
        unittest.main()
    else:
        suite = unittest.TestSuite()
        #suite.addTest(TestWarnings('test_nonexistent_attribute'))
        suite.addTest(TestInfer('test_method_lookup'))
        unittest.TextTestRunner().run(suite)
