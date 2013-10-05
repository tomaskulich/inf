import ast
import typez


def load_externs():
    from parse_ast import Parser
    parser=Parser()
    f=open("externs.py", "r")
    source=f.read()
    node=ast.parse(source, filename='externs.py', mode='exec')
    scope=Scope(is_root=True)    
    print('@@@@@@ parsing externs')
    extern_scope=typez.extern_scope=parser.eval_code(node, scope)
    typez.inf_setattr=extern_scope['inf_setattr']
    typez.inf_getattr=extern_scope['inf_getattr']
    extern_scope['int']=extern_scope['Num_']
    extern_scope['str']=extern_scope['Str_']
    extern_scope['object']=extern_scope['inf_object']
    print(typez.extern_scope)
    print('@@@@@@ externs parsed')

def find_by_name(name, extern_scope=None):
    if extern_scope==None:
        extern_scope=typez.extern_scope
    return extern_scope.resolve(name,'straight')

class CannotResolve(Exception):
    pass

def is_none(_typez):
    return _typez.kind=='const' and _typez.value=='None'


class Typez:
    """
    class enclosing most of the types we deal with.

    attributes:
        kind: any, prim, const, obj, class, func. All options but multi are considered single.
        multi: [Typez] if type is multi, it holds all the type-choices
        scope: Scope for the given type. scope.parent should point to the enclosing scope.
        node: ast.AST, important data for some node types
        bases: list of ancestor classes (used only for 'class' kind)
        value: value of the primitive type, or const
    """
    def __init__(self, kind, node=None, multi=None, scope=None, bases=None, value=None):
        self.kind=kind
        self.node=node
        self.multi=multi
        self.scope=scope
        self.value=value
        if self.kind=='prim':
            name=node.__class__.__name__+"_"
            class_type=find_by_name(name)
            self.scope=Scope(is_root=True)
            self.scope.update({'__class__':class_type})
        if self.kind=='class':
            if not bases:
                try:
                    inf_object=scope.resolve('inf_object', 'cascade')
                    bases=(inf_object,)
                except:
                    print('nepodarilo sa resolvnut inf_object')
            self.bases=bases
            self.scope['__bases__']=bases
                
    def __str__(self):
        res="Typez(%s kind, node: %s"%(self.kind,str(self.node))
        if self.value:
            res+=', value: %s'%self.value
        return res+')'

    def __repr__(self):
        return self.__str__()

    def resolve(self, symbol, mode):
        """
        resolves symbol. mode can be either:
            straight: search only in the scope of self
            cascade: search in the scope of self and cascade to parent scopes if needed
            class: search in the scope of self, cascade to class type and its parents with respect
                to __class__ and __bases__ attributes.
        """
        if is_none(self):
            return none_type
        if mode=='cascade':
            raise Exception('can not cascade resolving on type')
        if self.kind=='any':
            return Typez(kind='any')
        if self.kind=='multi':
            result=[]
            for _type in self.multi:
                result.append(_type.resolve(symbol, mode))
            return type_from_list(result)
        else:
            return self.scope.resolve(symbol, mode)



def type_from_list(list_of_typez, allow_none=True):
    """
       helper function that creates type out of iterable of types. 
    """
    if len(list_of_typez)==0:
        if allow_none:
            return Typez(kind='none')
        else:
            raise CannotResolve()
    elif len(list_of_typez)==1:
        return list_of_typez[0]
    else:
        return Typez(kind='multi', multi=list_of_typez)


class Scope(dict):
    """
       dict, that maps symbols to Typez. Useful for remembering objects' states or scope for running
       the functions.

       example: 

       def f():
           x=3
           y=4
           z=x+y
       
       after running f in its fresh-ly created scope, symbols x,y,z are primitive num types

       each scope (but root) knows its parent. Resolving of some attributes may be cascaded to that
       parent.
    """
    def __init__(self, parent=None, is_root=False):
        if is_root:
            parent=self
        self.parent=parent

    def is_root(self):
        return self.parent==self

    def __hash__(self):
        return id(self)

    def __str__(self):
        return dict.__str__(self)

    def resolve(self, symbol, mode='straight'):
        """
           similar to Typez.resolve
        """
        if symbol in self:
            return self[symbol]
        else:
            if mode=='straight':
                return none_type
            if mode=='cascade':
                if self.parent!=self:
                    return self.parent.resolve(symbol, mode)
                else:
                    return none_type
            if mode=='class':
                if '__class__' in self:
                    return self['__class__'].scope.resolve(symbol, mode)
                if '__bases__' in self:
                    result=[]
                    for base in self['__bases__']:
                        res=base.resolve(symbol, mode)
                        if res.kind=='multi':
                            result.extend(res.multi)
                        else:
                            result.append(res)
                    return type_from_list(result)

                else:
                    return none_type






none_type=Typez(kind='const', value='None')

