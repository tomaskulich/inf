import re
from ply import (
        yacc,
        lex,
        )


class Context(object):
    """
    context used for printing parsing tree. Holds information about indentation level and last-seen
    token
    """
    def __init__(self):
        self.indent=0
        self.last=None
        self.was_newline=False
    
    def get_indent(self):
        return '    '*self.indent

class Node(object):
    """
    general class for one node in the parsing tree. All nodes but leafs in the parsing tree should
    be of this type; leafs are instances of lex.Token
    """

    def __init__(self, kind, childs=None):
        self.kind=kind
        if not isinstance(childs, yacc.YaccProduction):
            raise Exception('should not get here')
        self.childs=[]
        for i in range(1,len(childs)):
            self.childs.append(childs[i])

    def __str__(self):
        return self.kind
    
    def __repr__(self):
        return self.__str__()

    def __iter__(self):
        yield self
        for child in self.childs:
            if not isinstance(child, Node):
                yield child
            else:
                for childchild in child:
                    yield childchild

def token_to_str(ctx, token):
    """
    converts token to string, handles special cases such as indent/dedent tokens, etc...
    """
    if token.type=='INDENT':
        ctx.indent+=1
    elif token.type=='DEDENT':
        ctx.indent-=1
    elif token.type=='NEWLINE':
        return '\n'
    elif token.type=='DEF':
        return 'def '
    elif token.type=='CLASS':
        return 'class '
    elif token.type=='FOR':
        return 'for '
    elif token.type=='WHILE':
        return 'while '
    elif token.type=='IF':
        return 'if '
    elif token.type=='NAME':
        if ctx.last and ctx.last.type=='NAME':
            return ' '+token.value
        else:
            return token.value
    elif token.type=='NUMBER':
        return str(token.value[1])
    elif token.type=='STRING':
        val=token.value
        triple_double='"""'
        triple_single="'''"
        if re.search(triple_single, val):
            delim=triple_double
            if re.search(triple_double, val):
                raise Exception('should not get here')
        else:
            delim=triple_single
        return delim+token.value+delim
    elif token.type in ['LPAR', 'RPAR', 'COLON', 'LBRACE', 'RBRACE', 'OPERATOR', 'STRING', 'LSQB', 'RSQB']:
        return token.value
    elif token.type == 'ENDMARKER':
        pass
    elif True:
        return str(token)

def node_to_tree(node):
    """
    returns string representation of a tree rooted in the given node.
    """
    def _to_tree_string(node, indent=0):
        res=["  "*indent+str(node)+'\n']
        if hasattr(node, 'childs'):
            for child in node.childs:
                res.extend(_to_tree_string(child, indent+1))
        return res

    res=_to_tree_string(node)

    return ''.join(res)

def node_to_str(node):
    """
    return code-like representation of a tree rooted in a given node. Should be parseable by exec,
    eval or compile builtins.
    """
    ctx=Context()
    def _to_string(node, ctx):
        res=[]
        for child in node.childs:
            if isinstance(child, Node):
                res.append(_to_string(child, ctx))
            elif isinstance(child, lex.LexToken):
                if ctx.was_newline and child.type!='INDENT' and child.type!='DEDENT':
                    ctx.was_newline=False
                    res.append(ctx.get_indent())
                if child.type=='NEWLINE':
                    ctx.was_newline=True
                token_string=token_to_str(ctx, child)
                if token_string:
                    res.append(token_string)
                ctx.last=child
            else:
                raise Exception('should not get here! '+str(child))
        return ''.join(res)
    return _to_string(node, ctx)
            

