
def inf_len(arg):
    return arg.__len__()
#inf_len.original_name="len"

def inf_getattr(obj, name):
    pass

def inf_setattr(obj, name, value):
    pass

class object:

    def __init__(self):
        pass

    def __getattr__(self, name):
        return inf_getattr(self, name)

    def __setattr__(self, name, value):
        return inf_setattr(self, name, value)
    
    def umriumri():
        pass

class num(inf_object):

    def __add__(self,x):
        return 0

    def __div__(self,x):
        return 0

    def __mul__(self,x):
        return 0

#inf_num.__name__ = 'num'


class str(inf_object):
    def __add__(self,x):
        return ""

#inf_str.__name__= 'str'

#class inf_list(inf_object):
#
#    def __init__(self):
#        pass
#
#    def getattr(self, attr):
#        pass
#
#    def setattr(self, attr, val):
#        pass

#Str_.original_name="str"
