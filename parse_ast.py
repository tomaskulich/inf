import ast
from typez import (
        Typez,
        Scope,
        is_none,
        none_type,
        )
import typez
import parse_ast
import logging

logger=logging.getLogger('')
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
logger.addHandler(console_handler)

    
"""
We resolve types of individual variables by symbolic execution of the code. 
"""

def logentry(fn):
    """decorator for logging visit of a node"""
    def _f(*args):
        node=[_node for _node in args if isinstance(_node, ast.AST)][0]
        if hasattr(node, 'lineno'):
            line=str(node.lineno)
        else:
            line='?'
        logger.debug(line + " "+fn.__name__)
        return fn(*args)
    _f.__name__=fn.__name__
    return _f


class Problem:
    """encapsulates data about execution problem, that may occur (such as unknown attribute)"""
    def __init__(self, node, message=None, symbol=None):
        self.node=node
        self.message=message
        self.symbol=symbol

    def __str__(self):
        return "message: %s, symbol: %s (node: %s)"%(self.message, str(self.symbol), str(self.node))

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
        self.modules=[]
        self.problems=[]

    def warn(self, node, message=None, symbol=None):
        """add new problem"""
        self.problems.append(Problem(node, message, symbol))

    @logentry
    def exec_BinOp(self, node, scope):
        op_dict={ast.Add: '__add__',
                ast.Div: '__div__'}
        left_type=self.eval_code(node.left, scope)
        right_type=self.eval_code(node.right, scope)
        args=[left_type, right_type]

        op_class=node.op.__class__
        if not op_class in op_dict:
            raise Exception('unknown operation '+str(node.op))
        fun_type=left_type.resolve(op_dict[node.op.__class__],'class')
        return self._exec_fun(fun_type, args, scope)

    @logentry
    def exec_FunctionDef(self, node, scope):
        scope[node.name]=typez.Typez(kind='func', node=node, scope=scope)

    @logentry
    def exec_ClassDef(self, node, scope):
        assert(isinstance(node, ast.AST))
        class_scope=Scope(parent=scope)
        for _node in node.body:
            self.eval_code(_node, class_scope)
        bases=[self.eval_code(base, scope) for base in node.bases]
        scope[node.name]=Typez(kind='class', node=node, bases=bases, scope=class_scope)

    @logentry
    def exec_Assign(self, node, scope):
        #TODO cover the case when having multiple targets such as a=b=3
        if(len(node.targets)==1):
            lhs=node.targets[0]
            rhs=node.value
            if isinstance(lhs, ast.Name):
                scope[lhs.id]=self.eval_code(rhs,scope)
            elif isinstance(lhs, ast.Attribute):
                if isinstance(lhs.ctx, ast.Store):
                    #this covers cases such as x.y=sth, x.y is attrubute in Store context. In this
                    #case, look for appropriate __setattr__, posibly cascasing to the object.__setattr__
                    lhs_obj=self.eval_code(lhs.value, scope)
                    rhs_val=self.eval_code(rhs, scope)
                    __setattr__=lhs_obj.resolve('__setattr__', 'class')
                    args=(lhs_obj, lhs.attr, rhs_val) 
                    self._exec_fun(__setattr__, args, scope)
                else:
                    raise Exception('bad context')
            else:
                raise Exception('should not get here')

    @logentry
    def exec_Num(self, node, scope):
        return Typez(kind='prim', node=node, value=node.n)

    @logentry
    def exec_Str(self, node, scope):
        return Typez(kind='prim', node=node, value=node.s)

    @logentry
    def exec_Expr(self, node, scope):
        return self.eval_code(node.value, scope)


    def _exec_fun(self, fun_type, args, scope, create_scope=True):
        """
        executes function with given args in the given scope. When create_scope is True, it creates new scope for the function
        executing with parameter scope as its parent. Otherwise, it executes function in the given
        scope.

        TODO: If fun_type is of a kind 'multi' then what?
        """
        if fun_type.kind=='multi':
            raise Exception('not yet implemented')
            #result=[]
            #for single_type in fun_type.multi:
            #   result.append( _exec_fun(single_type, args, scope))
            #return typez.type_from_list(result)
        else:
            if fun_type==typez.inf_setattr:
                attr=args[1]
                if isinstance(attr, Typez) and isinstance(attr.value, str):
                    attr=attr.value
                if isinstance(attr,str): 
                    args[0].scope[attr]=args[2]
                
            if create_scope:
                fun_scope=Scope(parent=scope)
            else:
                fun_scope=scope
            def_args=fun_type.node.args.args
            #binding arguments to their values; for now it only works with positional arguments
            if len(args)!=len(def_args):
                raise Exception('bad number of arguments (%d!=%d)'%(len(args), len(def_args)))
            for i, arg in enumerate(args):
                fun_scope[def_args[i].arg]=arg
            results=[]
            for _node in fun_type.node.body:
                res=self.eval_code(_node, fun_scope)
                if res:
                    results.append(res)
            if fun_type.kind=='class':
                return args[0]
            return typez.type_from_list(results)

    def exec_Call(self, node, scope):
        #first let's find out which function should be called. This should be easy when doing func()
        #call, but it can be tricky when using constructs such as 'a.b.c.func()'
        self_type=None
        #covers func() case
        if isinstance(node.func,ast.Name):
            logger.debug("? exec_Call "+node.func.id +" "+str(node))
            call_type=scope.resolve(node.func.id,'cascade')
        #covers a.b.c.func() case
        elif isinstance(node.func, ast.Attribute):
            logger.debug("? exec_Call "+node.func.attr +" "+str(node))
            call_type=self.eval_code(node.func, scope)
            if typez.is_none(call_type):
                self.warn(node.func, message='nonexistent_attribute', symbol=node.func.attr)
                return typez.none_type

            #whether we are dealing with function or with a method should be already resolved by
            #exec_Attribute
            if hasattr(call_type, 'is_method'):
                if call_type.is_method:
                    self_type=self.eval_code(node.func.value, scope)
        else:
            raise Exception('should not get here')

        #now we know what to invoke. Now we must distinguist whether it is func/method call or 'new'
        #statement.

        #Call-ing function or method
        if call_type.kind=='func':
            args=[self.eval_code(arg,scope) for arg in node.args]
            if self_type:
                args=[self_type]+args
            return self._exec_fun(call_type, args, call_type.scope)

        #Call-ing as a 'new' statement 
        if call_type.kind=='class':
            args=[self.eval_code(arg,scope) for arg in node.args]
            new=Typez(kind='obj', scope=Scope(parent=call_type.scope))
            args=[new]+args
            new.scope['__class__']=call_type
            constructor=call_type.resolve('__init__', 'straight')
            new.obj=self._exec_fun(constructor, args, new.scope)
            return new
        raise Exception('calling node must be either function or class')

    @logentry
    def exec_Module(self, node, scope):
        module_scope=Scope(parent=scope)
        for _node in node.body:
                self.eval_code(_node, module_scope)

        return module_scope

    @logentry
    def exec_Return(self, node, scope):
        return self.eval_code(node.value, scope)

    def exec_Name(self, node, scope):
        consts=['None', 'True', 'False']
        for const in consts:
            if node.id==const:
                return Typez(kind='const', value=const)

        return scope.resolve(node.id, 'cascade')

    def exec_Pass(self, node, scope):
        pass

    @logentry
    def exec_Attribute(self, node, scope):
        if not isinstance(node.ctx, ast.Load):
            raise Exception('''Attribute should allways be executed in Load context, in the case of
                x.y=z the whole assignment should be handled by exec_Assign''')
        _type=self.eval_code(node.value, scope)
        #we first try 'straight' resolution of 
        straight_resolution=_type.resolve(node.attr, 'straight')
        if not is_none(straight_resolution):
            return straight_resolution
        else:
            res=_type.resolve(node.attr, 'class')
            if not is_none(res):
                res.is_method=True
                return res
            else:
                self.warn(node, message='nonexistent_attribute', symbol=node.attr)
                return none_type

    def eval_code(self, node, scope=None):
        """
          main method of the parser, it executes code under certain node within the given scope (if
          the scope is not given, we use typez.extern_scope as a highest scope possible). It returns
          return value of the code.

          the whole idea is to dispatch work to exec_<ast_node_name> functions; exec_name functions
          are doing only minimum ammount of job to correctly cover the execution of the specific piece of
          code, recursively using eval_code to evaluate values of their children nodes.
        """
        if scope is None:
            scope=typez.extern_scope
        name='exec_'+node.__class__.__name__
        handler=Parser.__dict__[name]
        return handler(self, node, scope)


typez.load_externs()

if __name__ == '__main__':
    pass

                




