import ast

class FuncLister(ast.NodeVisitor):
    def visit_FunctionDef(self, node):
        print(node.name)
        self.generic_visit(node)
        
def treeWalk(node):
    #print(type(node), node.__dict__)
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
        
#b = analyzeLine(" # ahojte  ")
#if b:
#    print("valid commment")
#else:
#    print("no commment")
f= open("input_for_ply.py", "r")
#find commments in the source file
line = f.readline()

count = 1
while line:
   if analyzeLine(line):
        print(count, line)
   line = f.readline()
   count += 1
print("pocet riadkov:", count)
#parse the source file
f= open("input_for_ply.py", "r")
source = f.read()
n = ast.parse(source, filename='input_for_ply.py', mode='exec')
#find scope according to comment
treeWalk(n)


    
        