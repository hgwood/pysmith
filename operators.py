import ast
from collections import namedtuple

Operator = namedtuple('Operator', 'name, left_predicates, right_predicates')

def has(name):
    return lambda x: hasattr(x, name)

binary_operators = [
    Operator(ast.Add, [has('__add__')], [has('__radd__')]),
    Operator(ast.Sub, [has('__sub__')], [has('__rsub__')]),
    Operator(ast.Mult, [has('__mul__')], [has('__rmul__')]),
    Operator(ast.Div, [has('__div__')], [has('__rdiv__'), lambda x: x != 0]),
]

boolean_operators = [
    ast.And,
    ast.Or,
]