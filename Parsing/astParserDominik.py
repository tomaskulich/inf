import ast
     
def treeWalk(node):
    print(type(node), node.__dict__)
    for n in ast.iter_child_nodes(node):
       for x in n.__dict__:
            y = getattr(n, x)
            print(x,y)
       #print("synom je:", type(n), n.__dict__)
    for n in ast.iter_child_nodes(node):
        treeWalk(n)
def analyzeLine(line):
    first = True
    for x in line:
        if x == '#':
            return True
        if x != ' ':
            return False
    return True    

def parseWithAst(list):
    errors = []
    for x in list:
        try:
            n = ast.parse(str(x))
            treeWalk(n)
        except Exception as error:
            x = [error.args[1][1],error.args[1][2],error.args[1][3]]
            errors.append(x)
            print(error)      
        print("--------------------------------------")
    return errors
filename = "input_for_ply.py"

#Open the file, read it
f = open(filename)
data = f.read()

input = [['class moja():\n', [['a = 10\n'], ['def testing(self):\n', [['print()\n'], ['de test():\n', ['print()\n']], ['if a > 10:\n', ['print(54)\n\n']]]], ['b = 8 ']]]]        
#input1 = [['class moja():\n\ta = 10\n\tdef testing(self):\n\t\tprint(self.a)\n\tb = 8'], []]
#input.append(data)
errors = parseWithAst(input)
print(errors)


