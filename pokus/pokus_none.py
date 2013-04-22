
import ast

code="x=True"

node=ast.parse(code, mode='exec')
assign=node.body[0]
print(assign.value.id)
