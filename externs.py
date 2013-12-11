
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
    
class num(object):

    def __add__(self,x):
        return 0

    def __div__(self,x):
        return 0

    def __mul__(self,x):
        return 0

class str(object):


    def __add__(self,x):
        return ""

str.__name__ = "str"
num.__name__ = "num"

