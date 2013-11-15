import typez
import ast
from log import logger


def load_externs():
    from parse_ast import Parser
    parser = Parser()
    f = open("externs.py", "r")
    source = f.read()
    node = ast.parse(source, filename = 'externs.py', mode = 'exec')
    scope = Scope(is_root = True)    
    logger.info('parsing externs')
    extern_scope = typez.extern_scope = parser.eval_code(node, scope)
    typez.inf_setattr = extern_scope['inf_setattr']
    typez.inf_getattr = extern_scope['inf_getattr']
    #extern_scope['int'] = extern_scope['inf_num']
    #extern_scope['str'] = extern_scope['inf_str']
    #extern_scope['object'] = extern_scope['inf_object']
    logger.info('externs parsed')

def find_by_name(name, extern_scope = None):
    if extern_scope == None:
        extern_scope = typez.extern_scope
    return extern_scope.resolve(name,'straight')

class CannotResolve(Exception):
    pass

def is_none(_typez):
    return _typez.kind == 'const' and _typez.value == 'None'

class Typez:
    """
    class enclosing most of the types we deal with.

    attributes:
        kind: any, prim, const, obj, class, func. 
        scope: Scope for the given type. scope.parent should point to the enclosing scope.
        node: ast.AST, important data for some node types
        bases: list of ancestor classes (used only for 'class' kind)
        value: value of the primitive type, or const
    """

    def clone(self):
        other = Typez(kind = 'any')
        for attr in ['kind', 'node', 'scope', 'parent_scope', 'bases', 'value', 'klass_name']:
            if hasattr(self, attr):
                setattr(other, attr, getattr(self, attr))
        return other

    def __init__(self, kind, node = None, scope = None, parent_scope = None, bases = None, value = None, klass_name =
            None):
        self.kind = kind
        self.node = node
        self.value = value
        self.is_method = False
        self.self_obj = None
        
        if scope != None:
            self.scope = scope
        else:
            if parent_scope != None:
                self.scope = Scope(parent = parent_scope)
            else:
                self.scope = Scope(is_root = True)
        if self.kind == 'obj':
            if klass_name:
                class_type = find_by_name(klass_name)
                self.scope.update({'__class__':class_type})
        if self.kind == 'class':
            if not bases:
                inf_object = scope.resolve('object', 'cascade')
                if  inf_object:
                    bases = (inf_object,)
                else:
                    logger.info('nepodarilo sa resolvnut inf_object')
                    logger.debug('nepodarilo sa ... data: ' + str(scope) +' '+ str(scope.parent) + ' ' + str(scope.parent.parent))
                    bases = ()
            self.bases = bases
            self.scope['__bases__'] = bases
            self.scope['__name__'] = klass_name

                
    def __str__(self):
        res = "Typez(%s kind, node: %s"%(self.kind,str(self.node))
        if self.value:
            res += ', value: %s'%self.value
        return res+')'

    def __repr__(self):
        return self.__str__()

    def resolve(self, symbol, mode = 'class'):
        """
        resolves symbol. mode can be either:
            straight: search only in the scope of self
            class: search in the scope of self, cascade to class type and its parents with respect
                to __class__ and __bases__ attributes.
        """
        if not mode in ['straight', 'class']:
            raise Exception('cannot perform resolution in mode %s on type'%str(mode))
        if mode == 'cascade':
            raise Exception('can not cascade resolving on type')
        if self.kind == 'any':
            return Typez(kind = 'any')
        res = self.scope.resolve(symbol, 'straight')
        if res:
            return res
        if mode == 'class':
            if '__class__' in self.scope:
                res = self.scope['__class__'].resolve(symbol, mode)
                if res: 
                    return res
            if '__bases__' in self.scope:
                for base in self.scope['__bases__']:
                    res = base.resolve(symbol, mode)
                    if res:
                        return res
        return None


class Scope(dict):
    """
       dict, that maps symbols to Typez. Useful for remembering objects' states or scope for running
       the functions.

       example: 

       def f():
           x = 3
           y = 4
           z = x+y
       
       after running f in its fresh-ly created scope, symbols x,y,z are primitive num types

       each scope (but root) knows its parent. Resolving of some attributes may be cascaded to that
       parent.
    """
    def __init__(self, parent = None, is_root = False):
        if is_root:
            parent = self
        self.parent = parent

    def is_root(self):
        return self.parent == self

    def __hash__(self):
        return id(self)

    def __str__(self):
        return dict.__str__(self)

    def resolve(self, symbol, mode = 'straight'):
        """
           similar to Typez.resolve
           ``mode == cascade`` cascades resolution to parent scopes
        """
        if not mode in ['straight', 'cascade']:
            raise Exception('cannot perform resolution in mode %s on scope'%str(mode))
        if symbol in self:
            return self[symbol]
        else:
            if mode == 'straight':
                return None
            if mode == 'cascade':
                if self.parent is not self:
                    return self.parent.resolve(symbol, mode)
                else:
                    return None






none_type = Typez(kind = 'const', value = 'None')
any_type = Typez(kind = 'any')

