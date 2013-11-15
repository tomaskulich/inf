import ast
from typez import (
        Typez,
        Scope,
        is_none,
        none_type,
        any_type,
        )
import typez
from log import logger

def safe_resolve(obj, attrs):
    try:
        for attr in attrs.split('.'):
            obj = getattr(obj, attr)
        return obj
    except Exception:
        return None

def not_none(*args):
    for arg in args:
        if arg != None:
            return arg
    
"""
We resolve types of individual variables by symbolic execution of the code. 
"""

def logentry(fn):
    """decorator for logging visit of a node"""
    def _f(*args):
        node = [_node for _node in args if isinstance(_node, ast.AST)][0]
        if hasattr(node, 'lineno'):
            line = str(node.lineno)
        else:
            line = '?'
        logger.debug(line + " "+fn.__name__)
        return fn(*args)
    _f.__name__ = fn.__name__
    return _f


class Problem:
    """encapsulates data about execution problem, that may occur (such as unknown attribute)"""
    def __init__(self, node = None, message = None, symbol = None):
        self.node = node
        self.message = message
        self.symbol = symbol

    def __str__(self):
        return "Problem(message: %s, symbol: %s, node: %s, line: %d)"%(self.message, str(self.symbol),
                str(self.node.__class__), self.node.lineno)

    def __repr__(self):
        return self.__str__()

class Parser:
    """
       class that gathers parsing utilites.

       attributes:
          modules: TODO. will be list of modules already imported
          problems: list of all problems found by parsing

       main parser method is eval_code. exec_* methods are used to process individual ast nodes.
    """
    def __init__(self):
        self.modules = []
        self.problems = []

    def warn(self, node = None, message = None, symbol = None):
        """add new problem"""
        self.problems.append(Problem(node, message, symbol))

    @logentry
    def exec_BinOp(self, node, scope):
        op_dict = {ast.Add: '__add__',
                ast.Div: '__div__'}
        left_type = self.eval_code(node.left, scope)
        right_type = self.eval_code(node.right, scope)
        args = [left_type, right_type]

        op_class = node.op.__class__
        if not op_class in op_dict:
            raise Exception('unknown operation '+str(node.op))
        fun_type = left_type.resolve(op_dict[node.op.__class__],'class')
        return self._exec_fun(fun_type, args, scope, node=node)

    @logentry
    def exec_FunctionDef(self, node, scope):
        scope[node.name] = typez.Typez(kind = 'func', node = node, scope = scope)

    @logentry
    def exec_ClassDef(self, node, scope):
        assert(isinstance(node, ast.AST))
        class_scope = Scope(parent = scope)
        for _node in node.body:
            self.eval_code(_node, class_scope)
        bases = [self.eval_code(base, scope) for base in node.bases]
        scope[node.name] = Typez(kind = 'class', node = node, bases = bases, scope = class_scope,
                klass_name = node.name)

    @logentry
    def exec_Assign(self, node, scope):
        #TODO cover the case when having multiple targets such as a = b = 3
        if(len(node.targets) == 1):
            lhs = node.targets[0]
            rhs = node.value
            if isinstance(lhs, ast.Name):
                scope[lhs.id] = self.eval_code(rhs,scope)
            elif isinstance(lhs, ast.Attribute):
                if isinstance(lhs.ctx, ast.Store):
                    #this covers cases such as x.y = sth, x.y is attrubute in Store context. In this
                    #case, look for appropriate __setattr__, posibly cascasing to the object.__setattr__
                    lhs_obj = self.eval_code(lhs.value, scope)
                    rhs_val = self.eval_code(rhs, scope)
                    __setattr__ = lhs_obj.resolve('__setattr__', 'class')
                    args = (lhs_obj, lhs.attr, rhs_val) 
                    self._exec_fun(__setattr__, args, scope, node=node)
                else:
                    raise Exception('bad context')
            else:
                raise Exception('should not get here')

    @logentry
    def exec_Num(self, node, scope):
        return Typez(kind = 'obj', node = node, value = node.n, klass_name = 'num')

    @logentry
    def exec_Str(self, node, scope):
        return Typez(kind = 'obj', node = node, value = node.s, klass_name = 'str')

    @logentry
    def exec_List(self, node, scope):
        res = Typez(kind = 'obj', node = node, klass_name = 'inf_list')
        for item in node.elts:
            item_val = self.eval_code(item, scope)
            append = res.resolve('append', 'class')
            self._exec_fun(append, item_val, scope, node=node)

    @logentry
    def exec_Expr(self, node, scope):
        return self.eval_code(node.value, scope)


    def _exec_fun(self, fun_type, args, scope, create_scope = True, node = None):
        """
        executes function with given args in the given scope. When create_scope is True, it creates new scope for the function
        executing with parameter scope as its parent. Otherwise, it executes function in the given
        scope.

        """
        if fun_type == typez.inf_setattr:
            attr = args[1]
            if isinstance(attr, Typez) and isinstance(attr.value, str):
                attr = attr.value
            if isinstance(attr, str): 
                args[0].scope[attr] = args[2]
            
        if create_scope:
            fun_scope = Scope(parent = scope)
        else:
            fun_scope = scope
        def_args = fun_type.node.args.args
        #binding arguments to their values; for now it only works with positional arguments
        if len(args) != len(def_args):
            symbol = not_none(safe_resolve(node, 'func.attr'), safe_resolve(node, 'func.id'))
            self.warn(node, symbol = symbol, message = 'bad number of arguments (%d given, %d expected)'%(len(args), len(def_args)))
        for i, arg in enumerate(def_args):
            if i<len(args):
                fun_scope[arg.arg] = args[i]
            else:
                fun_scope[arg.arg] = any_type
        for _node in fun_type.node.body:
            res = self.eval_code(_node, fun_scope)
            if res is not None:
                return res
        if fun_type.kind == 'class':
            return args[0]

    def exec_IfExp(test, body, orelse):
        pass

    def exec_Call(self, node, scope):
        #first let's find out which function should be called. This should be easy when doing func()
        #call, but it can be tricky when using constructs such as 'a.b.c.func()'

        #covers func() case
        if isinstance(node.func, ast.Name):
            logger.debug("? exec_Call "+node.func.id +" "+str(node))
            call_type = scope.resolve(node.func.id,'cascade')
            if call_type is None:
               call_type = any_type 
        #covers a.b.c.func() case
        elif isinstance(node.func, ast.Attribute):
            logger.debug("? exec_Call "+node.func.attr +" "+str(node))
            call_type = self.eval_code(node.func, scope)
            if call_type.kind == 'any':
                return any_type

        else:
            raise Exception('should not get here')

        #now we know what to invoke. Now we must distinguish whether it is func/method call or 'new'
        #statement.

        #TODO: dorobit spustanie 'any' kind
        #Call-ing function or method
        if call_type.kind == 'func':
            args = [self.eval_code(arg, scope) for arg in node.args]
            if call_type.is_method:
                args = [call_type.self_obj]+args
            return self._exec_fun(call_type, args, call_type.scope, node=node)

        #Call-ing as a 'new' statement 
        if call_type.kind == 'class':
            args = [self.eval_code(arg,scope) for arg in node.args]
            new = Typez(kind = 'obj', parent_scope = scope)
            args = [new]+args
            new.scope['__class__'] = call_type
            constructor = call_type.resolve('__init__', 'class')
            if constructor:
                new.obj = self._exec_fun(constructor, args, new.scope, node=node)
            return new
        self.warn(node, message = 'nonexistent_function', symbol = node.func.id)

    @logentry
    def exec_Module(self, node, scope):
        module_scope = Scope(parent = scope)
        for _node in node.body:
                self.eval_code(_node, module_scope)

        return module_scope


    @logentry
    def exec_Return(self, node, scope):
        return self.eval_code(node.value, scope)

    def exec_Name(self, node, scope):
        consts = ['None', 'True', 'False']
        for const in consts:
            if node.id == const:
                return Typez(kind = 'const', value = const)

        return scope.resolve(node.id, 'cascade')

    def exec_Pass(self, node, scope):
        pass

    @logentry
    def exec_Attribute(self, node, scope):
        if not isinstance(node.ctx, ast.Load):
            raise Exception('''Attribute should allways be executed in Load context, in the case of x.y = z the whole assignment should be handled by exec_Assign''')
        _type = self.eval_code(node.value, scope)
        #we first try 'straight' resolution of the attribute
        res = _type.resolve(node.attr, 'straight')
        if res:
            res.is_method = False
            res.self_obj = None
            print('straight resolution', node.attr)
            return res
        else:
            res = _type.resolve(node.attr, 'class')
            if res is not None:
                # we are creating partial
                res = res.clone()
                res.is_method = True
                res.self_obj = _type
                print('class resolution', node.attr, res, id(res), res.is_method)
                return res
            else:
                self.warn(node, message = 'nonexistent_attribute', symbol = node.attr)
                return any_type

    def eval_code(self, node, scope = None):
        """
          main method of the parser, it executes code under certain node within the given scope (if
          the scope is not given, we use typez.extern_scope as a highest scope possible). It returns
          return value of the code.

          the whole idea is to dispatch work to exec_<ast_node_name> functions; exec_name functions
          are doing only minimum ammount of job to correctly cover the execution of the specific piece of
          code, recursively using eval_code to evaluate values of their children nodes.
        """
        if scope is None:
            scope = typez.extern_scope
        name = 'exec_'+node.__class__.__name__
        handler = Parser.__dict__[name]
        return handler(self, node, scope)


typez.load_externs()

if __name__ == '__main__':
    pass

                




