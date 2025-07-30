import argparse
from enum import Enum
import ast
import subprocess
import os
from reader import read_arguments, parse_source

class ExprContext(Enum):
    LOAD = 1
    STORE = 2
    DEL = 3

    def __str__(self):
        return self.name

def getExprContext(ctx):
    if isinstance(ctx, ast.Load):
        return ExprContext.LOAD
    if isinstance(ctx, ast.Store):
        return ExprContext.STORE
    if isinstance(ctx, ast.Del):
        return ExprContext.DEL

class NodeModule:
    def __init__(self, body):
        self.body = body

    def __repr__(self):
        body_repr = ',\n'.join("    " + repr(stmt).replace("\n", "\n    ") for stmt in self.body)
        return f"Module(\n{body_repr})" 

class NodeImport():
    def __init__(self, module):
        modules = [m.name for m in module]
        self.modules = modules

    def __repr__(self):
        names = ', '.join(f"'{name}'" for name in self.modules)
        return f"Import(modules=[{names}])"

class NodeImportFrom():
    def __init__(self, module, names):
        names = [m.name for m in names]
        self.module = module
        self.names = names

    def __repr__(self):
        names = ', '.join(f"'{name}'" for name in self.names)
        return f"ImportFrom(module='{self.module}', names=[{names}])"

class NodeTuple():
    def __init__(self, items):
        self.items = items

    def _repr(self, indent=0):
        return f"In development tuple"

class NodeName():
    def __init__(self, name, ctx):
        self.name = name
        self.ctx = ctx

    def __repr__(self):
        return f"Name(name='{self.name}', ctx={self.ctx})"

    def _repr(self, indent=0):
        return "  " * indent + f"Name(name='{self.name}', ctx={self.ctx})"

class NodeAssign():
    def __init__(self, targets, value):
        self.setTargets(targets)

        self.value = value

    def setTargets(self, targets):
        targets_list = []
        for target in targets:
            if isinstance(target, ast.Name):
                targets_list.append(NodeName(target.id, getExprContext(target.ctx)))

            if isinstance(target, ast.Tuple):
                targets_list.append(NodeTuple(target.elts))

        self.targets = targets_list

    def __repr__(self):
        targets_repr = ',\n'.join("    " + stmt._repr(1).replace("\n", "\n    ") for stmt in self.targets)
        return f"Assign(\n   targets=[\n{targets_repr}\n   ],\n   value={self.value})"

def traverseModule(node, indent=0):
    # print("  " * indent + type(node).__name__ + " " + str(node.__dir__()))
    return NodeModule([traverse(child, indent + 1) for child in node.body])

def traverseImport(node, indent=0):
    return NodeImport(node.names)

def traverseImportFrom(node, indent=0):
    return NodeImportFrom(node.module, node.names)

def traverse(node, indent=0):
    try:
        if isinstance(node, ast.Module):
            return traverseModule(node, indent)

        if isinstance(node, ast.Import):
            return traverseImport(node, indent)

        if isinstance(node, ast.ImportFrom):
            return traverseImportFrom(node, indent)

        if isinstance(node, ast.Assign):
            return NodeAssign(node.targets, node.value)

        raise NotImplementedError(f"Node type not implemented: {type(node).__name__}")           
        
    except Exception as e:
        print(e)
        # return

    print("  " * indent + type(node).__name__)
    for child in ast.iter_child_nodes(node):
        traverse(child, indent + 1)

def main():
    args = read_arguments()

    ast_tree = parse_source(args.filename)

    print(ast.dump(ast_tree, indent=4))

    tree = traverse(ast_tree)
    print(tree)
 
if __name__ == "__main__":
    main()