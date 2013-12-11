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
        for attr in ['kind', 'node', 'scope', 'parent_scope', 'bases', 'value' ]:
            if hasattr(self, attr):
                setattr(other, attr, getattr(self, attr))
        return other

    def __init__(self, kind, node = None, scope = None, parent_scope = None, value = None, __class__ = None):
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
        if __class__:
            self.scope.update({'__class__': __class__})
                
    def __str__(self):
        res = "Typez(%s kind, node: %s"%(self.kind,str(self.node))
        if self.value:
            res += ', value: %s'%self.value
        return res+')'

    def __repr__(self):
        return self.__str__()

    def resolve(self, symbol, mode = 'class', tried = None):
        """
        resolves symbol. mode can be either:
            straight: search only in the scope of self
            class: search in the scope of self, cascade to class type and its parents with respect
                to __class__ and __bases__ attributes.
        """
        if not mode in ['straight', 'class']:
            raise Exception('cannot perform resolution in mode %s on type'%str(mode))
        if self.kind == 'any':
            return Typez(kind = 'any')
        res = self.scope.resolve(symbol, 'straight')
        if res:
            return res
        if mode == 'class':
            if tried == None:
                tried = []
            if '__class__' in self.scope:
                clazz = self.scope['__class__']
                res = clazz.resolve(symbol, mode, tried = tried)
                if res: 
                    return res
            #TODO: implement method lookup protocol properly
            if '__bases__' in self.scope:
                for base in self.scope['__bases__']:
                    if not base in tried:
                        tried.append(base)
                        res = base.resolve(symbol, 'class', tried = tried)
                        if res:
                            return res
        return None


class Scope(dict):
    """
       dict, that maps symbols to Typez. Useful for remembering objects' states or scope for running
       the functions.

       example: 

       > def f():
       >     x = 3
       >     y = 4
       >     z = x+y
       
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

