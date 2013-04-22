import ast

code="x.y.z(9)"

node=ast.parse(code, mode='exec')
expr=node.body[0]
print(expr, expr.value, expr.value.func, expr.value.func.ctx, expr.value.func.attr)

