import ast

def Arguments(names, defaults, vararg, kwarg):
    return ast.arguments([Name(i) for i in names], vararg, kwarg, defaults)

def Call(callee, args):
    return ast.Call(callee, args, [], None, None)

def List(list):
    return ast.List(list, None)

def Name(name):
    return ast.Name(name, None)

def Tuple(tuple):
    return ast.Tuple(tuple, None)