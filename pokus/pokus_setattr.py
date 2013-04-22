class A(object):

    def __init__(self):
        return 

    def __setattr__(self, name, value):
        print("setting %s to %s" %(name, str(value)))
        object.__setattr__(self, name, value)

   #     super().__setattr__(name, value)

a=A()
a.b=1
