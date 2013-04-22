
def inf_len(arg):
    return arg.__len__()
#inf_len.original_name="len"

def inf_getattr(obj, name):
    pass

def inf_setattr(obj, name, value):
    pass

class inf_object:

    def __init__(self):
        pass

    def __getattr__(self, name):
        return inf_getattr(self, name)

    def __setattr__(self, name, value):
        return inf_setattr(self, name, value)

class Num_(inf_object):
    def __add__(self,x):
        return 0
    def __div__(self,x):
        return 0
    def __mul__(self,x):
        return 0

#Num_.original_name="int"


class Str_(inf_object):
    def __add__(self,x):
        return ""

#Str_.original_name="str"
