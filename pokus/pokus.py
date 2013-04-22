
class A:

    def __init__(self):
        pass

    def __getattr__(self, name):
        print("tu")
        return object.__getattr__(self, name)

    #def __setattr__(self, name, value):
    #    print("tuuu")
    #    return object.__setattr__(self, name, value)
a=A()
a.__setattr__('x',10)
print(dir(A))
#a.x=10
print(a.x)
